import streamlit as st
from datetime import datetime

# Mock user database (for demonstration)
USER_CREDENTIALS = {"username": "AmitJha", "password": "123456"}

# You can get this API Key from - https://openweathermap.org/api
get_weather_api = 'API_KEY_OpenWeatherMap' 

# You can get this API Key from - https://gnews.io/
get_local_news_api = 'API_KEY_GNews'

import streamlit as st
import ollama
import requests
from neo4j import GraphDatabase

# Connect to Neo4j
def connect_to_db():
    uri = "bolt://localhost:7687"
    driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
    return driver

# Store user preferences in Neo4j
def store_user_preferences(driver, user_id, preferences):
    with driver.session() as session:
        session.run(
            """
            MERGE (u:User {id: $user_id})
            SET u.name = $name, u.city = $city, u.day = $day, u.start_time = $start_time, 
                u.end_time = $end_time, u.budget = $budget, u.interests = $interests, u.spoint = $spoint
            """,
            user_id=user_id,
            name=preferences.get('what_is_your_name'),
            city=preferences.get('where_do_you_want_to_travel'),
            day=preferences.get('what_day_are_you_planning_for'),
            start_time=preferences.get('what_time_do_you_want_to_start'),
            end_time=preferences.get('what_time_do_you_want_to_end_your_day'),
            budget=preferences.get('what_is_your_budget_for_the_day'),
            interests=preferences.get('what_are_your_interests'),
            spoint=preferences.get('what_is_your_starting_point')
        )

# Retrieve user preferences from Neo4j
def get_user_preferences(driver, user_id):
    with driver.session() as session:
        result = session.run(
            """
            MATCH (u:User {id: $user_id})
            RETURN u.name AS name, u.city AS city, u.day AS day, u.start_time AS start_time, 
                   u.end_time AS end_time, u.budget AS budget, u.interests AS interests, u.spoint AS spoint
            """,
            user_id=user_id
        )
        return result.single()  # returns a dictionary of the user's preferences, or None

# Fetch weather data from OpenWeatherMap
def get_weather(city, date):
    api_key = get_weather_api 
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"
    response = requests.get(url)
    data = response.json()
    weather = data.get('weather', [{}])[0].get('description', 'No weather information available')
    return weather

# Fetch local news using Gnews API
def get_local_news(city):
    api_key = get_local_news_api  # Your provided Gnews API key
    url = f"https://gnews.io/api/v4/search?q={city}&token={api_key}"
    response = requests.get(url)
    news_data = response.json()

    # Extracting the titles of the top 5 news articles
    headlines = [article['title'] for article in news_data['articles'][:5]]
    return headlines

# Refine itinerary logic with specific time slots, priorities, and budget
def refine_itinerary_logic(preferences):
    city = preferences['Where do you want to travel?']
    day = preferences['What day are you planning for?']
    start = preferences['What time do you want to start?']
    end = preferences['What time do you want to end your day?']
    budget = preferences['What is your budget for the day?']
    interest = preferences['What are your interests? (e.g., culture, food, adventure)']
    spoint = preferences['What is your starting point?']
    
    user_preferences = f"Generate a one-day itinerary in {city} for {day}, with specific time slots, starting from {start} and ending at {end}, prioritizing interests in {interest}, and keeping within a budget of {budget}. Include details such as start times, end times, and places to visit. The places suggested should begin near {spoint} so that the itinerary is optimised based on time, location, travel and budget."
    return user_preferences

# Function to interact with Ollama for user preferences and itinerary suggestion
def ask_questions(driver):
    # Define the questions to ask
    questions = [
        "What is your name?",
        "Where do you want to travel?",
        "What day are you planning for?",
        "What time do you want to start?",
        "What time do you want to end your day?",
        "What is your budget for the day?",
        "What are your interests? (e.g., culture, food, adventure)",
        "What is your starting point?"
    ]
    
    # Initialize session state variables for responses and index if not already initialized
    if 'question_index' not in st.session_state:
        # print("question_index not in st.session_state")
        st.session_state['question_index'] = 0
        st.session_state['responses'] = {}
        st.session_state['conversation'] = []  # Store the conversation history

    # If we have a user_id, check for stored preferences in Neo4j
    user_id = st.session_state.get('user_name')  # using user_name as user_id, change this if you need a unique ID
    if user_id:
        stored_preferences = get_user_preferences(driver, user_id)
        if stored_preferences:
            st.session_state['responses'] = stored_preferences
            st.session_state['question_index'] = len(questions)  # Skip questions if data exists

    # Check if we have reached the end of the questions list
    if st.session_state['question_index'] >= len(questions):
        preferences = ", ".join([f"{key}: {value}" for key, value in st.session_state['responses'].items()])

        # print("Session State :")
        # print(st.session_state['responses'])

        # Check if city and day are missing in the responses
        city = st.session_state['responses']['Where do you want to travel?']

        # print("city:", city)

        if not city:
            st.error("City is missing. Please provide a valid city.")
            return

        day = st.session_state['responses'].get('What day are you planning for?')
        
        # print("day:", day)

        if not day:
            st.error("Day is missing. Please provide a valid day.")
            return
        
        start = st.session_state['responses'].get('What time do you want to start?')
        end = st.session_state['responses'].get('What time do you want to end your day?')
        budget = st.session_state['responses'].get('What is your budget for the day?')
        interest = st.session_state['responses'].get('What are your interests? (e.g., culture, food, adventure)')

        # Generate the itinerary using Ollama
        try:
            # print("Trying now:")
            desiredModel = 'llama3.2:latest'
            weather = get_weather(city, day)
            news = get_local_news(city)
            routes = "Specify the travel distance and estimated time from the starting point to each attraction and between all subsequent stops."
            seq = "Arrange the stops in an optimal order to maximize the user’s time at each attraction and minimize travel time, considering the available time from {start} to {end}."
            mode = "Recommend the best mode of transport (walking, public transport, taxi, etc.) based on distance, time, and user budget constraints."
            bud = "Ensure transportation costs align with the user’s budget of {budget}. Specify segments where public transportation or taxis are advised based on the budget and time efficiency."
            user_preferences = f"{refine_itinerary_logic(st.session_state['responses'])} {routes} {seq} {mode} {bud}. Weather of {city} on {day} is {weather}. Tell the user about the weather also. Here is some news about {city} : {news}. Tell a short summary of this news to the user."
            
            print("user_preferences: ",user_preferences)
            
            response = ollama.chat(model=desiredModel, messages=[{'role': 'user', 'content': user_preferences}])
            
            print("response:", response)

            itinerary_response = response['message']['content']

            print("itinerary_response: ", itinerary_response)

            # Add user message and Ollama's response to the conversation history
            st.session_state['conversation'].append({"role": "user", "content": user_preferences})
            st.session_state['conversation'].append({"role": "model", "content": itinerary_response})

            # Display the conversation history
            for msg in st.session_state['conversation']:
                if msg["role"] == "user":
                    st.write(f"You: {msg['content']}")
                else:
                    st.write(f"Ollama: {msg['content']}")

            # # Display weather and news updates
            # st.write(f"\nWeather Forecast: {weather}")
            # st.write(f"\nLocal News: {', '.join(news)}")  # Show top news headlines

            # Ask for feedback on the itinerary
            st.write("\nIs this itinerary okay for you?")
            feedback = st.radio("Do you want to modify your itinerary?", ("Yes", "No"))
            
            if feedback == "Yes":
                # Ask what they would like to change
                change = st.text_area("What would you like to change? (e.g., timings, activities, budget, etc.)")
                
                if change:
                    # Store the feedback (change)
                    st.session_state['feedback'] = change
                    
                    # Update user_preferences to include the feedback
                    adjusted_preferences = user_preferences + f" Adjust the itinerary based on the following: {change}"
                    
                    # Re-run the itinerary generation with the updated preferences
                    response = ollama.chat(model=desiredModel, messages=[{'role': 'user', 'content': adjusted_preferences}])
                    updated_itinerary = response['message']['content']

                    # Show the updated itinerary
                    st.session_state['conversation'].append({"role": "user", "content": adjusted_preferences})
                    st.session_state['conversation'].append({"role": "model", "content": updated_itinerary})

                    # Display the updated itinerary
                    st.write(f"Updated Itinerary: {updated_itinerary}")
                    # Store the updated itinerary in Neo4j
                    store_user_preferences(driver, user_id, st.session_state['responses'])

            else:
                st.write("Great! Your itinerary is finalized.")

        except Exception as e:
            print("Exception has occured.")
            st.error(f"Error communicating with Ollama: {e}")

        # Reset the session state for a new session
        st.session_state['question_index'] = 0
        return

    # Ask the current question
    question = questions[st.session_state['question_index']]
    response = st.text_input(question)

    if response:
        st.session_state['responses'][question] = response
        st.session_state['question_index'] += 1

# Main flow for Streamlit app
def main():
    # Initialize Neo4j connection
    driver = connect_to_db()

    ask_questions(driver)

# Function to add interactions to the sidebar
def add_interaction(message):
    """Add interaction message to session state and display in sidebar."""
    if "interactions" not in st.session_state:
        st.session_state["interactions"] = []
    st.session_state["interactions"].append(message)

# Define login function
def login(username, password):
    """Authenticate user credentials."""
    if username == USER_CREDENTIALS["username"] and password == USER_CREDENTIALS["password"]:
        st.session_state["logged_in"] = True
        st.session_state["username"] = username
        st.success("Logged in successfully!")
        add_interaction(f"User {username} logged in.")
    else:
        st.error("Invalid username or password")

# Define logout function
def logout():
    """Clear session state for logout."""
    st.session_state["logged_in"] = False
    st.session_state.pop("username", None)
    st.info("Logged out successfully.")
    add_interaction("User logged out.")

# Start a new chat session
def start_new_chat():
    """Initialize a new chat session with a unique timestamp key."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state["chat_sessions"][timestamp] = []  # Start an empty conversation history
    st.session_state["selected_chat"] = timestamp  # Set the new chat as the active session

# Add message to the current chat session
def add_message(role, content):
    """Add a message to the current chat session history."""
    if st.session_state["selected_chat"]:
        st.session_state["chat_sessions"][st.session_state["selected_chat"]].append(
            {"role": role, "content": content}
        )

# Initialize session state variables if not set
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "chat_sessions" not in st.session_state:
    st.session_state["chat_sessions"] = {}  # Store chat sessions by timestamp
if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = None  # Selected chat session to view


# Sidebar: Chat session selection and interaction history
st.sidebar.title("Interaction History")
if st.session_state["logged_in"]:
    # Button to start a new chat session
    if st.sidebar.button("Start New Chat"):
        start_new_chat()
    
    # Display each chat session in the sidebar
    for timestamp in st.session_state["chat_sessions"].keys():
        if st.sidebar.button(timestamp):
            st.session_state["selected_chat"] = timestamp  # Set selected chat

# Main application logic
if not st.session_state["logged_in"]:
    st.title("Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        login_button = st.form_submit_button("Login")

        if login_button:
            login(username, password)
else:
    st.title(f"Welcome, {st.session_state['username']}!")

    # Logout button
    if st.button("Logout"):
        logout()

    # Main content for logged-in users
    main()

    # Display selected chat history in main area
    # Main content area: Display selected chat history
    if st.session_state["selected_chat"]:
        selected_timestamp = st.session_state["selected_chat"]
        st.subheader(f"Chat History for {selected_timestamp}")
        
        # Show each message in the selected chat session
        if selected_timestamp in st.session_state["chat_sessions"]:
            for message in st.session_state["chat_sessions"][selected_timestamp]:
                if message["role"] == "user":
                    st.write(f"You: {message['content']}")
                else:
                    st.write(f"Ollama: {message['content']}")
        else:
            st.write("No messages found in this chat.")
    


    # # Sample interaction input for demonstration
    # user_message = st.text_input("Enter your message:")
    # if user_message:
    #     add_interaction(f"User: {user_message}")
    #     st.write(f"You: {user_message}")
        
    #     # Simulate a system response (replace this with actual logic)
    #     response_message = f"System: This is a response to '{user_message}'"
    #     add_interaction(response_message)
    #     st.write(response_message)
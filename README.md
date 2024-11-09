# AttentionsAI

# Project One-Day Tour Planning Application

## NAME - Amit Kumar Jha
## ROLL NO. - 210110019
## MAIL ID - amitkjha2403@gmail.com

## Overview

This Streamlit application provides a personalized itinerary generation tool for users based on their preferences. The application connects with OpenWeatherMap to fetch weather data, GNews to retrieve local news, and Neo4j to store user preferences and generate customized itineraries. The app also integrates with Ollama for AI-based conversation and itinerary generation, ensuring that the itinerary is optimized based on user-defined parameters such as budget, time, interests, and starting point.

Key features:
- User login system.
- Step-by-step preference collection for itinerary planning.
- Integration with OpenWeatherMap for weather data and GNews for local news.
- Use of Neo4j database to store and retrieve user preferences.
- AI-powered itinerary generation using Ollama.
- MAP : I tried to implement this feature but was not able to find any good free APIs for this task of mapping the routes of the itinerary

## Requirements

To run this project, you will need the following:
- Python 3.x
- Streamlit
- Neo4j
- Requests
- Ollama
- OpenWeatherMap API Key (for weather data)
- GNews API Key (for local news)

### Installation

1. Install the necessary Python packages:
   ```bash
   pip install streamlit neo4j requests ollama
2. Obtain API keys:
   
   OpenWeatherMap -
   ```bash
   https://openweathermap.org/api
   ```
   GNews - 
   ```bash
   https://gnews.io/
   ```

3. Set up Neo4j:

   Install and configure a local Neo4j database.

   Replace the uri and auth details in the connect_to_db() function with your database URI and credentials.

### Neo4j Setup

To store and retrieve user preferences in the Neo4j database, the app uses Cypher queries. Make sure that the database is running and accessible. The following is a basic connection setup for the Neo4j database:

```python
uri = "bolt://localhost:7687"
driver = GraphDatabase.driver(uri, auth=("neo4j", "password"))
```
Make sure to replace the neo4j password with your own.

### Running the App

To run the application:

1. Save the Python script.
2. Launch the Streamlit app by running:

   ```bash
   streamlit run final.py
3. The app will open in your default web browser.

## Features

### User Authentication

The app includes a simple login system with predefined user credentials:

- **Username**: AmitJha
- **Password**: 123456

Once logged in, users can plan an itinerary, which will be saved in the Neo4j database for future use.

### Step-by-Step Itinerary Planning

The app asks the user a series of questions to gather the following preferences:
1. Name
2. Destination city
3. Day of the trip
4. Start and end times for the day
5. Budget for the day
6. Interests (culture, food, adventure, etc.)
7. Starting point for the itinerary

The user's answers are saved in the Neo4j database, and the app uses them to generate a customized itinerary.

### AI-Powered Itinerary Generation

Once the user answers all the questions, the app sends the collected data to Ollama, an AI service that generates a personalized one-day itinerary. The AI considers:
- User interests (e.g., culture, adventure).
- Available time from start to end of the day.
- Budget constraints.
- The weather in the chosen city.
- Local news headlines for added context.

The generated itinerary is then presented to the user along with the weather forecast and local news for the selected city.

### User Feedback and Modifications

After the itinerary is generated, users can provide feedback and request modifications. The app allows users to adjust aspects of the itinerary (e.g., timing, activities, budget) and re-runs the itinerary generation based on their feedback.

### Interaction History

The app maintains a history of interactions and conversation sessions in the sidebar, allowing users to view and revisit previous chat sessions.

### Session Management

- **Login/Logout**: Users can log in and log out of the application.
- **Chat Sessions**: Each conversation with the AI is stored with a timestamp. Users can view past chat sessions.
- **User Preferences**: User preferences are stored in Neo4j and can be retrieved to avoid repeating the entire process.

## Code Structure

- **`final.py`**: The main script that runs the Streamlit app. It includes all the functions for user interaction, itinerary generation, and integration with APIs and the Neo4j database.
- **`neo4j`**: Contains functions to connect to the Neo4j database and store/retrieve user preferences.
- **`weather`**: Functions for fetching weather data from OpenWeatherMap.
- **`news`**: Functions for fetching local news from the GNews API.
- **`ollama`**: Functions for interacting with the Ollama API to generate personalized itineraries.

## Example Workflow

1. **Login**: The user logs in with their credentials.
2. **Questionnaire**: The app asks the user for their travel preferences (name, city, day, etc.).
3. **Itinerary Generation**: Based on the user's input, the app fetches weather and news data, then uses Ollama to generate a personalized itinerary.
4. **User Feedback**: The user can provide feedback and modify the itinerary if needed.
5. **Finalized Itinerary**: Once the user is satisfied, the itinerary is finalized, and the session is saved.

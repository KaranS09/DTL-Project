from flask import Flask, render_template, request, redirect, url_for
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from gtts import gTTS
import io
import base64
import json

import os
from dotenv import load_dotenv

# Custom modules
import PostHandler

load_dotenv()


app = Flask(__name__)

# Testing Parameters
REAL_DATA = False            # ? False: use sample data / True: use real data
TEST_CONNECTION = False     # ? False: don't test connection / True: test connection


# Define db and collection as placeholders
db = None
collection = None

if REAL_DATA:
    # MongoDB connection
    mongodb_uri = os.getenv("MONGODB_URI")
    client = MongoClient(mongodb_uri, server_api=ServerApi('1'))

    # Select the database and collection
    db = client['DTL_db']
    collection = db['posts']

    # Send a ping to confirm a successful connection
    if TEST_CONNECTION:
        try:
            client.admin.command('ping')
            print("✅ Pinged your deployment. You successfully connected to MongoDB!")
        except Exception as e:
            print(e)

        # Add a sample document in the collection (don't add if already exists)
        name = 'John Doe'
        if collection.count_documents({'name': name}) == 0:
            collection.insert_one({'name': name})
            print("✅ Added a sample document in the collection.")

        # Retrieve the sample document added
        result = collection.find_one({'name': name})
        print(result)
        print("✅ Retrieved the sample document.")

        # Delete the sample document added
        collection.delete_one({'name': name})
        print("✅ Deleted the sample document.")


@app.route('/')
def index():

    posts_dict = PostHandler.getPostsData(collection, REAL_DATA)

    return render_template('dashboard.html', posts_dict=posts_dict)


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/events')
def events():
    return render_template('events.html')


@app.route('/events/all_in_one/<category>')
def all_in_one(category):

    # category = upcoming/ongoing/completed

    posts_dict = PostHandler.getPostsData(collection, REAL_DATA)
    return render_template('all_in_one.html', posts_dict=posts_dict, category=category)


@app.route('/eventDetail')
def eventDetail():

    # Get the event details from the URL

    title = request.args.get('title')
    date = request.args.get('date')
    des = request.args.get('des')
    image = request.args.get('image')
    host = request.args.get('host')

    return render_template('eventDetails.html', title=title, date=date, des=des, image=image, host=host)


@app.route('/clubs')
def clubs_page():
    return render_template('clubs.html')


@app.route('/clubs/all_in_one_clubs/<category>')
def all_in_one_clubs(category):

    posts_dict = PostHandler.getPostsDataClubs(collection, REAL_DATA)
    return render_template('all_in_one_clubs.html', posts_dict=posts_dict, category=category)


@app.route('/clubDetails')
def clubDetails():

    # Get the event details from the URL

    name = request.args.get('name')
    posts_dict = PostHandler.getPostsDataClubs(collection, REAL_DATA)
    return render_template('clubDetails.html', name=name, posts_dict=posts_dict)


# Chatbot functions
def getSpeech(result_text):

    language = 'en'
    speech = gTTS(text=result_text, lang=language, slow=False)

    # On local machine
    # speech.save("speech.mp3")
    # os.system("start speech.mp3")

    # Save the speech to memory as bytes
    speech_file = io.BytesIO()
    speech.write_to_fp(speech_file)
    speech_bytes = speech_file.getvalue()
    speech_base64 = base64.b64encode(speech_bytes).decode('utf-8')

    return speech_base64


@app.route('/find_location/<location>')
def find_location(location):

    # Load data from JSON file
    with open('static/json/locations.json') as f:
        data = json.load(f)

    # Check if location exists in the JSON file
    location_data = None
    if location in data:
        location_data = data[location]
    else:
        location_data = data['default']

    return render_template('find_location.html', location_data=location_data)


def getChatbotResponse(user_input):

    # Default values
    response_text = "Sorry, I don't understand. Please try again."
    redirect_link = None

    if user_input == "See upcoming events":
        response_text = "You chose option 1: See upcoming events."
        redirect_link = url_for('all_in_one', category='upcoming')
        redirect_text = "View upcoming events"
    elif user_input == "See ongoing events":
        response_text = "You chose option 2: See ongoing events."
        redirect_link = url_for('all_in_one', category='ongoing')
        redirect_text = "View ongoing events"
    elif user_input == "See completed events":
        response_text = "You chose option 3: See completed events."
        redirect_link = url_for('all_in_one', category='completed')
        redirect_text = "View completed events"
    elif user_input == "Visit the events page":
        response_text = "You chose option 4: Visit the events page."
        redirect_link = url_for('events')
        redirect_text = "Visit the events page"
    elif user_input == "Visit the official RVCE website":
        response_text = "You chose option 5: Visit the official RVCE website."
        redirect_link = "https://www.rvce.edu.in/"
        redirect_text = "Visit the official RVCE website"
    elif user_input == "Get Placement Statistics":
        response_text = "You chose option 6: Get Placement Statistics."
        redirect_link = "https://rvce.edu.in/placement-statistics"
        redirect_text = "Get Placement Statistics"

    elif user_input == "Find the admin block":
        response_text = "You chose option 7: Find the admin block."
        redirect_link = url_for('find_location', location='admin')
        redirect_text = "Find the admin block"
    elif user_input == "Find canteen":
        response_text = "You chose option 8: Find canteen."
        redirect_link = url_for('find_location', location='canteen')
        redirect_text = "Find the canteen"
    elif user_input == "Enquire about hostel facilities":
        response_text = "You chose option 9: Enquire about hostel facilities."
        redirect_link = url_for('find_location', location='hostel')
        redirect_text = "Enquire about hostel facilities"
    elif user_input == "Find the library":
        response_text = "You chose option 10: Find the library."
        redirect_link = url_for('find_location', location='library')
        redirect_text = "Find the library"
    elif user_input == "Enquire about the admission process":
        response_text = "You chose option 11: Enquire about the admission process."
        redirect_link = url_for('find_location', location='admission')
        redirect_text = "Enquire about the admission process"
    elif user_input == "Find the auditorium":
        response_text = "You chose option 12: Find the auditorium."
        redirect_link = url_for('find_location', location='auditorium')
        redirect_text = "Find the auditorium"

    audio_text = f"""{response_text} Opening the link for you.
    If not redirected automatically, please click the link below. 
    If you would like to choose another option, please select it from the dropdown menu given above."""

    response_audio = getSpeech(audio_text)

    return response_text, redirect_link, redirect_text, response_audio


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():

    # Question : Options dictionary
    questionnaire = {"What would you like to do?": ["See upcoming events",
                                                    "See ongoing events",
                                                    "See completed events",
                                                    "Visit the events page",
                                                    "Visit the official RVCE website",
                                                    "Get Placement Statistics",

                                                    "Find the admin block",
                                                    "Find the canteen",
                                                    "Enquire about hostel facilities",
                                                    "Find the library",
                                                    "Enquire about the admission process",
                                                    "Find the auditorium",
                                                    ]}

    hello = "Hello, I am RVCE's chatbot, at your service. How can I help you today?"
    speech_base64 = getSpeech(hello)

    if request.method == 'POST':
        user_input = request.form['user_input']
        response_text, redirect_link, redirect_text, response_audio = getChatbotResponse(
            user_input)

        return render_template('chatbot.html', questionnaire=questionnaire,
                               user_input=user_input, response_text=response_text,
                               redirect_link=redirect_link, redirect_text=redirect_text,
                               response_audio=response_audio)

    return render_template('chatbot.html', questionnaire=questionnaire, speech_base64=speech_base64)


if __name__ == '__main__':
    app.run(debug=True)

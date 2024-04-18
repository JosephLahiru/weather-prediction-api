from flask import Flask, request, jsonify, render_template
from datetime import datetime
from waitress import serve
import mysql.connector
from dotenv import load_dotenv
import os
import pytz

load_dotenv()

start_time = datetime.now().isoformat()

def db_init():
    cnx = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

    return cnx

cnx = db_init()

app = Flask(__name__)

last_known_coordinates = {}

def console(message):
    ist_timezone = pytz.timezone('Asia/Kolkata')
    time = datetime.now(ist_timezone).strftime('%d/%m/%Y %H:%M:%S')
    print(f"{time} [LOG]: Processing {message}")


@app.route("/")
def status():
    console("Status")
    return jsonify({"project":"weather-prediction-api", "status": "online", "start_time": start_time})


@app.route('/push_weather_data', methods=['POST'])
def push_weather_data():
    console("Push Weather Data")
    try:
        global cnx
        weather_data = request.get_json()

        console(weather_data)
        cursor = cnx.cursor()

        insert_query = "INSERT INTO weather_data (humidity, temperature, luminosity, raining) VALUES (%s, %s, %s, %s)"
        values = (weather_data['humidity'], weather_data['temperature'], weather_data['luminosity'], weather_data['raining'])
        cursor.execute(insert_query, values)
        cnx.commit()

        cursor.close()
        return jsonify({"message": "Weather data added successfully!"}), 200
    
    except Exception as e:
        cnx = db_init()
        return jsonify({"error": e}), 500


if __name__ == '__main__':
    console("Starting Server")
    serve(app, host='0.0.0.0', port=5009, threads=10)
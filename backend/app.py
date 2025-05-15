from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import pymysql
import time
import traceback
import openai

# Load environment variables from .env file
load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app, origins=["https://staging4.bitcoiners.africa"])

# Environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
ASSISTANT_API_KEY = os.getenv('ASSISTANT_API_KEY')  # Optional if you use assistant ID

# OpenAI setup
openai.api_key = OPENAI_API_KEY

# Database config
DB_HOST = "127.0.0.1"
DB_USER = "u450724067_iX9ab"
DB_PASSWORD = "IxGLaj3MJp"
DB_NAME = "u450724067_oZCJ5"
DB_PORT = 3306

# Establish DB connection
def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

# Chat route
@app.route("/api/chat", methods=["POST"])
def chat():
    start_time = time.time()
    try:
        data = request.json
        user_input = data.get("message", "")
        user_id = data.get("user_id", "anonymous")
        session_id = data.get("session_id", "default_session")

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Extract AI response
        ai_response = response['choices'][0]['message']['content'].strip()
        ai_response_links = ""  # Optional: add link extraction or enrichment here
        response_time = time.time() - start_time

        # Log to DB
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO wp_ai_chatbot 
                (user_id, session_id, user_input, ai_response, ai_response_links, ip_address, response_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            ip_address = request.remote_addr or ""
            cursor.execute(sql, (
                user_id,
                session_id,
                user_input,
                ai_response,
                ai_response_links,
                ip_address,
                response_time
            ))
            connection.commit()

        return jsonify({
            "response": ai_response,
            "links": ai_response_links
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error"}), 500

# Run app
if __name__ == "__main__":
    app.run(debug=True)

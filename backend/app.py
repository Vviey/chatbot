# backend/app.py

import time
import uuid
import openai
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

# Flask setup
app = Flask(__name__)
CORS(app)

# OpenAI setup
openai.api_key = os.getenv("OPENAI_API_KEY")

# MySQL DB setup
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message", "").strip()
    session_id = data.get("session_id", str(uuid.uuid4()))
    user_id = data.get("user_id", "anonymous")
    ip_address = request.remote_addr or "unknown"

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    start_time = time.time()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Bitcoin assistant for Africans."},
                {"role": "user", "content": user_input}
            ]
        )
        ai_response = response["choices"][0]["message"]["content"]
        response_time = round(time.time() - start_time, 2)
    except Exception as e:
        return jsonify({"error": f"OpenAI Error: {str(e)}"}), 500

    # Save chat to WordPress DB
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        sql = """
            INSERT INTO wp_ai_chatbot (user_id, session_id, user_input, ai_response, ip_address, response_time)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            user_id,
            session_id,
            user_input,
            ai_response,
            ip_address,
            response_time
        ))
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as db_err:
        return jsonify({"error": f"MySQL Error: {str(db_err)}"}), 500

    return jsonify({
        "session_id": session_id,
        "user_id": user_id,
        "response": ai_response,
        "response_time": response_time
    })

if __name__ == "__main__":
    app.run(debug=True)

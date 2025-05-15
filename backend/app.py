# backend/app.py

import time
import uuid
from flask import Flask, request, jsonify
import openai
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# OpenAI Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# DB Config
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
    "port": int(os.getenv("DB_PORT", 3306))
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    session_id = data.get('session_id', str(uuid.uuid4()))
    user_id = data.get('user_id', 'anonymous')
    ip_address = request.remote_addr or 'unknown'

    if not user_input:
        return jsonify({"error": "No message provided"}), 400

    start_time = time.time()

    try:
        # AI response
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful Bitcoin assistant for Africans."},
                {"role": "user", "content": user_input}
            ]
        )
        ai_response = response['choices'][0]['message']['content']
    except Exception as e:
        return jsonify({"error": f"AI error: {str(e)}"}), 500

    response_time = round(time.time() - start_time, 2)

    # Save to MySQL
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
    except mysql.connector.Error as err:
        return jsonify({"error": f"MySQL error: {str(err)}"}), 500

    return jsonify({
        "session_id": session_id,
        "user_id": user_id,
        "response": ai_response,
        "response_time": response_time
    })

if __name__ == '__main__':
    app.run(debug=True)

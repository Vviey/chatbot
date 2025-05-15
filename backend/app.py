import os
import time
import pymysql
import openai
from flask import Flask, request, jsonify
from flask_cors import CORS

# Set API Key from environment (Render)
openai.api_key = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_API_KEY")

# Database credentials (set in Render environment variables)
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

# Flask setup
app = Flask(__name__)
CORS(app, origins=["https://staging4.bitcoiners.africa"])

# Simple memory-based session tracking (replace with Redis later if needed)
session_threads = {}

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/", methods=["GET"])
def home():
    return "Am alive!!"

@app.route("/api/chat", methods=["POST"])
def chat():
    start_time = time.time()

    try:
        data = request.get_json()
        user_message = data.get("message")
        user_id = data.get("user_id", "anonymous")  # fallback
        session_id = data.get("session_id", "default_session")
        ip_address = request.remote_addr or ""

        if not user_message:
            return jsonify({"error": "Missing user message"}), 400

        # Get or create thread for user
        thread_id = session_threads.get(user_id)
        if not thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
            session_threads[user_id] = thread_id

        # Add user message
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Start run
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=ASSISTANT_ID
        )

        # Wait for response
        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                return jsonify({"error": "Assistant run failed"}), 500

        # Fetch reply
        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        bot_reply = next((msg.content[0].text.value for msg in messages.data if msg.role == "assistant"), None)

        response_time = time.time() - start_time

        # Save to DB
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO wp_ai_chatbot (user_id, session_id, user_input, ai_response, ai_response_links, ip_address, response_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                user_id,
                session_id,
                user_message,
                bot_reply,
                "",  # ai_response_links (optional)
                ip_address,
                response_time
            ))
            connection.commit()

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

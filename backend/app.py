from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os

# Read API key from Render environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Enable CORS for staging & production
CORS(app, origins=[
    "https://bitcoiners.africa",
    "https://staging4.bitcoiners.africa"
])

# Session management
session_threads = {}

@app.route("/", methods=["GET"])
def home():
    return "Chatbot backend is live."

@app.route("/api/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message")
        user_id = data.get("user_id")

        if not user_message or not user_id:
            return jsonify({"error": "Missing message or user_id"}), 400

        thread_id = session_threads.get(user_id)
        if not thread_id:
            thread = openai.beta.threads.create()
            thread_id = thread.id
            session_threads[user_id] = thread_id

        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=os.getenv("OPENAI_ASSISTANT_ID")
        )

        while True:
            status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run.id)
            if status.status == "completed":
                break
            elif status.status == "failed":
                return jsonify({"error": "Run failed"}), 500

        messages = openai.beta.threads.messages.list(thread_id=thread_id)
        bot_reply = next((msg.content[0].text.value for msg in messages.data if msg.role == "assistant"), None)

        return jsonify({"reply": bot_reply})

    except Exception as e:
        print("Chatbot error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)

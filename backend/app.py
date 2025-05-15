import uuid
import time
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Setup CORS for frontend domain and localhost (dev)
CORS(app,
     resources={r"/*": {"origins": ["https://staging4.bitcoiners.africa"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Origin"],
     methods=["GET", "POST", "OPTIONS"])

# In-memory session storage: user_id -> thread_id
session_threads = {}

# Setup logger
logging.basicConfig(level=logging.INFO)

@app.route('/', methods=['GET'])
def health_check():
    return "Bitcoin Sidekick API - Operational"

@app.route('/api/chat', methods=['OPTIONS'])
def options():
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Origin')
    response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
    response.headers.add('Access-Control-Max-Age', '3600')
    response.headers.add('Vary', 'Origin')
    return response

@app.route('/api/chat', methods=['POST'])
def chat_handler():
    try:
        data = request.get_json(force=True)
        user_message = data.get('message')
        user_id = data.get('user_id')

        if not user_message or not user_id:
            return jsonify({"error": "Message and user_id required"}), 400

        # Get or create thread for the user
        thread_id = session_threads.get(user_id)
        if not thread_id:
            logging.info(f"Creating new thread for user_id: {user_id}")
            thread = openai.beta.threads.create()
            thread_id = thread.id
            session_threads[user_id] = thread_id

        # Add user message to the thread
        openai.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_message
        )

        # Run the assistant on this thread
        run = openai.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id="asst_wXH9h4xeSZ3nmPZgjWqvRVfL"
        )

        # Poll for run completion with timeout
        timeout_seconds = 20
        poll_interval = 1
        waited = 0
        while waited < timeout_seconds:
            status = openai.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if status.status == "completed":
                break
            if status.status in ["failed", "cancelled"]:
                logging.error(f"Run failed/cancelled for user {user_id}, thread {thread_id}")
                return jsonify({"error": "Processing failed"}), 500
            time.sleep(poll_interval)
            waited += poll_interval
        else:
            # Timeout exceeded
            logging.error(f"Run timeout for user {user_id}, thread {thread_id}")
            return jsonify({"error": "Processing timeout"}), 504

        # Retrieve all messages and find the last assistant reply
        messages = openai.beta.threads.messages.list(thread_id=thread_id)

        bot_reply = None
        for msg in reversed(messages.data):
            if msg.role == "assistant":
                # Defensive: check message structure
                try:
                    bot_reply = msg.content[0].text.value
                    break
                except Exception as e:
                    logging.warning(f"Unexpected message content format: {e}")

        if not bot_reply:
            bot_reply = "Sorry, I could not generate a response."

        # Return response with CORS headers
        response = jsonify({"reply": bot_reply})
        response.headers.add("Access-Control-Allow-Origin", request.headers.get('Origin', '*'))
        response.headers.add("Vary", "Origin")
        return response

    except Exception as e:
        logging.exception("Error handling chat request")
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

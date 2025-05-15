import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv
import traceback

# Load environment variables from .env
load_dotenv()

# Configure the OpenAI client - using newer client format
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# Configure CORS to allow all origins for simplicity
CORS(app,
     resources={r"/*": {"origins": "*"}},  # Allow all origins for testing
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Origin"],
     methods=["GET", "POST", "OPTIONS"])

# In-memory session storage for assistant conversations
session_threads = {}

@app.route('/', methods=['GET'])
def health_check():
    return "Bitcoin Sidekick API - Operational"

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_handler():
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Origin')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

    try:
        # Get request data
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        user_message = data.get('message')
        user_id = data.get('user_id', 'default_user')
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Log the incoming request
        print(f"Received message from {user_id}: {user_message}")

        # Simple completion approach - more reliable than assistants for testing
        try:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Use a reliable model
                messages=[
                    {"role": "system", "content": "You are the African Bitcoin Assistant, helping people learn about Bitcoin in Africa. Provide concise, helpful responses about Bitcoin topics, especially as they relate to African users and communities."},
                    {"role": "user", "content": user_message}
                ]
            )
            bot_reply = completion.choices[0].message.content
        except Exception as api_error:
            print(f"OpenAI API error: {str(api_error)}")
            print(traceback.format_exc())
            return jsonify({"error": f"OpenAI API error: {str(api_error)}"}), 500

        # Return reply
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"Server error: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

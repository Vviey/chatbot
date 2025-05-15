import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

app = Flask(__name__)

# Configure CORS to allow requests from your frontend domain
CORS(app,
     resources={r"/*": {"origins": ["https://staging4.bitcoiners.africa"]}},
     supports_credentials=True,
     allow_headers=["Content-Type", "Authorization", "Origin"],
     methods=["GET", "POST", "OPTIONS"])

@app.route('/', methods=['GET'])
def health_check():
    return "Bitcoin Sidekick API - Operational"

@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_handler():
    if request.method == 'OPTIONS':
        # Handle CORS preflight
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'https://staging4.bitcoiners.africa')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, Origin')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Max-Age', '3600')
        response.headers.add('Vary', 'Origin')
        return response

    try:
        data = request.get_json()
        user_message = data.get('message')
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # Call OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": user_message}
            ]
        )

        bot_reply = response.choices[0].message.content
        # Return reply with CORS header
        resp = jsonify({"reply": bot_reply})
        resp.headers.add("Access-Control-Allow-Origin", "https://staging4.bitcoiners.africa")
        resp.headers.add("Vary", "Origin")
        return resp

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

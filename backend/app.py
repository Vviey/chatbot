from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

app = Flask(__name__)
CORS(app, origins=["https://staging4.bitcoiners.africa/ "])  # Use * for now to test with Postman or localhost

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

print(">>> Loaded API Key:", bool(DEEPSEEK_API_KEY))  # Debugging

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message')

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        if not DEEPSEEK_API_KEY:
            return jsonify({"error": "Missing DeepSeek API key"}), 500

        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": user_message}]
        }

        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raises 4xx/5xx as exceptions

        bot_reply = response.json()['choices'][0]['message']['content']
        return jsonify({"reply": bot_reply})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print(">>> Flask app starting...")
    app.run(debug=True, port=5000)


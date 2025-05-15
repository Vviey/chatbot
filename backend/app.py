from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import time
import traceback

app = Flask(__name__)
CORS(app, origins=["https://staging4.bitcoiners.africa"])  # allow your frontend origin

# DB credentials from env or hardcode for now
DB_HOST = "127.0.0.1"
DB_USER = "u450724067_iX9ab"
DB_PASSWORD = "IxGLaj3MJp"
DB_NAME = "u450724067_oZCJ5"
DB_PORT = 3306

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/api/chat", methods=["POST"])
def chat():
    start_time = time.time()
    try:
        data = request.json
        user_input = data.get("message", "")
        user_id = data.get("user_id", "anonymous")  # fallback if none
        session_id = data.get("session_id", "default_session")

        # Here you call your AI/chat logic, example dummy reply
        ai_response = "This is a dummy response to: " + user_input
        ai_response_links = ""  # could parse or generate links if you want

        response_time = time.time() - start_time

        # Save chat interaction to DB
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO wp_ai_chatbot (user_id, session_id, user_input, ai_response, ai_response_links, ip_address, response_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            ip_address = request.remote_addr or ""
            cursor.execute(sql, (user_id, session_id, user_input, ai_response, ai_response_links, ip_address, response_time))
            connection.commit()

        return jsonify({
            "response": ai_response,
            "links": ai_response_links
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal Server Error"}), 500


if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
import pymysql
import os


DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_PORT = int(os.getenv("DB_PORT", 3306))

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        port=DB_PORT,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )


@app.route('/api/chat', methods=['POST'])
def insert_chat():
    try:
        data = request.get_json()
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO wp_ai_chatbot (
                    user_id, session_id, user_input, ai_response, ip_address
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (
                str(data.get("user_id", "0")),
                data.get("session_id", "unknown"),
                data.get("user_input", ""),
                data.get("ai_response", ""),
                data.get("ip_address", "")
            ))
        conn.commit()
        return jsonify({"status": "success", "message": "Data inserted"}), 200
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

import os
import pymysql
from flask import Flask, jsonify

app = Flask(__name__)

# Load DB config from environment variables (already set in Render)
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

@app.route('/test-db', methods=['GET'])
def test_db_insert():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO wp_ai_chatbot (user_id, session_id, user_input, ai_response)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, (
                'fake-user-id-123',
                'fake-session-id-abc',
                'Test user input',
                'Test AI response'
            ))
        conn.commit()
        conn.close()
        return jsonify({"status": "success", "message": "Test data inserted into DB"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

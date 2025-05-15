from flask import Flask
import mysql.connector
from datetime import datetime
import uuid

app = Flask(__name__)

# Your DB credentials
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'u450724067_iX9ab',
    'password': 'IxGLaj3MJp',
    'database': 'u450724067_oZCJ5',
    'port': 3306
}

@app.route('/test-db')
def test_db_insert():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        cursor = connection.cursor()

        # Sample/fake test data
        user_id = "test_user_123"
        session_id = str(uuid.uuid4())
        user_input = "What is Bitcoin?"
        ai_response = "Bitcoin is a decentralized digital currency."
        response_time = 0.95
        ip_address = "127.0.0.1"

        insert_query = """
        INSERT INTO wp_ai_chatbot 
        (user_id, session_id, user_input, ai_response, response_time, ip_address) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (user_id, session_id, user_input, ai_response, response_time, ip_address))
        connection.commit()

        cursor.close()
        connection.close()

        return f"✅ Test insert successful for user_id: {user_id}"
    except Exception as e:
        return f"❌ DB connection or insert failed: {e}"

if __name__ == '__main__':
    app.run(debug=True)

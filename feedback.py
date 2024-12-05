import psycopg2

async def feedbackSave(SessionId, MessageId, Answer, Question, Textual_Feedback, Numerical_Feedback, Reason):
    try:
        print(SessionId,MessageId, Answer, Question, Textual_Feedback, Numerical_Feedback, Reason)
        db_config = {
            "host": "kms-postgres.postgres.database.azure.com",
            "dbname": "feedback",
            "user": "kmsadmin",
            "password": "Celebal@123456",
            "port": 5432,  # Default PostgreSQL port
            "sslmode": "require",  # Enforce SSL
        }

        create_table_query = """
        CREATE TABLE IF NOT EXISTS KMSfeedbackNew (
            id SERIAL PRIMARY KEY,
            SessionId TEXT NOT NULL,
            MessageId TEXT NOT NULL,
            Answer TEXT NOT NULL,
            Question TEXT NOT NULL,
            Textual_Feedback TEXT NOT NULL,
            Numerical_Feedback INT NOT NULL,
            Reason TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """

        try:
            # Connect to PostgreSQL
            with psycopg2.connect(**db_config) as conn:
                with conn.cursor() as cur:
                    # Create feedback table
                    cur.execute(create_table_query)
                    print("Feedback table created successfully.")
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
            
        feedback_data = {
            "SessionId": SessionId,
            "MessageId": MessageId,
            "Answer": Answer,
            "Question": Question,
            "Textual_Feedback":Textual_Feedback,
            "Numerical_Feedback":Numerical_Feedback,
            "Reason": Reason
        }

        # SQL to insert feedback
        insert_query = """
        INSERT INTO KMSfeedbackNew (SessionId, MessageId, Answer, Question, Textual_Feedback, Numerical_Feedback, Reason)
        VALUES (%s, %s, %s, %s, %s, %s, %s);
        """

        try:
            # Connect to PostgreSQL
            with psycopg2.connect(**db_config) as conn:
                with conn.cursor() as cur:
                    # Insert feedback data
                    cur.execute(insert_query, (feedback_data["SessionId"], feedback_data["MessageId"], feedback_data["Answer"], feedback_data["Question"], feedback_data["Textual_Feedback"], feedback_data["Numerical_Feedback"], feedback_data["Reason"]))
                    conn.commit()  # Commit transaction
                    print("Feedback inserted successfully.")
                    return "Feedback inserted successfully."
        except psycopg2.Error as e:
            print(f"An error occurred: {e}")
        return True
    except Exception as e:
        print(e)


   
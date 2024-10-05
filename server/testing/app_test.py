from datetime import datetime
from app import app
from models import db, Message


class TestApp:
    '''Flask application tests in app.py'''

    # Clean up any existing messages before running tests
    with app.app_context():
        # Delete any pre-existing messages with the specified criteria
        messages_to_delete = Message.query.filter(
            Message.body == "Hello 👋",
            Message.username == "Liza"
        ).all()

        for message in messages_to_delete:
            db.session.delete(message)

        db.session.commit()

    def test_has_correct_columns(self):
        '''Test that a Message has the correct columns.'''
        with app.app_context():
            # Create a test message
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()

            # Check if the fields have the correct values and types
            assert hello_from_liza.body == "Hello 👋"
            assert hello_from_liza.username == "Liza"
            assert isinstance(hello_from_liza.created_at, datetime)

            # Clean up the test message
            db.session.delete(hello_from_liza)
            db.session.commit()

    def test_returns_list_of_json_objects_for_all_messages_in_database(self):
        '''Returns a list of JSON objects for all messages in the database.'''
        with app.app_context():
            response = app.test_client().get('/messages')
            records = Message.query.all()

            # Ensure each message returned from the API matches a DB record
            for message in response.json:
                assert message['id'] in [record.id for record in records]
                assert message['body'] in [record.body for record in records]

    def test_creates_new_message_in_the_database(self):
        '''Creates a new message in the database.'''
        with app.app_context():
            # Send POST request to create a new message
            app.test_client().post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza",
                }
            )

            # Verify that the message was created in the database
            created_message = Message.query.filter_by(body="Hello 👋").first()
            assert created_message

            # Clean up the created message
            db.session.delete(created_message)
            db.session.commit()

    def test_returns_data_for_newly_created_message_as_json(self):
        '''Returns data for the newly created message as JSON.'''
        with app.app_context():
            # Send POST request to create a new message
            response = app.test_client().post(
                '/messages',
                json={
                    "body": "Hello 👋",
                    "username": "Liza",
                }
            )

            # Verify that the response contains the correct JSON data
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Hello 👋"
            assert response.json["username"] == "Liza"

            # Clean up the created message
            created_message = Message.query.filter_by(body="Hello 👋").first()
            assert created_message

            db.session.delete(created_message)
            db.session.commit()

    def test_updates_body_of_message_in_database(self):
        '''Updates the body of a message in the database.'''
        with app.app_context():
            # Get the first message and its current body
            message_to_update = Message.query.first()
            original_body = message_to_update.body

            # Send PATCH request to update the message's body
            app.test_client().patch(
                f'/messages/{message_to_update.id}',
                json={"body": "Goodbye 👋"}
            )

            # Verify that the message's body was updated
            updated_message = Message.query.filter_by(body="Goodbye 👋").first()
            assert updated_message

            # Revert the body back to the original value
            updated_message.body = original_body
            db.session.commit()

    def test_returns_data_for_updated_message_as_json(self):
        '''Returns data for the updated message as JSON.'''
        with app.app_context():
            # Get the first message and its current body
            message_to_update = Message.query.first()
            original_body = message_to_update.body

            # Send PATCH request to update the message's body
            response = app.test_client().patch(
                f'/messages/{message_to_update.id}',
                json={"body": "Goodbye 👋"}
            )

            # Verify that the response contains the updated JSON data
            assert response.content_type == 'application/json'
            assert response.json["body"] == "Goodbye 👋"

            # Revert the body back to the original value
            updated_message = Message.query.filter_by(body="Goodbye 👋").first()
            updated_message.body = original_body
            db.session.commit()

    def test_deletes_message_from_database(self):
        '''Deletes a message from the database.'''
        with app.app_context():
            # Create a new test message
            hello_from_liza = Message(
                body="Hello 👋",
                username="Liza"
            )
            db.session.add(hello_from_liza)
            db.session.commit()

            # Send DELETE request to remove the message
            app.test_client().delete(f'/messages/{hello_from_liza.id}')

            # Verify that the message was deleted from the database
            deleted_message = Message.query.filter_by(body="Hello 👋").first()
            assert not deleted_message

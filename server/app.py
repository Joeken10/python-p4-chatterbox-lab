from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from models import db, Message
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# Get all messages
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    messages_list = [message.to_dict() for message in messages]
    return jsonify(messages_list), 200

# Create a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()
    if not data.get('body') or not data.get('username'):
        return make_response(jsonify({"error": "Missing body or username"}), 400)
    
    new_message = Message(
        body=data['body'],
        username=data['username'],
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201

# Update a message
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    # Use db.session.get() to avoid deprecation warnings
    message = db.session.get(Message, id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    data = request.get_json()
    if 'body' in data:
        message.body = data['body']
        message.updated_at = datetime.now()

    db.session.commit()

    return jsonify(message.to_dict()), 200

# Delete a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    # Use db.session.get() to avoid deprecation warnings
    message = db.session.get(Message, id)
    if not message:
        return make_response(jsonify({"error": "Message not found"}), 404)

    db.session.delete(message)
    db.session.commit()

    return make_response(jsonify({"message": "Message deleted"}), 200)

if __name__ == '__main__':
    app.run(port=5555)

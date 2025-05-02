from flask import Blueprint, request, jsonify
import firebase_admin
from firebase_admin import credentials
import os
from dotenv import load_dotenv
from firebase_admin import credentials, firestore, auth
load_dotenv()
cred = credentials.Certificate(os.getenv('sdk'))
firebase_admin.initialize_app(cred)

menue_bp = Blueprint('Menue',__name__)
# Firestore DB
db = firestore.client()

#chekc wether user is online or ofline
@menue_bp.route('/set_status', methods=['POST'])
def set_status():
    try:
        data = request.get_json()
        username = data.get("username")
        status = data.get("status")

        if username is None or status is None:
            return jsonify({"error": "Missing username or status"}), 400

        query = db.collection("Users").where("Username", "==", username).limit(1).stream()
        user_doc = next(query, None)
        if not user_doc:
            return jsonify({"error": "User not found"}), 404

        user_id = user_doc.id
        db.collection("Users").document(user_id).update({"Status": status})

        return jsonify({"message": f"Status updated to {status}"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#get usersername by id for communication
@menue_bp.route('/get_username_by_id', methods=['GET'])
def get_username_by_id():
    try:
        doc_id = request.args.get('doc_id')
        if not doc_id:
            return jsonify({"error": "Missing doc_id"}), 400
        doc = db.collection("Users").document(doc_id).get()
        if not doc.exists:
            return jsonify({"error": "User not found"}), 404
        data = doc.to_dict()
        return jsonify({"Username": data.get("Username", doc_id)}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

#fetch user's info from FireStore
@menue_bp.route('/get_use_info', methods=['GET'])
def get_usr_info():
    try:
        # Get the username from query parameter (sent from frontend)
        username = request.args.get('user_id')  # still using ?user_id= but it's actually a username
        if not username:
            return jsonify({"error": "Missing user_id (username) parameter"}), 400

        # Query the Users collection where Username matches
        users_ref = db.collection("Users")
        query = users_ref.where("Username", "==", username).limit(1).stream()
        user_doc = next(query, None)

        if not user_doc:
            return jsonify({"error": "User not found"}), 404

        data = user_doc.to_dict()
        number_of_wins = data.get("NumberOfWins", 0)
        points = data.get("Points", 0)

        return jsonify({
            "NumberOfWins": number_of_wins,
            "Points": points,
            "Username": data.get("Username", "Unknown")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


#Authenticate ure and it returns uID and Email
@menue_bp.route('/login_auth', methods=['POST'])
def login_auth():
    try:
        data = request.get_json()
        id_token = data.get('idToken')

        if not id_token:
            return jsonify({'error': 'Missing ID token'}), 400

        # Verify token with Firebase
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']

        # Optionally get user details
        user = auth.get_user(uid)

        return jsonify({
            'message': 'Authentication successful',
            'uid': uid,
            'email': user.email
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 401

#this fetch the friends list
@menue_bp.route('/get_friends_list', methods=['GET'])
def get_friends_list():
    try:
        username = request.args.get('user_id')  # This is actually the username now
        if not username:
            return jsonify({"error": "Missing username"}), 400

        # Look up user by username
        query = db.collection("Users").where("Username", "==", username).limit(1).stream()
        user_doc = next(query, None)

        if not user_doc:
            return jsonify({"error": "User not found"}), 404

        data = user_doc.to_dict()
        friends_ids = data.get("Friends", [])

        friends_data = []
        for fid in friends_ids:
            friend_doc = db.collection("Users").document(fid).get()
            if friend_doc.exists:
                friend_data = friend_doc.to_dict()
                friends_data.append({
                    "id": fid,
                    "Username": friend_data.get("Username", ""),
                    "Points": friend_data.get("Points", 0),
                    "NumberOfWins": friend_data.get("NumberOfWins", 0),
                    "Online": friend_data.get("Status", False)
                })

        return jsonify({"friends": friends_data}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#search users
@menue_bp.route('/search_user_by_username', methods=['GET'])
def search_user_by_username():
    try:
        # Get the username from query parameter
        username = request.args.get('username')
        if not username:
            return jsonify({"error": "Missing username parameter"}), 400

        # Query the Users collection for a matching Username
        users_ref = db.collection('Users')
        query = users_ref.where('Username', '==', username).stream()

        result = []
        for doc in query:
            user_data = doc.to_dict()
            result.append({
                "id": doc.id,
                "Username": user_data.get("Username"),
                "email": user_data.get("email"),
                "Points": user_data.get("Points", 0),
                "NumberOfWins": user_data.get("NumberOfWins", 0)
            })

        if not result:
            return jsonify({"message": "User not found"}), 404

        return jsonify({"user": result[0]}), 200  # return only first match

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#send friend request
@menue_bp.route('/send_friend_request', methods=['POST'])
def send_friend_request():
    try:
        data = request.get_json()
        sender_username = data.get('sender_username')
        receiver_username = data.get('receiver_username')

        if not sender_username or not receiver_username:
            return jsonify({"error": "Missing sender or receiver username"}), 400

        # Look up users
        sender_query = db.collection("Users").where("Username", "==", sender_username).limit(1).stream()
        receiver_query = db.collection("Users").where("Username", "==", receiver_username).limit(1).stream()
        sender_doc = next(sender_query, None)
        receiver_doc = next(receiver_query, None)

        if not sender_doc or not receiver_doc:
            return jsonify({"error": "Sender or receiver not found"}), 404

        sender_id = sender_doc.id
        receiver_id = receiver_doc.id

        # Load existing data or fallback to empty
        sender_ref = db.collection("Users").document(sender_id)
        receiver_ref = db.collection("Users").document(receiver_id)

        sender_data = sender_ref.get().to_dict()
        receiver_data = receiver_ref.get().to_dict()

        sent = sender_data.get("FriendRequestsSent", [])
        received = receiver_data.get("FriendRequestsReceived", [])

        # Avoid duplicate request
        if receiver_id in sent:
            return jsonify({"message": "Request already sent"}), 409
        if sender_id in received:
            return jsonify({"message": "Request already pending"}), 409

        # Update both users
        sender_ref.update({
            "FriendRequestsSent": firestore.ArrayUnion([receiver_id])
        })
        receiver_ref.update({
            "FriendRequestsReceived": firestore.ArrayUnion([sender_id])
        })

        return jsonify({"message": "Friend request sent"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#accept a friend request
@menue_bp.route('/accept_friend_request', methods=['POST'])
def accept_friend_request():
    try:
        data = request.get_json()
        user_id = data.get('user_id')            # The one accepting the request
        sender_id = data.get('sender_id')        # The one who sent the request

        if not user_id or not sender_id:
            return jsonify({"error": "Missing user or sender ID"}), 400

        # Add each other as friends
        db.collection("Users").document(user_id).update({
            "Friends": firestore.ArrayUnion([sender_id]),
            "FriendRequestsReceived": firestore.ArrayRemove([sender_id])
        })

        db.collection("Users").document(sender_id).update({
            "Friends": firestore.ArrayUnion([user_id]),
            "FriendRequestsSent": firestore.ArrayRemove([user_id])
        })

        return jsonify({"message": "Friend request accepted"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#gers friends requests
@menue_bp.route('/get_friend_requests', methods=['GET'])
def get_friend_requests():
    try:
        username = request.args.get('user_id')  # This is actually the Username
        if not username:
            return jsonify({"error": "Missing username"}), 400

        # Look up document by username
        query = db.collection("Users").where("Username", "==", username).limit(1).stream()
        user_doc = next(query, None)

        if not user_doc:
            return jsonify({"error": "User not found"}), 404

        data = user_doc.to_dict()
        received = data.get("FriendRequestsReceived", [])
        sent = data.get("FriendRequestsSent", [])

        return jsonify({
            "received": received,
            "sent": sent
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

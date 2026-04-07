import pyrebase
import os

# Firebase configuration
firebase_config = {
    "apiKey": "YOUR_API_KEY",
    "authDomain": "YOUR_PROJECT_ID.firebaseapp.com",
    "projectId": "YOUR_PROJECT_ID",
    "storageBucket": "YOUR_PROJECT_ID.appspot.com",
    "messagingSenderId": "YOUR_SENDER_ID",
    "appId": "YOUR_APP_ID",
    "databaseURL": ""
}

# Check if we are in Mock Mode (using placeholder keys)
MOCK_MODE = firebase_config["apiKey"] == "YOUR_API_KEY"

class FirebaseAuth:
    def __init__(self):
        self.auth = None
        if not MOCK_MODE:
            try:
                self.firebase = pyrebase.initialize_app(firebase_config)
                self.auth = self.firebase.auth()
            except Exception as e:
                print(f"Firebase Init Error: {e}")

    def sign_up(self, email, password):
        if MOCK_MODE:
            # Mock success for testing
            return {"localId": "mock_user_id", "email": email}, None
        
        try:
            user = self.auth.create_user_with_email_and_password(email, password)
            if self.auth:
                self.auth.send_email_verification(user['idToken'])
            return user, None
        except Exception as e:
            return None, str(e)

    def sign_in(self, email, password):
        if MOCK_MODE:
            # Mock success for testing (any non-empty password works)
            if email and password:
                return {"localId": "mock_user_id", "email": email}, None
            return None, "Invalid email or password."

        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            account_info = self.auth.get_account_info(user['idToken'])
            if account_info['users'][0]['emailVerified']:
                return user, None
            else:
                return None, "Please verify your email first."
        except Exception as e:
            return None, str(e)

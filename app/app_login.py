import pyrebase
import os
import json

# --- FIREBASE CONFIGURATION ---
firebase_config = {
    "apiKey": "AIzaSyDIAmDh1LMoZDjD0dZoiiEy5dxKJRsrAbQ",
    "authDomain": "skinalyse-eb362.firebaseapp.com",
    "projectId": "skinalyse-eb362",
    "storageBucket": "skinalyse-eb362.firebasestorage.app",
    "messagingSenderId": "36288039539",
    "appId": "1:36288039539:web:3f812989745b0e8c0bf806",
    "measurementId": "G-WLC9RECMS8",
    "databaseURL": ""
}

class FirebaseAuth:
    def __init__(self):
        try:
            self.firebase = pyrebase.initialize_app(firebase_config)
            self.auth = self.firebase.auth()
            print("[*] Firebase Auth: Initialized Successfully.")
        except Exception as e:
            print(f"[!] Firebase Init Error: {e}")
            self.auth = None

    def sign_up(self, email, password):
        try:
            # Create the user
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # Send verification email immediately
            # user['idToken'] is required to tell Firebase which user to verify
            self.auth.send_email_verification(user['idToken'])
            
            return user, None
        except Exception as e:
            # Use the error parser we discussed to clean up the JSON error string
            return None, self._parse_error(e)

    def sign_in(self, email, password):
        """Authenticates user and checks if email is verified."""
        try:
            user = self.auth.sign_in_with_email_and_password(email, password)
            
            # Check if email is verified
            account_info = self.auth.get_account_info(user['idToken'])
            is_verified = account_info['users'][0]['emailVerified']
            
            if is_verified:
                return user, None
            else:
                return None, "Please verify your email before logging in."
        except Exception as e:
            return None, self._parse_error(e)

    def _parse_error(self, error):
        """Extracts readable error messages from the Firebase JSON response."""
        try:
            # error.args[1] usually contains the JSON string from Google
            error_data = json.loads(error.args[1])
            return error_data['error']['message'].replace('_', ' ')
        except:
            return str(error)
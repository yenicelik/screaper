"""
    Following this medium post
    https://medium.com/@nschairer/flask-api-authentication-with-firebase-9affc7b64715
"""
import os
import json
import firebase_admin
import pyrebase
from dotenv import load_dotenv
from firebase_admin import credentials, auth
from flask import Flask, request, jsonify
from six import wraps

load_dotenv()

from screaper_backend.application.authentication import whitelist_emails

def check_authentication_token(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if not request.headers.get('authorization'):
            return jsonify({
                "errors": ["Permission denied (E.001)", str(request.headers)]
            }), 403
        try:
            auth_token = request.headers['authorization']
            user = auth.verify_id_token(auth_token)
            # Make sure the user's email is in the whitelist
            print("User is: ", user)
            if 'email' not in user:
                print("errors", ["Permission denied (E.002)", str(request.headers)])
                return jsonify({
                    "errors": ["Permission denied (E.002)", str(request.headers)]
                }), 403

            if user['email'] not in whitelist_emails:
                print("errors", ["Permission denied (E.002)", str(request.headers)])
                return jsonify({
                    "errors": ["Permission denied (E.002)", str(request.headers)]
                }), 403

            # Check if e-mail was verified
            if not user['email_verified']:
                print("errors", ["Please verify your e-mail!", str(request.headers)])
                return jsonify({
                    "errors": ["Please verify your e-mail!", str(request.headers)]
                }), 403

            request.user = user

        except Exception as e:
            return jsonify({
                "errors": ["Permission denied (E.003)", str(request.headers), str(e)]
            }), 403

        return f(*args, **kwargs)

    return wrap


class FirebaseWrapper:

    def __init__(self):
        self.cred = credentials.Certificate(os.getenv("FIREBASE_CRED"))
        self.firebase = firebase_admin.initialize_app(self.cred)
        self.pb = pyrebase.initialize_app(json.load(open(os.getenv("FIREBASE_APP"))))

    def verify_token(self, id_token):
        decoded_token = auth.verify_id_token(id_token)
        uid = decoded_token['uid']
        email = decoded_token['email']
        print("Decoded token is: ", decoded_token)
        print("Decoded token is: ", decoded_token)

        # Check if email is within the whitelist (hardcoded here ...)
        # I know this could written more efficiently... but this is to be more bug-prone lol
        if email in ["yedavid@ethz.ch"]:
            return True
        else:
            return False

firebase_wrapper = FirebaseWrapper()

if __name__ == "__main__":
    # get all users

    # auth.getUser(uid)
    # users = db.child("users").get()

    # login user
    email = "yedavid@ethz.ch"
    password = "password"
    token = auth.sign_in_with_email_and_password(email, password)


    print("Checking if we can verify the authentication")
    uid = "6QXFCBNIgSdZOcdLJbfW3a0w1KS2"
    firebase_wrapper.verify_token(uid)

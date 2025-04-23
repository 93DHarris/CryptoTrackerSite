import os
from dotenv import load_dotenv
import json
from flask import Flask, redirect, url_for, session, request, render_template
from google_auth_oauthlib.flow import Flow
from google.auth.transport.requests import Request
import google.auth
from googleapiclient.discovery import build
import logging


logging.basicConfig(level=logging.INFO)
load_dotenv()

# Fetch from environment variables
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
PROJECT_ID = os.getenv("PROJECT_ID")


# Set up Flask app
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# OAuth 2.0 client secrets from environment variables
CLIENT_SECRETS = {
    "installed": {
        "client_id": GOOGLE_CLIENT_ID,
        "project_id": PROJECT_ID,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": GOOGLE_CLIENT_SECRET
    }
}

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# The redirect URI you set up in Google Cloud Console
REDIRECT_URI = '/callback'

@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect(url_for('authorize'))
    
    credentials = json.loads(session['credentials'])
    credentials = google.auth.credentials.Credentials.from_authorized_user_info(credentials)

    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            return redirect(url_for('authorize'))

    
    try:
        sheets_service = build('sheets', 'v4', credentials=credentials)
        sheet = sheets_service.spreadsheets().values().get(spreadsheetId=GOOGLE_SHEET_ID, range="Sheet1").execute()
        records = sheet.get('values', [])
        return render_template("website.html", records=records)
    except Exception as e:
        return f'Error: {e}'

@app.route('/authorize')
def authorize():
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        redirect_uri=url_for('callback', _external=True)
    )
    authorization_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true')
    session['state'] = state
    return redirect(authorization_url)

@app.route('/callback')
def callback():
    state = session['state']
    flow = Flow.from_client_config(
        CLIENT_SECRETS,
        scopes=SCOPES,
        state=state,
        redirect_uri=url_for('callback', _external=True)
    )
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session['credentials'] = json.dumps(credentials.to_json())
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)



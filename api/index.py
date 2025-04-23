from flask import Flask, render_template
import gspread
from google.auth import default
from datetime import datetime

app = Flask(__name__)

# Authenticate using ADC (application-default credentials)
creds, _ = default()
client = gspread.authorize(creds)

# Open the sheet
sheet = client.open("FiverrDemo").sheet1

@app.route("/")
def index():
    records = sheet.get_all_records()
    last_updated = datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    return render_template("index.html", data=records, last_updated=last_updated)

def handler(environ, start_response):
    return app(environ, start_response)

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 5000
    print(f"\nUp @ http://{host}:{port}\n")
    app.run(debug=True, host=host, port=port)

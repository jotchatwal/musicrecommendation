from flask import Flask, request, render_template, redirect, url_for, session
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)
app.secret_key = "2dcf15dcc7d5ec9958ceb1c2a6bc249e9b774f5538ae83e6"  # Set your secret key here

# Google Sheets API credentials
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('./credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("credentials").sheet1

def get_users_from_sheet():
    records = sheet.get_all_records()
    return {record['username']: record['password'] for record in records}

@app.route('/')
def home():
        return render_template('login.html')  # Ensure you have this template

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        print(f"Received username: {username}, password: {password}")
        users = get_users_from_sheet()
        print(f"Users from sheet: {users}")
        if username in users:
            stored_password = str(users.get(username)).strip()  # Convert stored password to string
            print(f"Stored password for '{username}': '{stored_password}'")
            if stored_password == password:
                print(f"Password matches for username: {username}")
                session['username'] = username
                return redirect(url_for('landing'))
            else:
                print(f"Password does not match for username: {username}")
                return render_template('login.html', error='Invalid credentials')
        else:
            print(f"Username {username} not found in users")
            return render_template('login.html', error='Invalid credentials')
    return render_template('login.html')

@app.route('/home')
def landing():
        return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

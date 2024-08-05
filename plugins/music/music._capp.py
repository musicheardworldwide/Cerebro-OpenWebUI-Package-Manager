
from flask import Flask, request, jsonify
import requests
import hashlib
import time

app = Flask(__name__)

# Define constants
ampache_url = 'https://app.heargoodmusic.com'
username = 'artist_username'
password = 'artist_password'
version = '6.5.0'

# Define the make_request function
def make_request(action, token, data=None, files=None):
    params = {'action': action, 'auth': token}
    response = requests.post(f'{ampache_url}/server/json.server.php', params=params, data=data, files=files, verify=True)
    response.raise_for_status()
    return response.json()

# Define the login route
@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data['username']
    password = data['password']

    # Generate the passphrase
    timestamp = str(int(time.time()))
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    passphrase = hashlib.sha256((timestamp + password_hash).encode()).hexdigest()

    # Set headers and parameters for the handshake request
    headers = {'User-Agent': 'Ampache Handshake'}
    params = {'action': 'handshake', 'auth': passphrase, 'timestamp': timestamp, 'user': username, 'version': version}

    # Send the handshake request
    response = requests.get(ampache_url + '/server/json.server.php', headers=headers, params=params, verify=True)
    response.raise_for_status()

    # Check if the handshake was successful
    if response.status_code == 200:
        response_json = response.json()
        token = response_json.get('auth')
        if token:
            return jsonify({'token': token})
        else:
            return jsonify({'error': 'Token not found in response'}), 400
    else:
        return jsonify({'error': 'Handshake failed'}), 400

# Define the upload route
@app.route('/api/upload', methods=['POST'])
def upload():
    token = request.headers.get('Authorization')
    file = request.files['file']
    files = {'file': file}
    response = make_request('upload', token, files=files)
    return jsonify(response)

# Define the update profile route
@app.route('/api/update_profile', methods=['POST'])
def update_profile():
    token = request.headers.get('Authorization')
    profile_data = request.json
    response = make_request('update_user', token, data=profile_data)
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)

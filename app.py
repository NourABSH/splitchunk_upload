from flask import Flask, request, jsonify
from functools import wraps
import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError
import jwt
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# Create an instance of the Flask class
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'

# basic logging
logging.basicConfig(level=logging.INFO)

# dummy database of users
users = {
    "username1": generate_password_hash("password1")
}

# Function to check for valid JWT in the request
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# define route for GET requests, initialize boto3 S3 client, 
# retrieve filename from client-side JavaScript
@app.route('/generate-presigned-url')
def generate_presigned_url():
    s3_client = boto3.client('s3')
    file_name = request.args.get('filename')
    if not file_name:
        return jsonify({'error': 'Filename parameter is missing'}), 400
    
# generate pre-signed url for PUT operation to bucket, and error handling
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'your-bucket-name',
                                                            'Key': file_name,
                                                            'ContentType': 'application/octet-stream'},
                                                    ExpiresIn=3600)
    except NoCredentialsError:
        logging.error("No AWS credentials available")
        return jsonify({'error': 'Credentials not available'}), 403
    except ClientError as e:
        logging.error(f"Client error in generating pre-signed URL: {e}")
        return jsonify({'error': 'Failed to generate pre-signed URL'}), 500
    
# return URL to client as json
    return jsonify({'url': response})

# user login route to issue JWT
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    user = users.get(username)

    if user and check_password_hash(user, password):
        token = jwt.encode({
            'sub': username,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expires in 30 minutes
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

# server start
if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
import os
from functools import wraps
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
import logging
import jwt
import datetime
import mysql.connector
from flask_cors import CORS
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash


# Create an instance of the Flask class
app = Flask(__name__)
CORS(app) # enables CORS for all routes and methods
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Establishing a database connection using environment variables
try:
    connection = mysql.connector.connect(
        host=os.getenv('SPLITCHUNK_UPLOAD_DB_HOST', 'localhost'),
        database=os.getenv('SPLITCHUNK_UPLOAD_DB_NAME', 'splitchunk_upload'),
        user=os.getenv('SPLITCHUNK_UPLOAD_DB_USERNAME', 'your_default_username'),
        password=os.getenv('SPLITCHUNK_UPLOAD_DB_PASSWORD', 'your_default_password')
    )
    print("Connected to MySQL successfully")
except Error as e:
    print("Error while connecting to MySQL:", e)


# basic logging
logging.basicConfig(level=logging.INFO)

# Route for user registration
@app.route('/register', methods=['POST'])
def register():
    # Parse username and password from the incoming request
    username = request.json.get('username')
    password = request.json.get('password')

    # Generate a password hash to securely store the password
    hashed_password = generate_password_hash(password)

    # Initialize cursor to execute database queries
    cursor = connection.cursor()
    try:
        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, hashed_password))
        connection.commit()  # Commit the transaction to make sure data is saved in the database
        return jsonify({"message": "User registered successfully!"}), 201
    except mysql.connector.IntegrityError:
        return jsonify({"error": "This username is already taken"}), 409
    except Error as e:
        return jsonify({"error": "Failed to register user due to database error"}), 500
    except Exception as e:
        print("General error:", e)
        return jsonify({"error": "An unexpected error occurred"}), 500
    finally:
        # Close the cursor to free database resources
        cursor.close()



# Function to check for valid JWT in the request
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 403
        try:
            token = token.split()[1]  # Split "Bearer <token>"
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 401
        except Exception as e:
            print(f"Unexpected error: {e}")
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated

# define route for GET requests, initialize boto3 S3 client, 
# retrieve filename from client-side JavaScript
@app.route('/generate-presigned-url')
@token_required
def generate_presigned_url():
    file_name = request.args.get('filename')
    if not file_name:
        return jsonify({'error': 'Filename parameter is missing'}), 400
    s3_client = boto3.client('s3')

# generate pre-signed url for PUT operation to bucket, and error handling
    try:
        presigned_url = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'splitchunk-upload',
                                                            'Key': file_name,
                                                            'ContentType': 'application/octet-stream'},
                                                    ExpiresIn=3600)
        # return URL to client as json
        return jsonify({'url': presigned_url})
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 403
    except ClientError as e:
        return jsonify({'error': 'Failed to generate pre-signed URL'}), 500
    

# user login route to issue JWT
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    cursor = connection.cursor()
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    user_record = cursor.fetchone()
    cursor.close()

    if user_record and check_password_hash(user_record[0], password):
        token = jwt.encode({
            'sub': username,
            'iat': datetime.datetime.utcnow(),
            'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # Token expires in 30 minutes
        }, app.config['SECRET_KEY'], algorithm='HS256')

        return jsonify({'token': token})
    else:
        print("Login failed for user:", username)  # Log for debugging
        return jsonify({'message': 'Invalid credentials'}), 401

# server start
if __name__ == '__main__':
    app.run(debug=True)
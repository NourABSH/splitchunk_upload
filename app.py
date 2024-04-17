from flask import Flask, request, jsonify
import boto3
import logging
from botocore.exceptions import NoCredentialsError, ClientError

# Create an instance of the Flask class
app = Flask(__name__)

# basic logging
logging.basicConfig(level=logging.INFO)

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

# server start
if __name__ == '__main__':
    app.run(debug=True)
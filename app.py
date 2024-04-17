from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import NoCredentialsError

# Create an instance of the Flask class
app = Flask(__name__)

# define route for GET requests, initialize boto3 S3 client, 
# retrieve filename from client-side JavaScript
@app.route('/generate0presigned-url')
def generate_presigned_url():
    s3_client = boto3.client('s3')
    file_name = request.args.get('filename ')
# generate pre-signed url for PUT operation to bucket, and error handling
    try:
        response = s3_client.generate_presigned_url('put_object',
                                                    Params={'Bucket': 'your-bucket-name',
                                                            'Key': file_name},
                                                    ExpiresIn=3600)
    except NoCredentialsError:
        return jsonify({'error': 'Credentials not available'}), 403
    
# return URL to client as json
    return jsonify({'url': response})

# server start
if __name__ == '__main__':
    app.run(debug=True)
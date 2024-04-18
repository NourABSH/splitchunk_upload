import argparse
import requests

# send GET request for a pre-signed URL from the Flask server
def get_presigned_url(server_url, filename):
    response = requests.get(f'{server_url}/generate-presigned-url', params={'filename': filename})
    if response.status_code == 200:
        return response.json()['url']
    else:
        raise Exception("Failed to get pre-signed URL: " + response.text)

# upload file to S3 using pre-signed URL
def upload_file(url, file_path):
    with open(file_path, 'rb') as f:
        response = requests.put(url, data=f)
        return response.status_code == 200

# set up command-line argument parsing using 'file_path' and 'server_url'
def main():
    parser = argparse.ArgumentParser(description='Upload files to AWS S3 via a pre-signed URL.')
    parser.add_argument('file_path', type=str, help='Path to the file to upload.')
    parser.add_argument('server_url', type=str, help='URL of the Flask server providing pre-signed URLs.')
    args = parser.parse_args()

# process arguments, retrieve URL and upload
    try:
        url = get_presigned_url(args.server_url, args.file_path)
        if upload_file(url, args.file_path):
            print("Upload successful!")
        else:
            print("Upload failed!")
    except Exception as e:
        print(str(e))

if __name__ == "__main__":
    main()

# Splitchunk Upload Application

## Overview
Splitchunk Upload is a Flask-based application that allows users to upload large files securely to AWS S3. It uses MySQL for user management.

## Setup

### Prerequisites
- Python 3.x
- Flask
- MySQL
- AWS Account and configured AWS S3 bucket

### Installation
Clone the repository and install the required packages:
https://github.com/NourABSH/splitchunk_upload.git
cd splitchunk_upload
pip install -r requirements.txt

### Configuring Environment Variables

To run the Splitchunk Upload application, you need to set up several environment variables. Here's how you can set them up on different operating systems:

#### Unix-like Systems (Linux, macOS)
Open your terminal and add the following lines to your shell configuration file (`.bashrc`, `.zshrc`, etc.):
```bash
export SPLITCHUNK_UPLOAD_DB_HOST='localhost'
export SPLITCHUNK_UPLOAD_DB_NAME='splitchunk_upload'
export SPLITCHUNK_UPLOAD_DB_USERNAME='your_username'
export SPLITCHUNK_UPLOAD_DB_PASSWORD='your_password'

to reload the configuration:
source ~/.bashrc  # or source ~/.zshrc

set SPLITCHUNK_UPLOAD_DB_HOST=localhost
set SPLITCHUNK_UPLOAD_DB_NAME=splitchunk_upload
set SPLITCHUNK_UPLOAD_DB_USERNAME=your_username
set SPLITCHUNK_UPLOAD_DB_PASSWORD=your_password

### For a permanent setup, search for "Environment Variables" in Windows search and add the above variables through the GUI.

### Running the application
python app.py

### Contributing
Contributions are welcome! Please fork the repository and open a pull request with your improvements.
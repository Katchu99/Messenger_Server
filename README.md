# Messenger Server

A Flask-based web application that provides a messaging service with JWT authentication.

## Features

- User registration and login
- JWT authentication
- Token-based authentication
- Routes for checking tokens and user authentication

## Technologies Used

- Flask
- JWT (JSON Web Tokens)
- Python

## Installation

To install the project, clone the repository and install the required dependencies using pip:
* `git clone https://github.com/Katchu99/messenger-server.git cd messenger-server`
* `pip install -r requirements.txt`

## Usage

To run the application, use the following command:
* `python server.py`


This will start the Flask development server, and you can access the application at `http://localhost:5000`.

## API Endpoints

The following API endpoints are available:

- `/login`: Login endpoint that accepts a username and password
- `/register`: Registration endpoint that accepts a username and password
- `/check-token`: Endpoint that checks if a token is valid
- `/protected`: Protected endpoint that requires a valid token to access

## License

This project is licensed under the MIT License.

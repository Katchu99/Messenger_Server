####LIBRARY IMPORTS####
import logging
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_cors import CORS

####DATABASE IMPORT####
from database.db import Database

####ROUTE IMPORTS####
from routes.authRoutes import auth_routes as auth
#from routes.userRoutes import user

##INITIALIZE LOGGING##
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='server.log',
    filemode='w'
)

# ##INITIALIZE DATABASE##
Database()

##ADDING CONSOLE HANDLER##
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

#INITIALIZE LOGGER#
logger = logging.getLogger(__name__)

####INITIALIZE FLASK APP####
logger.info('Initializing Flask App...')
app = Flask(__name__)
cors = CORS(app)

##JWT CONFIGURATION##
app.config['JWT_SECRET_KEY'] = 'secret'
jwt = JWTManager(app)

##REGISTER ROUTES##
app.register_blueprint(auth)
#app.register_blueprint(user)

if __name__ == '__main__':
    logger.info('Starting Flask App...')
    app.run(debug=True, host='localhost', port=5000, threaded=True)
    #socketio.run(app, debug=True, host='localhost', port=5000, ssl_context=ssl_context)
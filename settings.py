import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
PORT = os.getenv("PORT")
FLASK_PRODUCTION = os.getenv('FLASK_PRODUCTION', 'False').lower() == 'true' 

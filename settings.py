import os
from os.path import join, dirname
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
PORT = int(os.getenv("PORT"))
FAST_PRODUCTION = os.getenv('FAST_PRODUCTION', 'False').lower() == 'true' 

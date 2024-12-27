from dotenv import load_dotenv
import os

load_dotenv()

MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
PROXYMESH_HOST = os.getenv('PROXYMESH_HOST')
PROXYMESH_PORT = int(os.getenv('PROXYMESH_PORT', '31280'))
TWITTER_USERNAME = os.getenv('TWITTER_USERNAME')
TWITTER_PASSWORD = os.getenv('TWITTER_PASSWORD')
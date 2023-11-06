import os
from dotenv import load_dotenv

current_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(current_dir, '.env')
load_dotenv(dotenv_path)
RABBIT_HOST = os.getenv('RABBIT_HOST')
RABBIT_LOGIN = os.getenv('RABBIT_LOGIN')
RABBIT_PASS = os.getenv('RABBIT_PASS')
DATA_PATH = os.getenv('DATA_PATH')

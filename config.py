from dotenv import load_dotenv
import os

def configure():
    load_dotenv()


TOKEN = os.getenv("token")
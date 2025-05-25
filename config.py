import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 8000
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
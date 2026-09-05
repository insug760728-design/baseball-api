import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = 'Sports Data Hub API'
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./sports_data.db')
    API_V1_STR: str = '/api/v1'
    API_SPORTS_KEY: str = os.getenv('API_SPORTS_KEY', '')
    RAPIDAPI_KEY: str = os.getenv('RAPIDAPI_KEY', '')

settings = Settings()

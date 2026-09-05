import os

class Settings:
    PROJECT_NAME: str = 'Sports Data Hub API'
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./sports_data.db')
    API_V1_STR: str = '/api/v1'

settings = Settings()

import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./master_vrp.db")

    GOOGLE_DISTANCE_MATRIX_URL: str = "https://maps.googleapis.com/maps/api/distancematrix/json"

settings = Settings()
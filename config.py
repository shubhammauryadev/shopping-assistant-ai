"""Configuration and environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = "sqlite:///./shopping_assistant.db"

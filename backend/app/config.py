import os

DATABASE_URL = os.getenv("INSIGHTDESK_DATABASE_URL", "sqlite:///./insightdesk.db")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

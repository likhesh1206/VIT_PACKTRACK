import os, sys
# Add the backend directory to PYTHONPATH so we can import the FastAPI app
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(backend_path)

# Import the FastAPI app defined in backend/main.py
from main import app

# Vercel's Python runtime automatically detects the ASGI callable named 'app'.
# No further code needed.

import os
import sys

# Add the parent directory to path so we can import backend
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import the Flask app
from backend.app import app

# Vercel needs this 'app' variable
# It acts as the handler
if __name__ == '__main__':
    app.run()

"""
Run the Grace API server
"""

import os
from src.api_server import app

if __name__ == "__main__":
    # Run the app
    app.run(host="0.0.0.0", port=9000)

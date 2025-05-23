"""
Run the Grace API server
"""

import os
from src.api_server import app


# Function to register static routes
def register_static_routes():
    """
    Register routes for serving static files from the UI directory.
    This should be called after all other routes are registered.
    """
    # Get the directory of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one directory and then to the ui folder
    ui_dir = os.path.join(os.path.dirname(current_dir), "ui")

    @app.route("/", endpoint="ui_index")
    def ui_index():
        return app.send_static_file("index.html")

    @app.route("/<path:path>", endpoint="ui_static")
    def ui_static(path):
        return app.send_static_file(path)


if __name__ == "__main__":
    # Set static folder
    app.static_folder = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "ui"
    )

    # Register static routes
    register_static_routes()

    # Run the app
    app.run(host="0.0.0.0", port=8000)

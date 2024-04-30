# This is the entry point into our application.
from dashboard import app

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
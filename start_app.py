"""
Simple script to start the application without requiring gunicorn
"""
from main import app

if __name__ == "__main__":
    print("Starting application on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=True)
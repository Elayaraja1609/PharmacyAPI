# Elastic Beanstalk entry point
# This file tells AWS Elastic Beanstalk how to run your Flask app
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app import app

if __name__ == "__main__":
    app.run()


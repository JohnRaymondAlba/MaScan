"""
Vercel Serverless Function Entry Point for MaScan Flask Application
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../app'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../app/src'))

from flask_app import create_app

# Create app instance
app = create_app()

# Export for Vercel

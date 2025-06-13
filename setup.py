#!/usr/bin/env python
"""
Setup script for the IFRC Surge Alert System.
This script generates initial migrations for the custom apps and applies them.
"""
import os
import subprocess
import sys

def main():
    """
    Generate initial migrations for custom apps and apply them.
    """
    print("Generating migrations for custom apps...")
    subprocess.run([sys.executable, "manage.py", "makemigrations", "surge", "users"], check=True)
    
    print("Applying migrations...")
    subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
    
    print("Setup complete!")
    print("You can now run the development server with: python manage.py runserver")

if __name__ == "__main__":
    main()
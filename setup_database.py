#!/usr/bin/env python
"""
Setup script for the IFRC Surge Alert System database.
This script checks if PostgreSQL is installed, creates the database if it doesn't exist,
and runs the migrations.
"""
import os
import subprocess
import sys
import platform
import shutil

def check_postgres_installed():
    """
    Check if PostgreSQL is installed on the system.
    """
    print("Checking if PostgreSQL is installed...")
    
    # Check if psql command is available
    psql_path = shutil.which('psql')
    if not psql_path:
        print("PostgreSQL is not installed or not in PATH.")
        print("Please install PostgreSQL and make sure it's in your PATH.")
        print("You can download PostgreSQL from: https://www.postgresql.org/download/")
        return False
    
    print(f"Found PostgreSQL client at: {psql_path}")
    return True

def check_postgres_running():
    """
    Check if PostgreSQL server is running.
    """
    print("Checking if PostgreSQL server is running...")
    
    try:
        # Try to connect to PostgreSQL server
        result = subprocess.run(
            ['psql', '-h', 'localhost', '-U', 'postgres', '-c', 'SELECT 1'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=dict(os.environ, PGPASSWORD='postgres')
        )
        
        if result.returncode == 0:
            print("PostgreSQL server is running.")
            return True
        else:
            print("PostgreSQL server is not running or credentials are incorrect.")
            print("Error:", result.stderr.decode())
            return False
    except Exception as e:
        print(f"Error checking PostgreSQL server: {e}")
        return False

def create_database():
    """
    Create the PostgreSQL database if it doesn't exist.
    """
    print("Checking if database exists...")
    
    # Check if database exists
    check_db_cmd = [
        'psql', 
        '-h', 'localhost', 
        '-U', 'postgres', 
        '-c', "SELECT 1 FROM pg_database WHERE datname='postgres'"
    ]
    
    result = subprocess.run(
        check_db_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=dict(os.environ, PGPASSWORD='postgres')
    )
    
    # If the database doesn't exist, create it
    if '1 row' not in result.stdout.decode():
        print("Creating database 'postgres'...")
        create_db_cmd = ['createdb', '-h', 'localhost', '-U', 'postgres', 'postgres']
        try:
            subprocess.run(
                create_db_cmd,
                check=True,
                env=dict(os.environ, PGPASSWORD='postgres')
            )
            print("Database 'postgres' created successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error creating database: {e}")
            return False
    else:
        print("Database 'postgres' already exists.")
    
    return True

def run_migrations():
    """
    Run Django migrations to set up the database schema.
    """
    print("Running migrations...")
    
    try:
        # Make migrations for custom apps
        subprocess.run([sys.executable, "manage.py", "makemigrations", "surge", "users"], check=True)
        
        # Apply migrations
        subprocess.run([sys.executable, "manage.py", "migrate"], check=True)
        
        print("Migrations applied successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e}")
        return False

def main():
    """
    Main function to set up the database.
    """
    print("Setting up the IFRC Surge Alert System database...")
    
    # Check if PostgreSQL is installed
    if not check_postgres_installed():
        sys.exit(1)
    
    # Check if PostgreSQL server is running
    if not check_postgres_running():
        print("\nPlease make sure PostgreSQL server is running.")
        print("On macOS, you can start it with: brew services start postgresql")
        print("On Windows, you can start it from the Services application.")
        print("On Linux, you can start it with: sudo service postgresql start")
        sys.exit(1)
    
    # Create database if it doesn't exist
    if not create_database():
        sys.exit(1)
    
    # Run migrations
    if not run_migrations():
        sys.exit(1)
    
    print("\nDatabase setup complete!")
    print("You can now run the development server with: python manage.py runserver")
    print("And fetch surge alerts with: python manage.py fetch_surge_alerts")

if __name__ == "__main__":
    main()
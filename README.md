# IFRC Surge Alert System

A Django application that periodically fetches surge alert data from the IFRC API and stores it in a PostgreSQL database. The system also provides user profiles with preferences for deployment.

## Features

- Automatically fetches and stores surge alert data from the IFRC API
- Handles pagination and updates to existing records
- User profiles with preferences:
  - Language abilities
  - Regional preferences
  - Travel restrictions (countries)
  - Qualified profiles
  - Rotation availability

## Technology Stack

- Django 4.2
- PostgreSQL
- Docker & Docker Compose
- Celery for background tasks
- Redis for message broker

## Setup

### Prerequisites

- Docker and Docker Compose (for Docker setup)
- Python 3.9+ (for local setup)
- PostgreSQL (for local setup)
  - [Download PostgreSQL](https://www.postgresql.org/download/)
  - Make sure it's added to your PATH

### Docker Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Start the Docker containers:
   ```
   docker-compose up -d
   ```

3. Create a superuser:
   ```
   docker-compose exec web python manage.py createsuperuser
   ```

4. Populate initial data:
   ```
   docker-compose exec web python manage.py populate_initial_data
   ```

5. Trigger the first data fetch:
   ```
   docker-compose exec web python manage.py fetch_surge_alerts
   ```

### Local Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up the PostgreSQL database:
   ```
   # Option 1: Use the setup_database.py script (recommended)
   python setup_database.py

   # Option 2: Set up manually
   # Make sure PostgreSQL is running locally
   createdb postgres  # Or use pgAdmin or another PostgreSQL client
   python manage.py migrate
   ```

5. Create a superuser:
   ```
   python manage.py createsuperuser
   ```

6. Populate initial data:
   ```
   python manage.py populate_initial_data
   ```

7. Start the development server:
   ```
   python manage.py runserver
   ```

8. Trigger the first data fetch:
   ```
   python manage.py fetch_surge_alerts
   ```

9. (Optional) For background tasks, run Redis and Celery in separate terminals:
   ```
   # Terminal 1: Run Redis (or install and run as a service)
   redis-server

   # Terminal 2: Run Celery worker
   celery -A core worker -l INFO

   # Terminal 3: Run Celery beat
   celery -A core beat -l INFO
   ```

## Usage

### Database Setup

If you're having issues with the database setup, you can use the provided `setup_database.py` script:

```
python setup_database.py
```

This script will:
1. Check if PostgreSQL is installed on your system
2. Verify if the PostgreSQL server is running
3. Create the database if it doesn't exist
4. Run the migrations to set up the database schema

If you encounter any issues, the script will provide helpful error messages and suggestions.

#### Connecting to the Database

When running with Docker, the PostgreSQL database is exposed on port 5433 of your host machine (to avoid conflicts with any local PostgreSQL instance). You can connect to it using:

```
# Using psql
psql -h localhost -p 5433 -U postgres -d postgres

# Password: postgres
```

You can also use GUI tools like pgAdmin by connecting to:
- Host: localhost
- Port: 5433
- Username: postgres
- Password: postgres
- Database: postgres

#### Installing PostgreSQL

If PostgreSQL is not installed on your system, you can download it from the [official website](https://www.postgresql.org/download/).

- **macOS**: You can use Homebrew: `brew install postgresql`
- **Windows**: Use the installer from the [PostgreSQL website](https://www.postgresql.org/download/windows/)
- **Linux**: Use your package manager, e.g., `sudo apt-get install postgresql` (Ubuntu/Debian)

After installation, make sure PostgreSQL is running:

- **macOS**: `brew services start postgresql`
- **Windows**: PostgreSQL should start automatically as a service
- **Linux**: `sudo service postgresql start`

Then run the setup script again:

```
python setup_database.py
```

### Admin Interface

Access the admin interface at `http://localhost:8000/admin/` to:
- View and manage surge alerts
- Manage user profiles
- Configure languages and regions

### Scheduled Tasks

The system automatically fetches new surge alert data every hour. You can modify the schedule in `surge/celery.py`.

### Manual Data Fetch

In development, you can manually fetch surge alert data using the management command:

```
python manage.py fetch_surge_alerts
```

With Docker:
```
docker-compose exec web python manage.py fetch_surge_alerts
```

This command calls the same task that runs on the schedule but executes it immediately and displays the results.

## Development

### Project Structure

- `core/`: Main Django project
- `surge/`: App for handling surge alert data
- `users/`: App for user profiles and preferences

### Initial Setup

If you're setting up the project for the first time, you need to generate migrations for the custom apps:

With Docker:
```
docker-compose exec web python manage.py makemigrations surge users
docker-compose exec web python manage.py migrate
```

Locally:
```
# Option 1: Run the setup script
python setup.py
# or if you've made it executable:
./setup.py

# Option 2: Run the commands manually
python manage.py makemigrations surge users
python manage.py migrate
```

### Running Tests

With Docker:
```
docker-compose exec web python manage.py test
```

Locally:
```
python manage.py test
```

### Making Migrations

With Docker:
```
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

Locally:
```
python manage.py makemigrations
python manage.py migrate
```

## License

[MIT License](LICENSE)

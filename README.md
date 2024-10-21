# Financial Analysis Project

A Django-based application for fetching financial data, performing backtesting, and generating predictions using machine learning. This project is designed for advanced developers but aims to provide beginner-friendly setup instructions. The public site is accessible at http://18.118.206.231:8000

[Previous sections remain the same until Configuration]

## Configuration

There are two ways to run this project: locally for development or on AWS for production.

### Local Development Setup

1. Install PostgreSQL locally:
   ```sh
   # For Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # For MacOS using Homebrew
   brew install postgresql
   
   # For Windows, download from https://www.postgresql.org/download/windows/
   ```

2. Create a local database:
   ```sh
   sudo -u postgres psql
   CREATE DATABASE finance_db;
   CREATE USER your_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE finance_db TO your_user;
   ```

3. Create a `.env` file in the project root:
   ```sh
   # .env for local development
   DB_NAME=finance_db
   DB_USER=your_user
   DB_PASSWORD=your_password
   DB_HOST=localhost
   DB_PORT=5432
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
   DEBUG=True
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

### Production Setup (AWS)

For production, we use AWS RDS for the database. Create a different `.env` file:
```sh
# .env for production
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
DEBUG=False
ALLOWED_HOSTS=your-ec2-public-dns,your-domain.com
```

[Previous Database Management section remains the same]

## Deployment
This project is set up for deployment on AWS EC2 with RDS PostgreSQL, but can be adapted for other cloud providers.

### AWS RDS Setup
[Previous RDS setup steps remain the same until the Docker run command]

8. Build and run with Docker:
   ```sh
   docker build -t your-project-name .
   docker run -d --env-file .env -p 8000:8000 your-project-name
   ```

### Django Settings
Make sure your Django settings.py is configured to handle both local and production setups:

```python
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

# Database configuration that works for both local and production
if os.getenv('DATABASE_URL'):
    # Production setup with DATABASE_URL
    DATABASES = {
        'default': dj_database_url.config(
            default=os.getenv('DATABASE_URL'),
            conn_max_age=600
        )
    }
else:
    # Local setup with individual parameters
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
        }
    }
```

### Requirements
Add these to your requirements.txt:
```
django
psycopg2-binary
dj-database-url
python-dotenv
```

### Docker
For local testing with Docker:
1. Build the image:
   ```sh
   docker build -t your-project-name .
   ```
2. Run the container:
   ```sh
   docker run -p 8000:8000 --env-file .env your-project-name
   ```

### Important Notes
- Keep your database credentials secure and never commit them to version control
- Consider using AWS Secrets Manager for production credentials
- Make regular database backups
- Monitor your RDS metrics in AWS CloudWatch
- For production, set up proper SSL certificates and domain names
- The application runs on port 8000 in both local and production environments

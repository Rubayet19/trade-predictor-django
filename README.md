# Financial Analysis Project

A Django-based application for fetching financial data, performing backtesting, and generating predictions using machine learning. This project is designed for advanced developers but aims to provide beginner-friendly setup instructions. The public site is accessible at http://18.118.206.231:8000

## Features

- Fetch and store financial data from Alpha Vantage API
- Perform backtesting with customizable strategies
- Generate predictions using pre-trained machine learning models
- Create performance reports in PDF and JSON formats
- Dockerized setup for easy deployment

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Management](#database-management)
- [Usage](#usage)
- [Deployment](#deployment)


## Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- pip (Python package manager)
- PostgreSQL
- Docker (for containerization and deployment)

You'll also need an Alpha Vantage API key, which you can obtain for free at [Alpha Vantage](https://www.alphavantage.co/support/#api-key).

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/financial-analysis-project.git
   cd financial-analysis-project
   ```

2. Set up a virtual environment:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. Create a `.env` file in the project root:
   ```sh
   touch .env
   ```

2. Add the following environment variables to the `.env` file:
   ```
   DB_NAME=your_database_name
   DB_USER=your_database_user
   DB_PASSWORD=your_database_password
   DB_HOST=your_database_host
   DB_PORT=your_database_port
   ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
   ```

   Replace the placeholders with your actual database credentials and Alpha Vantage API key. For example:
   - `your_database_name` might be something like `finance_db`
   - `your_database_user` is typically `postgres` for local development
   - `your_database_password` should be a strong, unique password
   - `your_database_host` could be `localhost` for local development, or an AWS RDS endpoint for production
   - `your_database_port` is typically `5432` for PostgreSQL
   - `your_alpha_vantage_api_key` should be the API key you obtained from Alpha Vantage

3. Ensure your `.env` file is added to `.gitignore` to prevent it from being committed to your repository:
   ```sh
   echo ".env" >> .gitignore
   ```

4. For local development, you can use these environment variables in your Django settings like this:
   ```python
   import os
   from dotenv import load_dotenv

   load_dotenv()

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

   ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY')
   ```

5. For production deployment (e.g., on AWS), set these environment variables in your deployment environment rather than using a `.env` file.

Remember: Never commit your `.env` file or share your actual credentials publicly. The example above uses placeholders to demonstrate the structure of the file.

## Database Management

1. Apply migrations to set up the database schema:
   ```sh
   python manage.py migrate
   ```

2. (Optional) Create a superuser to access the Django admin interface:
   ```sh
   python manage.py createsuperuser
   ```

3. Seed the database with initial data:
   ```sh
   python manage.py seed_data
   ```
   Note: The `seed_data` command is a custom management command. If you haven't created it yet, you'll need to implement it in `yourapp/management/commands/seed_data.py`. Here's a basic example:

   ```python
   from django.core.management.base import BaseCommand
   from yourapp.models import YourModel

   class Command(BaseCommand):
       help = 'Seed the database with initial data'

       def handle(self, *args, **options):
           YourModel.objects.create(name="Example", value=100)
           self.stdout.write(self.style.SUCCESS('Successfully seeded the database'))
   ```

## Usage

Run the development server:
```sh
python manage.py runserver
```

Access the application at `http://localhost:8000`.

## Deployment
This project is set up for deployment on AWS EC2 with RDS PostgreSQL, but can be adapted for other cloud providers.

### AWS RDS Setup
1. Create a PostgreSQL RDS instance:
   - Go to AWS RDS Dashboard
   - Click "Create database"
   - Choose PostgreSQL
   - Select Free tier or your preferred tier
   - Set up these configurations:
     - DB instance identifier: `your-db-name`
     - Master username: `postgres` (or your preferred username)
     - Master password: Set a secure password
   - Under Connectivity:
     - Make sure it's in the same VPC as your EC2
     - Create new security group or use existing
     - Make it publicly accessible if needed for development

2. Configure RDS Security Group:
   - Go to the RDS security group
   - Add inbound rule:
     - Type: PostgreSQL
     - Port: 5432
     - Source: Your EC2 security group ID
     - Description: Allow EC2 access

3. Get your RDS endpoint:
   - Go to RDS Dashboard
   - Click on your database
   - Find the endpoint URL
   - Your DATABASE_URL will be: `postgresql://username:password@endpoint:5432/dbname`

### AWS EC2 Deployment
1. Install the AWS CLI:
   ```sh
   pip install awscli
   ```

2. Configure your AWS credentials:
   ```sh
   aws configure
   ```

3. Launch an EC2 instance:
   - Log into AWS Console
   - Go to EC2 Dashboard
   - Click "Launch Instance"
   - Choose Amazon Linux 2 AMI
   - Select instance type (t2.micro for testing)
   - Configure security groups to allow HTTP (80), HTTPS (443), and SSH (22)
   - Create or select an existing key pair
   - Make sure it's in the same VPC as your RDS

4. Connect to your EC2 instance:
   ```sh
   ssh -i /path/to/your-key-pair.pem ec2-user@your-instance-public-dns
   ```

5. Set up your instance:
   ```sh
   # Update system packages
   sudo yum update -y
   
   # Install Docker
   sudo yum install -y docker
   sudo service docker start
   sudo usermod -a -G docker ec2-user
   
   # Install Git
   sudo yum install -y git
   
   # Install PostgreSQL client (for database management if needed)
   sudo yum install -y postgresql15
   ```

6. Clone and deploy your project:
   ```sh
   git clone your-repository-url
   cd your-project-name
   ```

7. Set up environment variables:
   ```sh
   # Create a .env file
   cat << EOF > .env
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
   ALLOWED_HOSTS=your-ec2-public-dns,your-domain.com
   DEBUG=False
   EOF
   ```

8. Build and run with Docker:
   ```sh
   docker build -t your-project-name .
   docker run -d --env-file .env -p 80:8000 your-project-name
   ```

9. Run Django migrations:
   ```sh
   # Enter the Docker container
   docker exec -it $(docker ps -q) bash
   
   # Run migrations
   python manage.py migrate
   
   # Create superuser if needed
   python manage.py createsuperuser
   ```

### Django Settings
Make sure your Django settings.py is configured to use the DATABASE_URL:

```python
import os
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL'),
        conn_max_age=600
    )
}
```

### Requirements
Add these to your requirements.txt:
```
psycopg2-binary
dj-database-url
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

### CI/CD

This project uses GitHub Actions for CI/CD. The workflow is defined in `.github/workflows/main.yml`. It automates testing, building the Docker image, and deploying to AWS Elastic Beanstalk.

To set up:
1. Add your AWS credentials as secrets in your GitHub repository settings.
2. Push your code to GitHub to trigger the workflow.

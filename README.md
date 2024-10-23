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
- Python 3.1 or higher
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


## Initial Data Fetching

Before using any analysis features, populate the database with stock data:

```bash
# Fetch last 30 days of AAPL data
python manage.py fetch_stock_data AAPL --days 30

# Fetch 2 years of historical data (recommended for backtesting)
python manage.py fetch_stock_data AAPL --years 2

# Combine both parameters
python manage.py fetch_stock_data MSFT --years 1 --days 30
```

**Important Notes:**
- Required before running any analysis
- Alpha Vantage API rate limit: 5 requests/minute (free tier)
- Initial fetch may take several minutes
- Data is stored in PostgreSQL database

Verify data population:
```python
# In Django shell
python manage.py shell

from financial_data.models import StockData
# Check data count
StockData.objects.filter(symbol='AAPL').count()
# View latest entries
StockData.objects.filter(symbol='AAPL').order_by('-date')[:5]
```

## Running Backtests

Test trading strategies using historical data:

```bash
curl -X POST http://18.118.206.231:8000/financial_data/backtest/ \
-H "Content-Type: application/json" \
-d '{
    "symbol": "AAPL",
    "initial_investment": 10000,
    "buy_ma_window": 50,
    "sell_ma_window": 200
}'
```

Python example:
```python
import requests

response = requests.post(
    "http://18.118.206.231:8000/financial_data/backtest/",
    json={
        "symbol": "AAPL",
        "initial_investment": 10000,
        "buy_ma_window": 50,
        "sell_ma_window": 200
    }
)

result = response.json()
print(f"Final Portfolio Value: ${result['final_value']:,.2f}")
```

## Generating Predictions

Get stock price predictions:

```bash
curl http://18.118.206.231:8000/financial_data/predict/?symbol=AAPL
```

Python example:
```python
import requests

response = requests.get(
    "http://18.118.206.231:8000/financial_data/predict/",
    params={"symbol": "AAPL"}
)

predictions = response.json()
```

## Generating Reports

Create PDF reports with analysis and visualizations:

```bash
curl "http://18.118.206.231:8000/financial_data/report/?symbol=AAPL&start_date=2024-01-01&end_date=2024-01-31&initial_investment=10000&buy_ma_window=50&sell_ma_window=200" \
--output report.pdf
```

Python example:
```python
import requests

response = requests.get(
    "http://18.118.206.231:8000/financial_data/report/",
    params={
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-01-31",
        "initial_investment": 10000,
        "buy_ma_window": 50,
        "sell_ma_window": 200
    }
)

if response.status_code == 200:
    with open("report.pdf", "wb") as f:
        f.write(response.content)
```

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
   - Configure security groups to allow HTTP (80), HTTPS (443), SSH (22), and Custom TCP (8000)
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
   docker run -d --env-file .env -p 8000:8000 your-project-name
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
Make sure these are in your requirements.txt:
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

### CI/CD

This project uses GitHub Actions for CI/CD. The workflow automates testing, building the Docker image, and deploying to AWS EC2.

1. Create the following secrets in your GitHub repository (Settings > Secrets and variables > Actions):
   ```
   AWS_ACCESS_KEY_ID
   AWS_SECRET_ACCESS_KEY
   EC2_HOST             # Your EC2 public DNS or IP
   EC2_USERNAME         # Usually 'ec2-user' for Amazon Linux
   EC2_SSH_KEY          # Your EC2 private key for SSH
   ```

2. Create `.github/workflows/main.yml` in your repository:
   ```yaml
   name: CI/CD Pipeline

   on:
     push:
       branches: [ main ]
     pull_request:
       branches: [ main ]

   jobs:
     test:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         - name: Set up Python
           uses: actions/setup-python@v2
           with:
             python-version: '3.8'
         - name: Install dependencies
           run: |
             python -m pip install --upgrade pip
             pip install -r requirements.txt
         - name: Run tests
           run: |
             python manage.py test

     deploy:
       needs: test
       runs-on: ubuntu-latest
       if: github.ref == 'refs/heads/main'
       
       steps:
         - uses: actions/checkout@v2
         
         - name: Configure AWS credentials
           uses: aws-actions/configure-aws-credentials@v1
           with:
             aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
             aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
             aws-region: us-east-2  # Change to your AWS region

         - name: Build Docker image
           run: |
             docker build -t financial-analysis .
             docker save financial-analysis > financial-analysis.tar

         - name: Copy Docker image to EC2
           uses: appleboy/scp-action@master
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ${{ secrets.EC2_USERNAME }}
             key: ${{ secrets.EC2_SSH_KEY }}
             source: "financial-analysis.tar"
             target: "/home/ec2-user"

         - name: Deploy to EC2
           uses: appleboy/ssh-action@master
           with:
             host: ${{ secrets.EC2_HOST }}
             username: ${{ secrets.EC2_USERNAME }}
             key: ${{ secrets.EC2_SSH_KEY }}
             script: |
               # Load the Docker image
               docker load < /home/ec2-user/financial-analysis.tar
               
               # Stop existing container
               docker stop $(docker ps -q) || true
               docker rm $(docker ps -a -q) || true
               
               # Run new container
               docker run -d \
                 --env-file /home/ec2-user/financial-analysis-project/.env \
                 -p 8000:8000 \
                 financial-analysis
               
               # Cleanup
               rm /home/ec2-user/financial-analysis.tar
   ```

3. Make sure your EC2 instance has Docker installed and running:
   ```sh
   sudo systemctl status docker
   ```

4. Ensure your EC2 security group allows inbound traffic on port 8000.

5. Store your production environment variables in `/home/ec2-user/financial-analysis-project/.env` on the EC2 instance.

The workflow will:
1. Run tests when you push code or create a pull request
2. On successful merge to main:
   - Build a Docker image
   - Copy the image to your EC2 instance
   - Deploy the new version
   - Clean up old containers and images


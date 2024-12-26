# Financial Analysis Project

A Django-based application for financial data analysis, backtesting, and machine learning predictions. You can run this locally or deploy it to AWS. A demo version is currently hosted and accessible via example API endpoints.

# Features

* Fetch and store financial data from Alpha Vantage API
* Perform backtesting with customizable strategies
* Generate predictions using pre-trained machine learning models
* Create performance reports in PDF and JSON formats
* Dockerized setup for easy deployment

# Quick Start

## Prerequisites

* Python 3.1+
* pip (Python package manager)
* PostgreSQL
* Docker
* Alpha Vantage API key ([Alpha Vantage](https://www.alphavantage.co/support/#api-key))

## Local Setup

1. Clone and install:
```sh
git clone https://github.com/yourusername/financial-analysis-project.git
cd financial-analysis-project

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

2. Create `.env` file:
```sh
DATABASE_URL=postgresql://localhost:5432/dbname
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

3. Setup database:
```sh
python manage.py migrate
python manage.py createsuperuser  # Optional: for admin access
```

# Working with Stock Data

## Fetching Data
Before running any analysis, you need to fetch stock data:

```bash
# Fetch last 30 days of data
python manage.py fetch_stock_data AAPL --days 30

# Fetch 2 years of historical data (recommended for backtesting)
python manage.py fetch_stock_data AAPL --years 2
```

**Important Notes:**
* Required before running analysis
* Alpha Vantage API rate limit: 5 requests/minute (free tier)
* Initial fetch may take several minutes

## Training Models
For predictions, train a model for each stock symbol:
```bash
python manage.py train_ml_model AAPL
```

# Example API Usage

A demo version is hosted at `3.130.162.114:8000`. You can test the functionality using these curl commands:

## Backtesting Example
```bash
curl -X POST http://3.130.162.114:8000/financial_data/backtest/ \
-H "Content-Type: application/json" \
-d '{
    "symbol": "AAPL",
    "initial_investment": 10000,
    "buy_ma_window": 50,
    "sell_ma_window": 200
}'
```

## Predictions Example
```bash
curl http://3.130.162.114:8000/financial_data/predict/?symbol=AAPL
```

## Report Generation Example
```bash
curl -X POST -H "Content-Type: application/json" \
-d '{
    "symbol": "AAPL",
    "start_date": "2024-11-01",
    "end_date": "2024-12-01",
    "initial_investment": 10000,
    "buy_ma_window": 5,
    "sell_ma_window": 20,
    "format": "pdf"
}' \
http://3.130.162.114:8000/financial_data/report/ --output AAPL_report.pdf
```

A report similar to this will be generated:
![image](https://github.com/user-attachments/assets/57fdc16d-469a-4d59-82ea-9ea29634af51)



**Note:** Replace `3.130.162.114` with your own server's IP address when you deploy your instance.

# Optional: AWS Deployment

If you want to deploy your own instance, follow these steps:

## AWS RDS Setup

1. Create PostgreSQL RDS instance:
   * Go to AWS RDS Dashboard
   * Click "Create database"
   * Choose PostgreSQL
   * Select Free tier or preferred tier
   * Configure instance details and connectivity

2. Configure Security Group:
   * Add inbound rule for PostgreSQL (port 5432)
   * Source: Your EC2 security group ID

## AWS EC2 Setup

1. Launch EC2 instance:
   * Choose Amazon Linux 2 AMI
   * Select instance type
   * Configure security groups (ports 22, 80, 443, 8000)
   * Create/select key pair

2. Install requirements:
```sh
sudo yum update -y
sudo yum install -y docker git postgresql15
sudo service docker start
sudo usermod -a -G docker ec2-user
```

3. Deploy application:
```sh
# Clone your repository
git clone your-repository-url
cd your-project-name

# Create production .env
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/dbname
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
DEBUG=False
ALLOWED_HOSTS=your-ec2-public-dns,your-domain.com

# Deploy with Docker
docker build -t financial-analysis .
docker run -d --env-file .env -p 8000:8000 financial-analysis
```

Once deployed, you can use the same API endpoints shown in the examples above, replacing `3.130.162.114` with your EC2 instance's public IP.

# CI/CD Configuration (Optional)

If you want to set up automatic deployments, see the CI/CD configuration in `.github/workflows/main.yml` in the repository. Required GitHub secrets:
```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
EC2_HOST
EC2_USERNAME
EC2_SSH_KEY
```

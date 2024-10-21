# Financial Analysis Project

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Django](https://img.shields.io/badge/django-3.2+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

A Django-based application for fetching financial data, performing backtesting, and generating predictions using machine learning.

## Features

- Fetch and store financial data from Alpha Vantage API
- Perform backtesting with customizable strategies
- Generate predictions using pre-trained machine learning models
- Create performance reports in PDF and JSON formats
- Dockerized setup for easy deployment

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Database Management](#database-management)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

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

4. Set up environment variables:
   Create a `.env` file in the project root with the following:
   ```
   DEBUG=True
   SECRET_KEY=your_secret_key
   DATABASE_URL=postgresql://user:password@localhost/dbname
   ALPHA_VANTAGE_API_KEY=your_api_key
   ```

5. Apply migrations:
   ```sh
   python manage.py migrate
   ```

## Usage

Run the development server:
```sh
python manage.py runserver
```

Access the application at `http://localhost:8000`.

## Database Management

### Migrations

Apply migrations:
```sh
python manage.py migrate
```

Create new migrations:
```sh
python manage.py makemigrations
```

### Seeding Data

To seed the database:
```sh
python manage.py seed_data
```

## Deployment

### AWS Deployment

1. Set up an AWS account and configure the AWS CLI.

2. Create an RDS PostgreSQL instance.

3. Set up Elastic Beanstalk:
   ```sh
   eb init -p docker your-project-name
   eb create your-environment-name
   ```

4. Set environment variables:
   ```sh
   eb setenv SECRET_KEY=your_secret_key DATABASE_URL=your_rds_url ALPHA_VANTAGE_API_KEY=your_api_key
   ```

5. Deploy:
   ```sh
   eb deploy
   ```

### Docker

Build the image:
```sh
docker build -t financial-analysis-project .
```

Run the container:
```sh
docker run -p 8000:8000 financial-analysis-project
```

### CI/CD

This project uses GitHub Actions for CI/CD. The workflow is defined in `.github/workflows/main.yml`.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

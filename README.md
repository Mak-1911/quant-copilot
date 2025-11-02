# Quant-Copilot

## Description
Quant Copilot is an innovative platform that leverages large language models (LLMs) to transform natural language trading strategy descriptions into executable Python code. The platform uses frameworks like **BackTrader** and **Vectorbt** for strategy execution and backtesting.

## Key Features
- **Strategy Generation**: Convert natural language to Python trading strategies
- **Visual Strategy Builder**: Drag-and-drop interface for strategy creation
- **Automated Backtesting**: Test strategies against historical data
- **Performance Analytics**: Detailed metrics and visualizations
- **Strategy Explanations**: AI-powered strategy documentation
- **Paper Trading**: Test strategies in real-time with virtual money
- **Leaderboard System**: Compare and rank strategy performance

## Tech Stack
- **Backend**: FastAPI
- **Database**: PostgreSQL with SQLModel ORM
- **Cache**: Redis
- **Authentication**: JWT with Email OTP
- **LLM Integration**: Google Gemini
- **Backtesting Engine**: Backtrader
- **Data Source**: Yahoo Finance
- **Package Management**: Poetry

## Installation

### Prerequisites
```bash
Python 3.9+
PostgreSQL
Redis
Poetry
```

### Setup
1. Clone the repository:
```bash
git clone https://github.com/yourusername/quant-copilot.git
cd quant-copilot
```

2. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. Install dependencies using Poetry:
```bash
poetry install
```

4. Set up environment variables:
```bash
# Create .env file
POSTGRES_URL=postgresql://user:password@localhost:5432/dbname
REDIS_URL=redis://localhost:6379
JWT_SECRET=your_jwt_secret
GEMINI_API_KEY=your_gemini_api_key
```

5. Initialize the database:
```bash
poetry run alembic upgrade head
```

### Running the Application
```bash
poetry run uvicorn app.main:app --reload
```

### Running Tests
```bash
poetry run pytest
```

## Project Structure
```
quant-copilot/
├── app/
│   ├── models/          # SQLModel definitions
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   └── utility/         # Helper functions
├── tests/              # Test suite
├── alembic/            # Database migrations
├── pyproject.toml      # Poetry configuration
└── poetry.lock         # Dependency lock file
```

## Development

### Adding Dependencies
```bash
poetry add package-name
poetry add package-name --dev  # for development dependencies
```

### Updating Dependencies
```bash
poetry update
```

### Creating a New Migration
```bash
poetry run alembic revision --autogenerate -m "migration description"
```

## API Documentation
Access the API documentation at `http://localhost:8000/docs` after starting the server.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Open a pull request

## License
This project is licensed under the MIT License - see the LICENSE file for details.


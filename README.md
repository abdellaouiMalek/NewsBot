# NewsBot AI - FastAPI Project

A professional FastAPI application with MongoDB integration for feed extraction and news bot functionality.

## Project Structure

```
project/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── routes.py
│   │       └── routes/
│   │           ├── __init__.py
│   │           ├── articles.py
│   │           ├── bot.py
│   │           └── health.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── enums.py
│   │   ├── article.py
│   │   └── session.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── article.py
│   │   └── message.py
│   └── services/
│       ├── __init__.py
│       ├── article_service.py
│       └── bot_service.py
├── main.py
├── requirements.txt
├── env.template
├── docker-compose.yml
├── Makefile
└── README.md
```

## Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **MongoDB Integration**: Async MongoDB connection using Motor
- **Feed Extraction**: Article management from RSS feeds, scraping, and APIs
- **Pydantic Models**: Data validation and serialization
- **Professional Structure**: Clean, scalable folder organization
- **Type Hints**: Full type annotation support
- **Environment Configuration**: Configurable settings via environment variables
- **API Documentation**: Automatic OpenAPI/Swagger documentation

## API Endpoints

### Articles (Feed Extraction)

- `GET /api/v1/articles` - Get articles with filtering
- `GET /api/v1/articles/{article_id}` - Get specific article by MongoDB ObjectId
- `GET /api/v1/articles/by-article-id/{article_id}` - Get specific article by custom article_id
- `POST /api/v1/articles` - Create new article from feed extraction
- `PUT /api/v1/articles/{article_id}` - Update article
- `DELETE /api/v1/articles/{article_id}` - Delete article
- `GET /api/v1/articles/source/{source_name}` - Get articles by source
- `GET /api/v1/articles/search/{query}` - Search articles

### Bot

- `POST /api/v1/bot/message` - Send message to bot
- `GET /api/v1/bot/sessions/{session_id}/messages` - Get session messages

### Health

- `GET /api/v1/health` - Health check

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- pip (Python package manager)

### Installation

1. **Clone or navigate to the project directory:**

   ```bash
   cd /home/ibrahim/Desktop/NewsBotAI/project
   ```

2. **Create a virtual environment:**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**

   ```bash
   cp env.template .env
   ```

   Edit `.env` file with your configuration:

   ```
   ENV=dev
   MONGO_URI=mongodb://NewsBotAI:secret@localhost:27017/newsbotdb?authSource=admin
   MONGO_DB=newsbotdb
   DEBUG=True
   ```

5. **Start MongoDB with Docker:**

   ```bash
   # Start MongoDB and Mongo Express
   make up

   # Or start only MongoDB
   make up-mongodb

   # Or use docker compose directly
   docker compose --env-file .env up -d
   ```

6. **Verify MongoDB is running:**

   ```bash
   # Check URLs
   make urls

   # Check MongoDB logs
   make logs-mongodb

   # Connect to MongoDB shell
   make db-shell
   ```

7. **Run the application:**

   ```bash
   # Dev mode (auto-reload)
   make run-dev

   # Or normal mode
   make run

   # Or directly via python
   python main.py

   # Or directly via uvicorn
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

8. **Access the services:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/api/v1/docs
   - ReDoc: http://localhost:8000/api/v1/redoc
   - Mongo Express: http://localhost:8081 (admin/admin)

### Docker Management

Use the provided Makefile for easy Docker management:

```bash
# Start all services
make up

# Stop all services
make down

# Restart all services
make restart

# View logs
make logs-mongodb
make logs-mongoexp

# Connect to MongoDB shell
make db-shell

# Show available URLs
make urls

# Get help
make help
```

## Development

### Code Quality Tools

The project includes several code quality tools:

```bash
# Format code
black .

# Sort imports
isort .

# Lint code
flake8 .
```

### Testing

```bash
# Run tests (when implemented)
pytest
```

## Configuration

The application uses environment variables for configuration. Key settings:

- `ENV`: Environment (dev/prod)
- `MONGO_URI`: MongoDB connection string with authentication
- `MONGO_DB`: Database name
- `MONGO_INITDB_ROOT_USERNAME`: Root username for admin tasks
- `MONGO_INITDB_ROOT_PASSWORD`: Root password for admin tasks
- `MONGO_EXPRESS_USER`: Mongo Express username (optional)
- `MONGO_EXPRESS_PASSWORD`: Mongo Express password (optional)
- `MONGO_EXPRESS_PORT`: Mongo Express port (optional)
- `DEBUG`: Enable debug mode
- `SECRET_KEY`: Secret key for JWT tokens (future use)

## Database Models

### Article

- Articles from feed extraction with title, content, summary, author, source, etc.
- Support for tags, categories, sentiment analysis, and embeddings
- Multiple fetch methods: RSS, scraping, API, manual
- Timestamps for publication and fetching
- Raw data storage for processing

### NewsBotSession

- Bot conversation sessions
- Message history and context
- Session expiration

## Services

- **ArticleService**: Manages articles from feed extraction with CRUD operations
- **BotService**: Manages bot interactions and sessions

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in environment
2. Use a strong `SECRET_KEY`
3. Configure proper CORS origins
4. Use a production MongoDB instance
5. Set up proper logging
6. Use a reverse proxy (nginx)
7. Consider using Docker for containerization

## Contributing

1. Follow the existing code structure
2. Use type hints
3. Add proper error handling
4. Write tests for new features
5. Update documentation

## License

This project is part of the NewsBot AI system.

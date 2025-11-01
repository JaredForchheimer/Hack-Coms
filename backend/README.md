# ASL Summarizer Backend API

A Flask-based backend API for the ASL Summarizer application that provides content scraping, validation, summarization, and database storage capabilities.

## Features

- **Content Scraping**: Extract text from news articles and YouTube videos
- **AI Content Validation**: Use Claude API to validate content for inappropriate material
- **AI Summarization**: Generate summaries using Claude API
- **Database Integration**: Store and retrieve sources and summaries using PostgreSQL
- **RESTful API**: Clean API endpoints for frontend integration
- **Error Handling**: Comprehensive error handling and logging
- **Security**: Input validation, CORS support, and secure configurations

## Technology Stack

- **Framework**: Flask 2.3.3
- **AI/LLM**: Anthropic Claude API
- **Database**: PostgreSQL with custom ORM
- **Web Scraping**: BeautifulSoup4, YouTube Transcript API
- **Validation**: Custom validators and sanitizers
- **Configuration**: Environment-based configuration

## Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL database
- Anthropic Claude API key

### Installation

1. **Clone and Navigate**
   ```bash
   cd backend
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Setup**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Database Setup**
   ```bash
   # Initialize database (run from parent directory)
   python database_handler/scripts/init_db.py
   ```

5. **Start Server**
   ```bash
   python run.py
   ```

The server will start at `http://localhost:5000`

## Environment Configuration

Create a `.env` file with the following variables:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Anthropic Claude API
ANTHROPIC_API_KEY=your_claude_api_key_here

# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=asl_summarizer
DB_USER=postgres
DB_PASSWORD=your_password_here

# Frontend Configuration
FRONTEND_URL=http://localhost:5173
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## API Endpoints

### Health Check
- `GET /health/` - Overall health check
- `GET /health/database` - Database health check
- `GET /health/claude` - Claude API health check

### Media Processing
- `POST /api/media/extract-url` - Extract content from URL
- `POST /api/media/process-file` - Process uploaded file
- `POST /api/media/validate` - Validate content with Claude
- `POST /api/media/summarize` - Generate summary and store in database

### Data Retrieval
- `GET /api/sources` - Get all text sources
- `GET /api/summaries` - Get all summaries
- `GET /api/sources/{id}` - Get specific source
- `GET /api/summaries/{id}` - Get specific summary
- `GET /api/statistics` - Get application statistics

## API Usage Examples

### Extract URL Content
```bash
curl -X POST http://localhost:5000/api/media/extract-url \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

### Generate Summary
```bash
curl -X POST http://localhost:5000/api/media/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Article content here...",
    "title": "Article Title",
    "source_data": {
      "type": "article",
      "url": "https://example.com/article"
    }
  }'
```

### Get Summaries
```bash
curl http://localhost:5000/api/summaries
```

## Project Structure

```
backend/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration management
│   ├── routes/
│   │   ├── api.py               # Main API endpoints
│   │   └── health.py            # Health check endpoints
│   ├── services/
│   │   ├── scraping_service.py  # Content scraping
│   │   ├── claude_service.py    # Claude AI integration
│   │   ├── media_service.py     # Main business logic
│   │   └── database_service.py  # Database operations
│   └── utils/
│       ├── validators.py        # Input validation
│       └── exceptions.py        # Custom exceptions
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment template
├── run.py                       # Application entry point
└── README.md                    # This file
```

## Content Processing Workflow

1. **URL/File Upload**: User submits URL or file
2. **Content Extraction**: Scrape text from source
3. **Validation**: Claude validates content for inappropriate material
4. **Review**: User reviews validation results
5. **Summarization**: Claude generates summary if accepted
6. **Storage**: Store source and summary in database
7. **Retrieval**: Frontend displays stored data

## Supported Content Types

### URLs
- News articles and blog posts
- YouTube videos (with transcripts)
- General web content

### Files
- PDF documents
- Text files (.txt, .md)

## Content Validation

The system uses Claude AI to check content for:
- Pornography
- Profanity
- Hate speech
- Discrimination
- Racism
- Political bias

## Error Handling

The API provides detailed error responses:

```json
{
  "success": false,
  "error": "Error description",
  "type": "ValidationError",
  "field": "specific_field"
}
```

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python run.py
```

### Testing API Endpoints
Use the health check endpoint to verify setup:
```bash
curl http://localhost:5000/health/
```

### Database Management
The database handler is located in the parent directory and provides:
- Automatic table creation
- Connection pooling
- Transaction support
- Data validation

### Logging
Logs are output to console in development mode. Configure logging levels in `config.py`.

## Production Deployment

### Environment Configuration
```env
FLASK_ENV=production
FLASK_DEBUG=False
```

### Security Considerations
- Set strong `SECRET_KEY`
- Configure proper CORS origins
- Use HTTPS in production
- Secure database credentials
- Rotate API keys regularly

### Performance Optimization
- Connection pooling is enabled by default
- Adjust `DB_POOL_SIZE` and `DB_MAX_OVERFLOW` for your needs
- Monitor API response times
- Consider caching for frequently accessed data

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify database credentials
   - Ensure database exists

2. **Claude API Error**
   - Check API key is set correctly
   - Verify API key has sufficient credits
   - Check internet connectivity

3. **Import Errors**
   - Ensure all dependencies are installed
   - Check Python path configuration
   - Verify database_handler is accessible

### Debug Mode
Enable debug logging:
```env
FLASK_DEBUG=True
```

### Health Checks
Monitor service health:
- `/health/` - Overall status
- `/health/database` - Database connectivity
- `/health/claude` - Claude API status

## Contributing

1. Follow the existing code structure
2. Add comprehensive error handling
3. Include input validation
4. Update documentation
5. Test with provided examples

## License

This project is provided as-is for development purposes.
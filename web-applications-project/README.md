# Web Applications Project

> **Part of [Python AI Course](../README.md)** - A comprehensive learning repository covering AI, algorithms, and real-world applications.  
> See also: [AI Development Project](../ai-development-project/) | [Fintech Tools](../fintech-tools/) | [Yelp-Style AI Assistant](../yelp-ai-assistant/)

A collection of web application examples demonstrating different Python web frameworks and features.

## Overview

This project contains multiple web application examples built with Flask and FastAPI, showcasing different features like keyword processing, Elasticsearch integration, and blog management systems.

## Project Structure

```
web-applications-project/
├── flask-app/             # Flask applications
│   ├── keyword_processor.py  # Flask app with keyword processing
│   ├── elasticsearch_app.py  # Flask app with Elasticsearch
│   └── templates/            # HTML templates (if needed)
├── fastapi-blog/          # FastAPI blog application
│   ├── blog_api.py           # Complete blog API with SQLAlchemy
│   └── models/              # Database models
├── tests/                 # Unit tests for all applications
├── requirements.txt       # Dependencies for all apps
└── README.md             # This file
```

## Applications Included

### Flask Applications

#### 1. Keyword Processor (`flask-app/keyword_processor.py`)
- **Features**: Text processing with hashtag addition
- **Endpoints**: 
  - `POST /process` - Process text and add hashtags
  - `POST /keyword` - Add new keywords
- **Storage**: File-based keyword storage

#### 2. Elasticsearch Integration (`flask-app/elasticsearch_app.py`)
- **Features**: Advanced text processing with Elasticsearch
- **Dependencies**: Requires Elasticsearch server
- **Enhanced**: Search and indexing capabilities

### FastAPI Applications

#### 1. Blog API (`fastapi-blog/blog_api.py`)
- **Features**: Complete blog management system
- **Database**: SQLite with SQLAlchemy ORM
- **Operations**: CRUD operations for blog posts
- **Schema**: Pydantic models for request/response validation
- **Features**:
  - Create, read, update, delete blog posts
  - Image URL support
  - Database persistence
  - API documentation (automatic with FastAPI)

## Installation

```bash
cd web-applications-project
pip install -r requirements.txt
```

### For Elasticsearch App (optional)
```bash
# Install and start Elasticsearch locally
# Or use Docker:
docker run -d --name elasticsearch -p 9200:9200 -e "discovery.type=single-node" elasticsearch:7.14.0
```

## Usage

### Flask Keyword Processor
```bash
cd flask-app
python keyword_processor.py

# Test endpoints:
curl -X POST http://localhost:5000/process -H 'Content-Type: application/json' -d '{"text": "Let us focus on eating more natural and artificial products."}'
curl -X POST http://localhost:5000/keyword -H 'Content-Type: application/json' -d '{"keyword": "healthy"}'
```

### Flask Elasticsearch App
```bash
cd flask-app
python elasticsearch_app.py

# Similar endpoints with enhanced search capabilities
```

### FastAPI Blog API
```bash
cd fastapi-blog
python blog_api.py

# Visit http://localhost:8000/docs for interactive API documentation
# API endpoints:
# GET /blogposts/ - List all posts
# POST /blogposts/ - Create new post
# GET /blogposts/{id} - Get specific post
# PUT /blogposts/{id} - Update post
# DELETE /blogposts/{id} - Delete post
```

## Testing

```bash
# Run all tests
python -m pytest tests/

# Test specific application
python -m pytest tests/test_flask_apps.py
python -m pytest tests/test_fastapi_blog.py
```

## Educational Value

This project demonstrates:
- **Flask vs FastAPI**: Compare different Python web frameworks
- **Database Integration**: SQLAlchemy ORM usage
- **API Design**: RESTful API principles
- **Request/Response Handling**: JSON processing
- **Search Integration**: Elasticsearch usage
- **Testing**: Unit testing web applications

## API Examples

### Flask Keyword Processor
```python
# Add keyword
POST /keyword
{
    "keyword": "artificial"
}

# Process text
POST /process
{
    "text": "Explore natural solutions and artificial intelligence."
}
```

### FastAPI Blog
```python
# Create blog post
POST /blogposts/
{
    "title": "My First Post",
    "content": "This is the content of my blog post.",
    "image_url": "https://example.com/image.jpg"
}

# Get all posts
GET /blogposts/
```

## Requirements

- Python 3.7+
- Flask 2.0+ (for Flask apps)
- FastAPI 0.68+ (for FastAPI apps)
- SQLAlchemy 1.4+ (for database operations)
- Pydantic (for data validation)
- Elasticsearch (optional, for search features)

## Contributing

Feel free to add new web application examples, improve existing features, or enhance test coverage!
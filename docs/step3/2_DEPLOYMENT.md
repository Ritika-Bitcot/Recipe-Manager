# Recipe Manager - Deployment Guide

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- PostgreSQL 12+ (for production)
- Git
- Virtual environment (venv, conda, or pipenv)

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Recipe-Manager
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements/requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   alembic upgrade head
   ```

6. **Run the application**
   ```bash
   python -m src.api.app
   ```

## 🔧 Environment Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/recipe_manager

# Security
SECRET_KEY=your-super-secret-key-here

# CORS Configuration
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Environment
ENVIRONMENT=development

# Logging
LOG_LEVEL=INFO
LOG_FILE=app.log
LOG_FORMAT=%(levelname)-8s %(asctime)s %(name)s.%(module)s:%(lineno)s | %(message)s
LOG_BODY=false

# JWT Configuration
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Caching
CACHE_TTL=300
ENABLE_CACHE=true
```

### Environment-specific Configuration

#### Development Environment
```bash
ENVIRONMENT=development
DATABASE_URL=postgresql://dev_user:dev_pass@localhost:5432/recipe_manager_dev
LOG_LEVEL=DEBUG
ENABLE_CACHE=true
```

#### Testing Environment
```bash
ENVIRONMENT=testing
DATABASE_URL=sqlite:///test.db
LOG_LEVEL=WARNING
ENABLE_CACHE=false
```

#### Production Environment
```bash
ENVIRONMENT=production
DATABASE_URL=postgresql://prod_user:prod_pass@prod-db:5432/recipe_manager_prod
LOG_LEVEL=INFO
ENABLE_CACHE=true
```

## 🗄️ Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install postgresql postgresql-contrib
   
   # macOS (with Homebrew)
   brew install postgresql
   
   # Windows
   # Download from https://www.postgresql.org/download/windows/
   ```

2. **Create database and user**
   ```sql
   -- Connect to PostgreSQL as superuser
   sudo -u postgres psql
   
   -- Create database
   CREATE DATABASE recipe_manager;
   
   -- Create user
   CREATE USER recipe_user WITH PASSWORD 'secure_password';
   
   -- Grant privileges
   GRANT ALL PRIVILEGES ON DATABASE recipe_manager TO recipe_user;
   
   -- Exit
   \q
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# Check current migration status
alembic current

# View migration history
alembic history
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "-m", "src.api.app"]
```

### Docker Compose

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://recipe_user:secure_password@db:5432/recipe_manager
      - SECRET_KEY=your-super-secret-key-here
      - ENVIRONMENT=production
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=recipe_manager
      - POSTGRES_USER=recipe_user
      - POSTGRES_PASSWORD=secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### Docker Commands

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Stop services
docker-compose down

# Remove volumes (WARNING: This will delete all data)
docker-compose down -v
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Using AWS Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize EB application**
   ```bash
   eb init
   ```

3. **Create environment**
   ```bash
   eb create production
   ```

4. **Deploy application**
   ```bash
   eb deploy
   ```

#### Using AWS ECS with Fargate

1. **Create ECS cluster**
2. **Create task definition**
3. **Create service**
4. **Configure load balancer**

### Google Cloud Platform

#### Using Cloud Run

1. **Build and push container**
   ```bash
   gcloud builds submit --tag gcr.io/PROJECT_ID/recipe-manager
   ```

2. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy recipe-manager \
     --image gcr.io/PROJECT_ID/recipe-manager \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

### Heroku Deployment

1. **Install Heroku CLI**
2. **Create Heroku app**
   ```bash
   heroku create recipe-manager-api
   ```

3. **Set environment variables**
   ```bash
   heroku config:set DATABASE_URL=postgresql://...
   heroku config:set SECRET_KEY=your-secret-key
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

## 🔒 Production Security

### Security Checklist

- [ ] **HTTPS**: Enable SSL/TLS encryption
- [ ] **Secret Management**: Use secure secret management
- [ ] **Database Security**: Secure database connections
- [ ] **CORS**: Configure appropriate CORS policies
- [ ] **Rate Limiting**: Implement rate limiting
- [ ] **Input Validation**: Validate all inputs
- [ ] **Error Handling**: Don't expose sensitive information
- [ ] **Logging**: Implement security logging
- [ ] **Updates**: Keep dependencies updated
- [ ] **Monitoring**: Set up security monitoring

### Environment Security

```bash
# Use strong secret keys
SECRET_KEY=$(openssl rand -hex 32)

# Use environment-specific databases
DATABASE_URL=postgresql://user:password@secure-db-host:5432/recipe_manager_prod

# Restrict CORS origins
ALLOWED_ORIGINS=["https://yourdomain.com", "https://api.yourdomain.com"]

# Enable production logging
LOG_LEVEL=INFO
```

## 📊 Monitoring & Logging

### Application Monitoring

```python
# Add to your application
import logging
from flask import request
import time

@app.before_request
def log_request_info():
    logging.info(f"Request: {request.method} {request.url}")
    logging.info(f"Headers: {dict(request.headers)}")

@app.after_request
def log_response_info(response):
    logging.info(f"Response: {response.status_code}")
    return response
```

### Health Checks

```bash
# Basic health check
curl http://localhost:5000/health

# Readiness check
curl http://localhost:5000/health/ready
```

### Log Management

```bash
# View application logs
tail -f logs/app.log

# View error logs
grep "ERROR" logs/app.log

# View access logs
grep "INFO" logs/app.log | grep "Request:"
```


## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check database connectivity
psql $DATABASE_URL

# Check database status
sudo systemctl status postgresql

# Restart database
sudo systemctl restart postgresql
```

#### Application Startup Issues
```bash
# Check Python version
python --version

# Check dependencies
pip list

# Check environment variables
env | grep DATABASE_URL

# Run with debug mode
FLASK_DEBUG=1 python -m src.api.app
```

#### Migration Issues
```bash
# Check migration status
alembic current

# Check migration history
alembic history

# Reset migrations (WARNING: Data loss)
alembic downgrade base
alembic upgrade head
```

### Performance Issues

#### Database Performance
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check database size
SELECT pg_size_pretty(pg_database_size('recipe_manager'));

-- Check table sizes
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

#### Application Performance
```bash
# Monitor memory usage
ps aux | grep python

# Monitor CPU usage
top -p $(pgrep -f "python.*src.api.app")

# Check open files
lsof -p $(pgrep -f "python.*src.api.app")
```

## 📈 Scaling Considerations

### Horizontal Scaling

1. **Load Balancer**: Use nginx or AWS ALB
2. **Multiple Instances**: Run multiple app instances
3. **Database Connection Pooling**: Use pgbouncer
4. **Caching**: Implement Redis for caching
5. **CDN**: Use CloudFront or similar for static assets

### Vertical Scaling

1. **Memory**: Increase RAM for better caching
2. **CPU**: Use more powerful instances
3. **Storage**: Use SSD storage for database
4. **Network**: Use high-bandwidth connections

## 🔧 Maintenance

### Regular Tasks

1. **Database Backups**: Daily automated backups
2. **Log Rotation**: Rotate logs to prevent disk full
3. **Security Updates**: Keep dependencies updated
4. **Monitoring**: Check application health
5. **Performance**: Monitor and optimize queries

### Backup Strategy

```bash
# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from backup
psql $DATABASE_URL < backup_20240115_120000.sql
```

This deployment guide provides comprehensive instructions for setting up, deploying, and maintaining the Recipe Manager application in various environments.

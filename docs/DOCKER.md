# Docker Setup for Recipe Manager API

This document provides comprehensive instructions for running the Recipe Manager API using Docker and Docker Compose.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)

## Quick Start

### Production Environment

1. **Build and start all services:**
   ```bash
   docker-compose up -d
   ```

2. **Check service status:**
   ```bash
   docker-compose ps
   ```

3. **View logs:**
   ```bash
   docker-compose logs -f app
   ```

4. **Stop services:**
   ```bash
   docker-compose down
   ```

### Development Environment

1. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **View development logs:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f app
   ```

## Services Overview

### Production Services (`docker-compose.yml`)

| Service | Port | Description |
|---------|------|-------------|
| `app` | 5000 | Flask application |
| `db` | 5432 | PostgreSQL database |
| `redis` | 6379 | Redis cache |

### Development Services (`docker-compose.dev.yml`)

| Service | Port | Description |
|---------|------|-------------|
| `app` | 5001 | Flask application (with hot reload) |
| `db` | 5433 | PostgreSQL database |
| `redis` | 6380 | Redis cache |

## Configuration

### Environment Variables

The application uses environment variables for configuration. Key variables include:

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask secret key for sessions
- `ALLOWED_ORIGINS`: CORS allowed origins
- `ENVIRONMENT`: Application environment (development/production)
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

### Database Configuration

The PostgreSQL database is configured with:
- Database: `recipe`
- User: `postgres`
- Password: `password`
- Port: `5432` (production) / `5433` (development)

### Redis Configuration

Redis is configured for caching:
- Port: `6379` (production) / `6380` (development)
- No authentication required for development

## Docker Commands

### Building Images

```bash
# Build the application image
docker build -t recipe-manager .

# Build with specific tag
docker build -t recipe-manager:latest .
```

### Running Containers

```bash
# Run in production mode
docker-compose up -d

# Run in development mode
docker-compose -f docker-compose.dev.yml up -d

# Run with specific services
docker-compose up -d db redis
```

### Database Operations

```bash
# Run database migrations
docker-compose exec app python -m flask db upgrade

# Create new migration
docker-compose exec app python -m flask db migrate -m "Description"

# Access database shell
docker-compose exec db psql -U postgres -d recipe
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs app
docker-compose logs db

# Follow logs in real-time
docker-compose logs -f app

# View container status
docker-compose ps
```

### Health Checks

```bash
# Check application health
curl http://localhost:5000/health

# Check database connectivity
docker-compose exec app python -c "from src.core.database import db; print('DB connected:', db.engine.url)"

# Check Redis connectivity
docker-compose exec redis redis-cli ping
```

## Development Workflow

### Hot Reload Development

1. **Start development environment:**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Make code changes** - the application will automatically reload

3. **View logs:**
   ```bash
   docker-compose -f docker-compose.dev.yml logs -f app
   ```

### Running Tests

```bash
# Run tests in container
docker-compose exec app python -m pytest tests/

# Run tests with coverage
docker-compose exec app python -m pytest tests/ --cov=src

# Run specific test file
docker-compose exec app python -m pytest tests/test_auth_routes.py
```

### Database Migrations

```bash
# Create new migration
docker-compose exec app python -m flask db migrate -m "Add new field"

# Apply migrations
docker-compose exec app python -m flask db upgrade

# Rollback migration
docker-compose exec app python -m flask db downgrade
```

## Production Deployment

### Security Considerations

1. **Change default passwords:**
   - Update `POSTGRES_PASSWORD` in `docker-compose.yml`
   - Update `SECRET_KEY` in environment variables

2. **Configure SSL/TLS:**
   - Use a reverse proxy like Nginx or Traefik in front of the application
   - Configure SSL certificates with your chosen reverse proxy

3. **Environment variables:**
   - Use `.env` file for sensitive configuration
   - Never commit secrets to version control

### Scaling

```bash
# Scale application instances
docker-compose up -d --scale app=3
```

### Monitoring

```bash
# View resource usage
docker stats

# View container logs
docker-compose logs --tail=100 app

# Monitor database performance
docker-compose exec db psql -U postgres -d recipe -c "SELECT * FROM pg_stat_activity;"
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check port usage
   netstat -tulpn | grep :5000
   
   # Use different ports
   docker-compose -f docker-compose.dev.yml up -d
   ```

2. **Database connection issues:**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Restart database
   docker-compose restart db
   ```

3. **Permission issues:**
   ```bash
   # Fix file permissions
   sudo chown -R $USER:$USER .
   
   # Rebuild containers
   docker-compose down && docker-compose up -d --build
   ```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove volumes (WARNING: This deletes all data)
docker-compose down -v

# Remove images
docker-compose down --rmi all

# Clean up everything
docker system prune -a
```

## File Structure

```
Recipe-Manager/
├── Dockerfile                 # Main application Dockerfile
├── docker-compose.yml        # Production services
├── docker-compose.dev.yml    # Development services
├── .dockerignore            # Docker ignore file
└── docker.env               # Docker environment variables
```

## Best Practices

1. **Use multi-stage builds** for smaller production images
2. **Run as non-root user** for security
3. **Use health checks** for service monitoring
4. **Separate development and production** configurations
5. **Use volumes** for persistent data
6. **Implement proper logging** and monitoring
7. **Keep secrets secure** using environment variables or secrets management

## Support

For issues related to Docker setup:
1. Check the logs: `docker-compose logs`
2. Verify environment variables
3. Ensure all required ports are available
4. Check Docker and Docker Compose versions

# Structured Logging System

This document describes the comprehensive structured logging system implemented in the Recipe Manager application.

## Overview

The logging system provides:
- **Dynamic log level filtering** based on `.env` configuration
- **Structured JSON logging** for production environments
- **Human-readable logging** for development
- **Comprehensive context** including request IDs, user IDs, and performance metrics
- **Automatic log rotation** with configurable file sizes
- **Multiple log outputs** (console and file)

## Configuration

### Environment Variables

Configure logging through environment variables in your `.env` file:

```bash
# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO

# Log file path (relative to project root)
LOG_FILE=logs/app.log

# Log request/response body (for debugging)
LOG_BODY=false
```

### Log Levels

The system supports five log levels with hierarchical filtering:

| Level | Description | Shows |
|-------|-------------|-------|
| `DEBUG` | Most verbose | All messages |
| `INFO` | Informational | INFO, WARNING, ERROR, CRITICAL |
| `WARNING` | Warning messages | WARNING, ERROR, CRITICAL |
| `ERROR` | Error messages | ERROR, CRITICAL |
| `CRITICAL` | Critical errors | CRITICAL only |

**Example**: If `LOG_LEVEL=INFO`, only INFO, WARNING, ERROR, and CRITICAL messages will be displayed. DEBUG messages will be suppressed.

### Automatic Environment-Based Logging

The logging system automatically adapts its output format based on the `ENVIRONMENT` setting:

#### Development Environment (`ENVIRONMENT=development`)
- Human-readable format with colors
- Includes module and line numbers
- Suitable for local development

```
2024-01-15 10:30:45 | INFO     | src.services.recipe_service:45 | Recipe created successfully
```

#### Production/Testing Environment (`ENVIRONMENT=production` or `ENVIRONMENT=testing`)
- Structured JSON format
- Machine-readable logs
- Includes comprehensive context
- Suitable for log aggregation systems

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "INFO",
  "logger": "src.services.recipe_service",
  "module": "recipe_service",
  "function": "create_recipe",
  "line": 45,
  "message": "Recipe created successfully",
  "user_id": "12345",
  "recipe_id": "67890",
  "operation": "create_recipe",
  "duration_ms": 125.5
}
```

## Usage

### Basic Logging

```python
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Basic logging
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical message")
```

### Structured Logging

```python
# Log with additional context
logger.info("User action performed", extra={
    "user_id": "12345",
    "action": "create_recipe",
    "recipe_id": "67890",
    "ip_address": "192.168.1.100"
})
```

### Service Class Logging

Use the `LoggerMixin` for automatic logger creation:

```python
from src.core.logging_config import LoggerMixin

class MyService(LoggerMixin):
    def __init__(self):
        # Logger is automatically available as self.logger
        self.logger.info("Service initialized")
    
    def process_data(self, data):
        self.logger.info("Processing data", extra={
            "data_size": len(data),
            "operation": "process_data"
        })
```

### Specialized Logging Functions

The system provides specialized logging functions for common operations:

#### Business Operations
```python
from src.core.logging_config import log_business_operation

log_business_operation(
    logger=logger,
    operation="create_recipe",
    user_id="12345",
    success=True,
    recipe_id="67890",
    duration_ms=125.5
)
```

#### Cache Operations
```python
from src.core.logging_config import log_cache_operation

log_cache_operation(
    logger=logger,
    operation="get",
    key="recipe:67890",
    hit=True,
    duration=0.001
)
```

#### Database Operations
```python
from src.core.logging_config import log_database_operation

log_database_operation(
    logger=logger,
    operation="SELECT",
    table="recipes",
    duration=0.045,
    success=True,
    rows_affected=1
)
```

#### HTTP Requests
```python
from src.core.logging_config import log_request_response

log_request_response(
    logger=logger,
    method="POST",
    url="/api/recipes",
    status_code=201,
    response_time=0.125,
    request_id="req-abc123",
    user_id="12345"
)
```

## Log Outputs

### Console Output
- **Development**: Colored, human-readable format
- **Production**: JSON format for log aggregation

### File Output
- **Main log file**: All log messages (`logs/app.log`)
- **Error log file**: ERROR and CRITICAL messages only (`logs/error.log`)
- **Automatic rotation**: 10MB max file size, 5 backup files

## Request/Response Logging

The application automatically logs all HTTP requests and responses:

### Request Logging
- Request method and URL
- User ID (from JWT token)
- Request ID (unique per request)
- User agent and IP address
- Request timestamp

### Response Logging
- Response status code
- Response time in milliseconds
- Request ID for correlation
- User ID for audit trail

## Performance Metrics

The logging system automatically tracks:
- **Response times** for HTTP requests
- **Database operation durations**
- **Cache hit/miss rates and response times**
- **Business operation execution times**

## Error Handling

### Exception Logging
```python
try:
    # Some operation
    result = risky_operation()
except Exception as e:
    logger.error("Operation failed", extra={
        "operation": "risky_operation",
        "error_type": type(e).__name__,
        "error_message": str(e),
        "user_id": user_id
    })
    raise
```

### Stack Trace Logging
Exceptions automatically include stack traces in the logs:

```json
{
  "timestamp": "2024-01-15T10:30:45.123Z",
  "level": "ERROR",
  "message": "Operation failed",
  "exception": {
    "type": "ValueError",
    "message": "Invalid input data",
    "traceback": "Traceback (most recent call last)..."
  }
}
```

## Testing the Logging System

### Test Script
Run the provided test script to see the logging system in action:

```bash
python test_logging.py
```

### Example Script
Run the comprehensive example:

```bash
python logging_example.py
```

### Manual Testing
1. Set different `LOG_LEVEL` values in your `.env` file
2. Start the application
3. Make API requests
4. Check console output and log files

## Best Practices

### 1. Use Appropriate Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General application flow
- **WARNING**: Something unexpected but not critical
- **ERROR**: Error conditions that don't stop the application
- **CRITICAL**: Serious errors that may stop the application

### 2. Include Context
Always include relevant context in your log messages:

```python
# Good
logger.info("Recipe created", extra={
    "user_id": user_id,
    "recipe_id": recipe.id,
    "recipe_title": recipe.title
})

# Avoid
logger.info("Recipe created")
```

### 3. Use Structured Data
Prefer structured logging over string formatting:

```python
# Good
logger.info("User logged in", extra={
    "user_id": user_id,
    "login_method": "jwt",
    "ip_address": request.remote_addr
})

# Avoid
logger.info(f"User {user_id} logged in via {login_method} from {ip}")
```

### 4. Log Performance Metrics
Include timing information for important operations:

```python
start_time = time.time()
# ... operation ...
duration = time.time() - start_time

logger.info("Operation completed", extra={
    "operation": "process_data",
    "duration_ms": round(duration * 1000, 2),
    "success": True
})
```

### 5. Don't Log Sensitive Data
Never log passwords, tokens, or other sensitive information:

```python
# Good
logger.info("User authenticated", extra={
    "user_id": user_id,
    "auth_method": "jwt"
})

# Avoid
logger.info("User authenticated", extra={
    "user_id": user_id,
    "password": password  # Never log passwords!
})
```

## Troubleshooting

### Common Issues

#### 1. Logs Not Appearing
- Check `LOG_LEVEL` setting
- Ensure log level is appropriate for the message
- Verify logger name is correct

#### 2. Log Files Not Created
- Check `LOG_FILE` path
- Ensure directory exists
- Check file permissions

#### 3. JSON Format Not Working
- Set `ENVIRONMENT=production` or `ENVIRONMENT=testing`
- Check for JSON serialization errors
- Verify all extra data is JSON-serializable

#### 4. Performance Issues
- Use appropriate log levels
- Avoid logging in tight loops
- Consider async logging for high-volume applications

### Debugging Log Configuration

```python
from src.core.logging_config import get_logger

logger = get_logger(__name__)

# Log current configuration
logger.info("Logging configuration", extra={
    "log_level": settings.LOG_LEVEL,
    "environment": settings.ENVIRONMENT,
    "log_file": settings.LOG_FILE
})
```

## Integration with Monitoring

### Log Aggregation
The structured JSON format is compatible with:
- **ELK Stack** (Elasticsearch, Logstash, Kibana)
- **Fluentd**
- **Splunk**
- **Datadog**
- **New Relic**

### Metrics Extraction
Use log parsing tools to extract metrics:
- Response time percentiles
- Error rates by endpoint
- User activity patterns
- Cache hit rates

### Alerting
Set up alerts based on log patterns:
- High error rates
- Slow response times
- Critical errors
- Authentication failures

This comprehensive logging system provides the foundation for monitoring, debugging, and maintaining the Recipe Manager application in production environments.

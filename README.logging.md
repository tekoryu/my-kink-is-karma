# Logging System Documentation

## Overview

This project implements a comprehensive logging system for monitoring, debugging, and auditing purposes. The logging system is designed to capture various types of events including API requests, database operations, user actions, security events, and performance metrics.

## Architecture

### Log Files Structure

The logging system creates the following log files in the `app/logs/` directory:

- **`debug.log`** - Debug level messages and database queries
- **`info.log`** - General application information and events
- **`error.log`** - Error messages and exceptions
- **`security.log`** - Security-related events and warnings
- **`api.log`** - API requests and responses in JSON format

### Log Rotation

All log files are configured with automatic rotation:
- **Maximum size**: 10MB per file
- **Backup count**: 5 backup files
- **Format**: RotatingFileHandler with automatic compression

## Configuration

### Django Settings

The logging configuration is defined in `app/config/settings.py`:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", "message": "%(message)s"}',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file_debug': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOGS_DIR / 'debug.log',
            'maxBytes': 1024 * 1024 * 10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        # ... other handlers
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file_info', 'file_error'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.pauta': {
            'handlers': ['console', 'file_api', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps.authentication': {
            'handlers': ['console', 'file_security', 'file_info'],
            'level': 'INFO',
            'propagate': False,
        },
        # ... other loggers
    },
}
```

## Usage

### Logging Utility Functions

The logging system provides utility functions in `app/apps/core/logging_utils.py`:

#### API Request Logging

```python
from apps.core.logging_utils import log_api_request

# Log API request details
log_api_request(request, response, duration)
```

**Parameters:**
- `request`: Django HttpRequest object
- `response`: Django HttpResponse object (optional)
- `duration`: Request duration in seconds (optional)

#### User Action Logging

```python
from apps.core.logging_utils import log_user_action

# Log user actions for audit trail
log_user_action(user, 'login_successful', {
    'ip': request.META.get('REMOTE_ADDR'),
    'user_agent': request.META.get('HTTP_USER_AGENT', '')
})
```

**Parameters:**
- `user`: Django User object
- `action`: Action description string
- `details`: Additional context dictionary (optional)

#### Security Event Logging

```python
from apps.core.logging_utils import log_security_event

# Log security-related events
log_security_event('login_failed', {
    'reason': 'invalid_credentials',
    'username': username,
    'ip': request.META.get('REMOTE_ADDR')
})
```

**Parameters:**
- `event_type`: Type of security event
- `details`: Event details dictionary
- `user`: Django User object (optional)

#### Database Operation Logging

```python
from apps.core.logging_utils import log_database_operation

# Log database operations
log_database_operation('INSERT', 'Tema', instance_id, {
    'nome': instance.nome
})
```

**Parameters:**
- `operation`: Database operation type (SELECT, INSERT, UPDATE, DELETE)
- `model`: Model name
- `instance_id`: Instance ID (optional)
- `details`: Additional details dictionary (optional)

#### Error Logging

```python
from apps.core.logging_utils import log_error

# Log errors with context
log_error(exception, {
    'view': 'TemaViewSet',
    'action': 'create',
    'data': request.data
})
```

**Parameters:**
- `error`: Exception object
- `context`: Additional context dictionary (optional)

#### Performance Logging

```python
from apps.core.logging_utils import log_performance

# Log performance metrics
log_performance('tema_list', duration, {
    'count': len(response.data)
})
```

**Parameters:**
- `operation`: Operation name
- `duration`: Duration in seconds
- `details`: Additional details dictionary (optional)

### Middleware Integration

The logging system includes automatic API request logging middleware:

```python
# In settings.py
MIDDLEWARE = [
    # ... other middleware
    'apps.core.logging_utils.api_logging_middleware',
]
```

This middleware automatically logs all API requests with:
- Request method and path
- User information
- Client IP address
- User agent
- Response status code
- Response size
- Request duration

### View Integration Examples

#### ViewSet with Logging

```python
from apps.core.logging_utils import log_database_operation, log_error, log_performance

class TemaViewSet(viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        try:
            import time
            start_time = time.time()
            
            response = super().list(request, *args, **kwargs)
            
            duration = time.time() - start_time
            log_performance('tema_list', duration, {'count': len(response.data)})
            log_database_operation('SELECT', 'Tema', details=f'Retrieved {len(response.data)} temas')
            
            return response
        except Exception as e:
            log_error(e, {'view': 'TemaViewSet', 'action': 'list'})
            raise
```

#### Authentication View with Logging

```python
from apps.core.logging_utils import log_user_action, log_security_event, log_error

def login_view(request):
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            log_security_event('login_failed', {
                'reason': 'missing_credentials',
                'username': username or 'not_provided'
            })
            return Response({'error': 'Username e password são obrigatórios'})
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            log_user_action(user, 'login_successful', {
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            })
            return Response({'message': 'Usuário autenticado com sucesso'})
        else:
            log_security_event('login_failed', {
                'reason': 'invalid_credentials',
                'username': username,
                'ip': request.META.get('REMOTE_ADDR')
            })
            return Response({'error': 'Credenciais inválidas'})
    except Exception as e:
        log_error(e, {'view': 'login_view'})
        raise
```

### Management Command Logging

```python
from apps.core.logging_utils import log_performance, log_error

class Command(BaseCommand):
    def handle(self, *args, **options):
        import time
        start_time = time.time()
        
        try:
            # Command logic here
            
            # Log performance metrics
            duration = time.time() - start_time
            log_performance('sync_proposicoes_command', duration, {
                'total_processed': total,
                'force': options['force'],
                'dry_run': options['dry_run']
            })
        except Exception as e:
            log_error(e, {'command': 'sync_proposicoes'})
            raise
```

## Log Formats

### Verbose Format
```
ERROR 2025-08-11 17:56:45,126 logging_utils 1 137622752340744 Error: {"error_type": "Exception", "error_message": "Test error", "timestamp": "2025-08-11T20:56:45.126126+00:00", "context": {"test": "context"}}
```

### JSON Format
```json
{"timestamp": "2025-08-11 17:56:45,154", "level": "INFO", "module": "logging_utils", "message": "API Request: {\"method\": \"GET\", \"path\": \"/test/\", \"user\": \"anonymous\", \"ip\": \"127.0.0.1\", \"user_agent\": \"\", \"timestamp\": \"2025-08-11T20:56:45.154458+00:00\"}"}
```

## Monitoring and Analysis

### Log File Locations

All log files are stored in the `app/logs/` directory:
- `app/logs/debug.log`
- `app/logs/info.log`
- `app/logs/error.log`
- `app/logs/security.log`
- `app/logs/api.log`

### Log Analysis Commands

The following examples show both Unix-like (bash) and Windows PowerShell equivalents.

```bash
# View recent errors (Unix/Linux/macOS)
tail -f app/logs/error.log

# Search for specific user actions (Unix/Linux/macOS)
grep "login_successful" app/logs/security.log

# Monitor API requests (Unix/Linux/macOS)
tail -f app/logs/api.log

# Check performance metrics (Unix/Linux/macOS)
grep "Performance" app/logs/info.log
```

```powershell
# View recent errors (Windows PowerShell 7+)
Get-Content .\app\logs\error.log -Wait -Tail 50

# Search for specific user actions (Windows PowerShell)
Select-String -Path .\app\logs\security.log -Pattern "login_successful"

# Monitor API requests (Windows PowerShell)
Get-Content .\app\logs\api.log -Wait -Tail 50

# Check performance metrics (Windows PowerShell)
Select-String -Path .\app\logs\info.log -Pattern "Performance"
```



Note:
- Use -Tail N to start with the last N lines; omit it to stream entire file.
- Paths in PowerShell use backslashes; leading .\ ensures relative to project root.
- For filtering multiple files in PowerShell, you can pass a wildcard path (e.g., .\app\logs\*.log) to Select-String.

### Services Logging (APISyncService)

The APISyncService in apps/pauta/services.py uses Python's logging with logger = logging.getLogger(__name__). When imported, the logger name resolves to apps.pauta.services and inherits the configuration from the apps.pauta logger family defined in settings.

What is logged:
- INFO:
  - Start of a proposition sync: "Sincronizando proposição: <identificador>"
  - Successful sync completion: "Proposição <identificador> sincronizada com sucesso"
- WARNING:
  - Non-200 responses from Senado/Câmara APIs, including the status code
- ERROR:
  - Request exceptions to external APIs
  - Exceptions while processing API responses
  - Exceptions during synchronization (also stored into proposicao.erro_sincronizacao)

Where the logs go:
- INFO and WARNING entries will appear in app/logs/info.log
- ERROR entries will appear in app/logs/error.log

Tip: To focus on synchronization activity only, filter by module name in the log line (module typically includes services) or search for keywords like "Sincronizando proposição" and "sincronizada com sucesso".

### Docker Commands

```bash
# View logs in Docker container
docker compose run --rm app sh -c "tail -f /app/logs/error.log"

# Check log file sizes
docker compose run --rm app sh -c "ls -lh /app/logs/"

# View specific log content
docker compose run --rm app sh -c "cat /app/logs/api.log"
```

## Security Considerations

### Sensitive Data

The logging system is designed to avoid logging sensitive information:
- Passwords are never logged
- Personal data is minimized
- IP addresses are logged for security monitoring
- User agents are logged for debugging

### Log File Permissions

Log files are created with appropriate permissions:
- Owner: django-u (application user)
- Group: django-u
- Permissions: 644 (readable by owner and group)

### Log Rotation

Automatic log rotation prevents:
- Disk space exhaustion
- Performance degradation
- Security risks from large log files

## Best Practices

### When to Log

1. **Always log:**
   - User authentication events
   - Database write operations
   - Security-related events
   - API errors and exceptions
   - Performance metrics for critical operations

2. **Consider logging:**
   - API requests (for monitoring)
   - Database read operations (for debugging)
   - Business logic events (for audit trails)

3. **Avoid logging:**
   - Sensitive user data
   - Passwords or authentication tokens
   - Excessive debug information in production

### Performance Considerations

1. **Use appropriate log levels:**
   - DEBUG: Development only
   - INFO: General application events
   - WARNING: Potential issues
   - ERROR: Actual errors

2. **Minimize log overhead:**
   - Use structured logging for better parsing
   - Avoid expensive operations in log messages
   - Use log rotation to manage file sizes

3. **Monitor log performance:**
   - Check log file sizes regularly
   - Monitor disk space usage
   - Review log rotation effectiveness

## Troubleshooting

### Common Issues

1. **Permission denied errors:**
   ```bash
   # Ensure logs directory exists and has correct permissions
   docker compose run --rm app sh -c "mkdir -p /app/logs && chown django-u:django-u /app/logs"
   ```

2. **Log files not created:**
   - Check Django settings configuration
   - Verify logger names match in code
   - Ensure logging is initialized properly

3. **Excessive log volume:**
   - Adjust log levels in settings
   - Review logging frequency in views
   - Implement log filtering

### Debugging Logging Issues

```python
# Test logging functionality
from apps.core.logging_utils import log_error, log_performance

# Test basic logging
log_error(Exception("Test error"), {'test': 'context'})
log_performance('test_operation', 0.5, {'test': 'details'})
```

## Future Enhancements

### Potential Improvements

1. **External Log Aggregation:**
   - Integration with ELK Stack (Elasticsearch, Logstash, Kibana)
   - Cloud logging services (AWS CloudWatch, Google Cloud Logging)
   - Centralized log management

2. **Advanced Analytics:**
   - Real-time log analysis
   - Automated alerting for critical events
   - Performance trend analysis

3. **Enhanced Security:**
   - Log encryption
   - Digital signatures for audit logs
   - Compliance reporting features

4. **Monitoring Integration:**
   - Prometheus metrics export
   - Health check endpoints
   - Custom dashboard creation

## Support

For issues related to the logging system:

1. Check the log files for error messages
2. Verify configuration in `settings.py`
3. Test logging functions individually
4. Review middleware configuration
5. Check file permissions and disk space

The logging system is designed to be robust and self-documenting, providing comprehensive visibility into application behavior while maintaining performance and security.

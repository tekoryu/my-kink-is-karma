import logging
from functools import wraps
from django.http import HttpRequest
from django.utils import timezone
import json

# Get loggers for different modules
logger = logging.getLogger('apps.core')
pauta_logger = logging.getLogger('apps.pauta')
auth_logger = logging.getLogger('apps.authentication')
security_logger = logging.getLogger('django.security')

def log_api_request(request: HttpRequest, response=None, duration=None):
    """Log API request details"""
    log_data = {
        'method': request.method,
        'path': request.path,
        'user': getattr(request.user, 'username', 'anonymous'),
        'ip': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'timestamp': timezone.now().isoformat(),
    }
    
    if response:
        log_data['status_code'] = response.status_code
        log_data['response_size'] = len(response.content) if hasattr(response, 'content') else 0
    
    if duration:
        log_data['duration_ms'] = round(duration * 1000, 2)
    
    pauta_logger.info(f"API Request: {json.dumps(log_data)}")

def get_client_ip(request: HttpRequest) -> str:
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')

def log_user_action(user, action, details=None):
    """Log user actions for audit trail"""
    log_data = {
        'user': user.username if user.is_authenticated else 'anonymous',
        'action': action,
        'timestamp': timezone.now().isoformat(),
    }
    
    if details:
        log_data['details'] = details
    
    auth_logger.info(f"User Action: {json.dumps(log_data)}")

def log_security_event(event_type, details, user=None):
    """Log security-related events"""
    log_data = {
        'event_type': event_type,
        'user': user.username if user and user.is_authenticated else 'anonymous',
        'details': details,
        'timestamp': timezone.now().isoformat(),
    }
    
    security_logger.warning(f"Security Event: {json.dumps(log_data)}")

def log_database_operation(operation, model, instance_id=None, details=None):
    """Log database operations"""
    log_data = {
        'operation': operation,
        'model': model,
        'instance_id': instance_id,
        'timestamp': timezone.now().isoformat(),
    }
    
    if details:
        log_data['details'] = details
    
    logger.info(f"Database Operation: {json.dumps(log_data)}")

def log_error(error, context=None):
    """Log errors with context"""
    log_data = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'timestamp': timezone.now().isoformat(),
    }
    
    if context:
        log_data['context'] = context
    
    logger.error(f"Error: {json.dumps(log_data)}")

def log_performance(operation, duration, details=None):
    """Log performance metrics"""
    log_data = {
        'operation': operation,
        'duration_ms': round(duration * 1000, 2),
        'timestamp': timezone.now().isoformat(),
    }
    
    if details:
        log_data['details'] = details
    
    logger.info(f"Performance: {json.dumps(log_data)}")

def api_logging_middleware(get_response):
    """Django middleware for automatic API logging"""
    def middleware(request):
        start_time = timezone.now()
        
        # Log request
        log_api_request(request)
        
        response = get_response(request)
        
        # Calculate duration
        duration = (timezone.now() - start_time).total_seconds()
        
        # Log response
        log_api_request(request, response, duration)
        
        return response
    
    return middleware

def log_function_call(func_name, args=None, kwargs=None, result=None, duration=None):
    """Log function calls for debugging"""
    log_data = {
        'function': func_name,
        'timestamp': timezone.now().isoformat(),
    }
    
    if args:
        log_data['args'] = str(args)
    if kwargs:
        log_data['kwargs'] = str(kwargs)
    if result is not None:
        log_data['result'] = str(result)
    if duration:
        log_data['duration_ms'] = round(duration * 1000, 2)
    
    logger.debug(f"Function Call: {json.dumps(log_data)}")

def log_decorator(logger_name='apps.core'):
    """Decorator to automatically log function calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import time
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log_function_call(
                    func.__name__, 
                    args, 
                    kwargs, 
                    result, 
                    duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time
                log_error(e, {'function': func.__name__})
                raise
        
        return wrapper
    return decorator

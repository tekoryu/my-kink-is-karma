from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from apps.core.logging_utils import log_user_action, log_security_event, log_error


@extend_schema(
    summary="Autenticar usuário",
    description="Autentica um usuário com username e password",
    tags=["authentication"],
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'username': {'type': 'string', 'description': 'Nome de usuário'},
                'password': {'type': 'string', 'description': 'Senha do usuário'},
            },
            'required': ['username', 'password']
        }
    },
    responses={
        200: {
            'type': 'object',
            'properties': {
                'message': {'type': 'string'},
                'user_id': {'type': 'integer'},
                'username': {'type': 'string'},
            }
        },
        401: {
            'type': 'object',
            'properties': {
                'error': {'type': 'string'},
            }
        }
    },
    examples=[
        OpenApiExample(
            'Login bem-sucedido',
            value={
                'message': 'Usuário autenticado com sucesso',
                'user_id': 1,
                'username': 'admin'
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            'Credenciais inválidas',
            value={
                'error': 'Credenciais inválidas'
            },
            response_only=True,
            status_codes=['401']
        ),
    ]
)
@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint para autenticação de usuários.
    
    Recebe username e password e retorna informações do usuário se autenticado.
    """
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            log_security_event('login_failed', {
                'reason': 'missing_credentials',
                'username': username or 'not_provided'
            })
            return Response(
                {'error': 'Username e password são obrigatórios'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            log_user_action(user, 'login_successful', {
                'ip': request.META.get('REMOTE_ADDR'),
                'user_agent': request.META.get('HTTP_USER_AGENT', '')
            })
            return Response({
                'message': 'Usuário autenticado com sucesso',
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_200_OK)
        else:
            log_security_event('login_failed', {
                'reason': 'invalid_credentials',
                'username': username,
                'ip': request.META.get('REMOTE_ADDR')
            })
            return Response(
                {'error': 'Credenciais inválidas'},
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        log_error(e, {
            'view': 'login_view',
            'username': username if 'username' in locals() else 'unknown'
        })
        raise

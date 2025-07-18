"""
Handler de AWS Lambda para la aplicación Flask

Este módulo adapta la aplicación Flask para funcionar en AWS Lambda
usando el patrón de proxy de API Gateway.

¿Qué hace este handler?
- Recibe eventos de API Gateway
- Los convierte en requests de Flask
- Ejecuta la aplicación Flask
- Retorna la respuesta en formato de API Gateway
"""

import json
import logging
from typing import Dict, Any
from application.main import app
from application.config import settings

# Configurar logging
logging.basicConfig(level=getattr(logging, settings.logging.log_level))
logger = logging.getLogger(__name__)


def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler principal de AWS Lambda
    
    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda
    
    Returns:
        Respuesta en formato de API Gateway
    """
    try:
        logger.info(f"Evento recibido: {json.dumps(event, default=str)}")
        
        # Extraer información del evento de API Gateway
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        query_string_parameters = event.get('queryStringParameters', {})
        body = event.get('body', '')
        
        # Crear request de Flask
        with app.test_request_context(
            path=path,
            method=http_method,
            headers=headers,
            query_string=query_string_parameters,
            data=body
        ):
            # Ejecutar la aplicación Flask
            response = app.full_dispatch_request()
            
            # Preparar respuesta para API Gateway
            return {
                'statusCode': response.status_code,
                'headers': dict(response.headers),
                'body': response.get_data(as_text=True)
            }
            
    except Exception as e:
        logger.error(f"Error en handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }


def health_check_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler específico para health check
    
    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda
    
    Returns:
        Respuesta de health check
    """
    try:
        logger.info("Health check solicitado")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'status': 'ok',
                'service': 'accounting-app',
                'environment': settings.environment,
                'version': settings.version
            })
        }
        
    except Exception as e:
        logger.error(f"Error en health check: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'error',
                'message': str(e)
            })
        }


def options_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler para requests OPTIONS (CORS preflight)
    
    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda
    
    Returns:
        Respuesta CORS
    """
    logger.info("Request OPTIONS recibido")
    
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS',
            'Access-Control-Max-Age': '86400'
        },
        'body': ''
    }


def error_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handler para manejo de errores
    
    Args:
        event: Evento de API Gateway
        context: Contexto de Lambda
    
    Returns:
        Respuesta de error
    """
    logger.error(f"Error no manejado: {json.dumps(event, default=str)}")
    
    return {
        'statusCode': 500,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        })
    } 
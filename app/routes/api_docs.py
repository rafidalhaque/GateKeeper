"""
API Documentation Routes
"""
from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from app.swagger_spec import SWAGGER_SPEC

bp = Blueprint('api_docs', __name__)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "GateKeeper API Documentation",
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 3,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'syntaxHighlight': {
            'activate': True,
            'theme': 'monokai'
        }
    }
)


@bp.route('/swagger.json')
def swagger_spec():
    """Return the OpenAPI specification as JSON"""
    return jsonify(SWAGGER_SPEC)


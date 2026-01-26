"""
API Documentation Routes with Enhanced Swagger UI
"""
from flask import Blueprint, jsonify
from flask_swagger_ui import get_swaggerui_blueprint
from app.swagger_spec import SWAGGER_SPEC

bp = Blueprint('api_docs', __name__)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

# Enhanced Swagger UI with custom styling and configuration
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "GateKeeper API Documentation",
        'docExpansion': 'list',  # 'list', 'full', or 'none'
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'displayRequestDuration': True,
        'filter': True,  # Enable search/filter
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,  # Enable "Try it out" by default
        'requestSnippetsEnabled': True,  # Show request code snippets
        'persistAuthorization': True,  # Persist authorization data
        'displayOperationId': False,
        'deepLinking': True,  # Enable deep linking for operations
        'syntaxHighlight': {
            'activate': True,
            'theme': 'monokai'  # monokai, agate, arta, nord, obsidian
        },
        'layout': 'BaseLayout',
        'validatorUrl': None,  # Disable validator badge
        # Custom CSS for beautiful, modern styling
        'customCss': '''
            /* Brand colors and modern styling */
            .swagger-ui .topbar { 
                background-color: #667eea;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border-bottom: 3px solid #5a67d8;
            }
            .swagger-ui .topbar .download-url-wrapper { display: none; }
            .swagger-ui .info { margin: 30px 0; }
            .swagger-ui .info .title { 
                font-size: 36px;
                color: #1a202c;
                font-weight: 700;
            }
            .swagger-ui .info .description { 
                font-size: 16px;
                line-height: 1.6;
                color: #4a5568;
                margin-top: 15px;
            }
            .swagger-ui .scheme-container { 
                background: #f7fafc;
                border-radius: 8px;
                padding: 15px;
                margin: 20px 0;
                border: 1px solid #e2e8f0;
            }
            .swagger-ui .opblock { 
                border-radius: 8px;
                margin-bottom: 15px;
                border: 1px solid #e2e8f0;
                box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
            }
            .swagger-ui .opblock.opblock-get {
                border-left: 4px solid #48bb78;
                background: rgba(72, 187, 120, 0.05);
            }
            .swagger-ui .opblock.opblock-post {
                border-left: 4px solid #4299e1;
                background: rgba(66, 153, 225, 0.05);
            }
            .swagger-ui .opblock.opblock-put {
                border-left: 4px solid #ed8936;
                background: rgba(237, 137, 54, 0.05);
            }
            .swagger-ui .opblock.opblock-delete {
                border-left: 4px solid #f56565;
                background: rgba(245, 101, 101, 0.05);
            }
            .swagger-ui .opblock .opblock-summary {
                border-radius: 8px 8px 0 0;
                padding: 15px;
            }
            .swagger-ui .btn { 
                border-radius: 6px;
                font-weight: 600;
                transition: all 0.2s;
            }
            .swagger-ui .btn.execute {
                background-color: #667eea;
                border-color: #667eea;
            }
            .swagger-ui .btn.execute:hover {
                background-color: #5a67d8;
                border-color: #5a67d8;
                transform: translateY(-1px);
                box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
            }
            .swagger-ui .response { 
                border-radius: 6px;
                margin-top: 10px;
            }
            .swagger-ui .model { 
                border-radius: 6px;
                background: #f7fafc;
            }
            .swagger-ui .model-title { 
                font-weight: 600;
                color: #2d3748;
            }
            .swagger-ui .parameter__name { 
                font-weight: 600;
                color: #2d3748;
            }
            .swagger-ui .parameter__type {
                color: #667eea;
                font-weight: 500;
            }
            .swagger-ui .response-col_status {
                font-weight: 700;
            }
            .swagger-ui .responses-inner h4 { 
                font-size: 16px;
                font-weight: 600;
                margin: 20px 0 10px 0;
            }
            .swagger-ui .markdown p { 
                line-height: 1.6;
                margin: 10px 0;
            }
            .swagger-ui .markdown code {
                background: #f7fafc;
                padding: 2px 6px;
                border-radius: 4px;
                font-size: 14px;
                color: #667eea;
                border: 1px solid #e2e8f0;
            }
            /* Search/filter styling */
            .swagger-ui .filter-container input {
                border-radius: 6px;
                border: 2px solid #e2e8f0;
                padding: 10px 15px;
                font-size: 14px;
            }
            .swagger-ui .filter-container input:focus {
                border-color: #667eea;
                outline: none;
                box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            }
            /* Authorization button */
            .swagger-ui .btn.authorize {
                background-color: #48bb78;
                border-color: #48bb78;
            }
            .swagger-ui .btn.authorize:hover {
                background-color: #38a169;
                border-color: #38a169;
            }
            /* Tag sections */
            .swagger-ui .opblock-tag {
                font-size: 20px;
                font-weight: 700;
                color: #1a202c;
                border-bottom: 2px solid #e2e8f0;
                padding: 15px 0;
                margin: 30px 0 20px 0;
            }
            /* Make it responsive */
            @media (max-width: 768px) {
                .swagger-ui .info .title { font-size: 28px; }
                .swagger-ui .opblock-tag { font-size: 18px; }
            }
        '''
    }
)


@bp.route('/swagger.json')
def swagger_spec():
    """Return the OpenAPI specification as JSON"""
    return jsonify(SWAGGER_SPEC)

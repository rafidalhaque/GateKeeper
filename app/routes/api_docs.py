"""
API Documentation Routes with Enhanced Swagger UI
"""
from flask import Blueprint, jsonify, Response
from flask_swagger_ui import get_swaggerui_blueprint
from app.swagger_spec import SWAGGER_SPEC

bp = Blueprint('api_docs', __name__)

# Swagger UI configuration
SWAGGER_URL = '/api/docs'
API_URL = '/api/swagger.json'

# Enhanced Swagger UI with custom styling and configuration
# CSS with DaisyUI theme support (light/dark)
swagger_css = '''
    /* Light Theme (Default) */
    [data-theme="light"] .swagger-ui,
    .swagger-ui {
        --swagger-bg: #ffffff;
        --swagger-text: #1f2937;
        --swagger-text-muted: #6b7280;
        --swagger-border: #e5e7eb;
        --swagger-card-bg: #f9fafb;
        --swagger-code-bg: #f3f4f6;
        --swagger-primary: #667eea;
        --swagger-primary-hover: #5a67d8;
        --swagger-success: #10b981;
        --swagger-info: #3b82f6;
        --swagger-warning: #f59e0b;
        --swagger-error: #ef4444;
    }
    
    /* Dark Theme */
    [data-theme="dark"] .swagger-ui {
        --swagger-bg: #1f2937;
        --swagger-text: #f9fafb;
        --swagger-text-muted: #d1d5db;
        --swagger-border: #374151;
        --swagger-card-bg: #111827;
        --swagger-code-bg: #1f2937;
        --swagger-primary: #818cf8;
        --swagger-primary-hover: #6366f1;
        --swagger-success: #34d399;
        --swagger-info: #60a5fa;
        --swagger-warning: #fbbf24;
        --swagger-error: #f87171;
    }
    
    /* Base Swagger UI Styles */
    .swagger-ui {
        background-color: var(--swagger-bg);
        color: var(--swagger-text);
        transition: background-color 0.3s ease, color 0.3s ease;
    }
    
    /* Topbar - DaisyUI gradient */
    .swagger-ui .topbar { 
        background: linear-gradient(135deg, var(--swagger-primary) 0%, #764ba2 100%);
        border-bottom: 3px solid var(--swagger-primary-hover);
        padding: 15px 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .swagger-ui .topbar .download-url-wrapper { display: none; }
    
    /* Theme Switcher Button */
    .theme-switcher {
        background: rgba(255, 255, 255, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.3);
        color: white;
        padding: 8px 16px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 600;
        transition: all 0.2s;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .theme-switcher:hover {
        background: rgba(255, 255, 255, 0.3);
        transform: translateY(-1px);
    }
    
    /* Info Section */
    .swagger-ui .info { 
        margin: 30px 0;
        padding: 20px;
        background: var(--swagger-card-bg);
        border-radius: 12px;
        border: 1px solid var(--swagger-border);
    }
    
    .swagger-ui .info .title { 
        font-size: 36px;
        color: var(--swagger-text);
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .swagger-ui .info .description { 
        font-size: 16px;
        line-height: 1.6;
        color: var(--swagger-text-muted);
        margin-top: 15px;
    }
    
    /* Scheme Container */
    .swagger-ui .scheme-container { 
        background: var(--swagger-card-bg);
        border-radius: 8px;
        padding: 15px;
        margin: 20px 0;
        border: 1px solid var(--swagger-border);
    }
    
    /* Operation Blocks */
    .swagger-ui .opblock { 
        border-radius: 8px;
        margin-bottom: 15px;
        border: 1px solid var(--swagger-border);
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        background: var(--swagger-card-bg);
        transition: all 0.2s;
    }
    
    .swagger-ui .opblock:hover {
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .swagger-ui .opblock.opblock-get {
        border-left: 4px solid var(--swagger-success);
        background: var(--swagger-card-bg);
    }
    
    .swagger-ui .opblock.opblock-post {
        border-left: 4px solid var(--swagger-info);
        background: var(--swagger-card-bg);
    }
    
    .swagger-ui .opblock.opblock-put {
        border-left: 4px solid var(--swagger-warning);
        background: var(--swagger-card-bg);
    }
    
    .swagger-ui .opblock.opblock-delete {
        border-left: 4px solid var(--swagger-error);
        background: var(--swagger-card-bg);
    }
    
    .swagger-ui .opblock .opblock-summary {
        border-radius: 8px 8px 0 0;
        padding: 15px;
        color: var(--swagger-text);
    }
    
    /* Buttons */
    .swagger-ui .btn { 
        border-radius: 6px;
        font-weight: 600;
        transition: all 0.2s;
    }
    
    .swagger-ui .btn.execute {
        background-color: var(--swagger-primary);
        border-color: var(--swagger-primary);
        color: white;
    }
    
    .swagger-ui .btn.execute:hover {
        background-color: var(--swagger-primary-hover);
        border-color: var(--swagger-primary-hover);
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(102, 126, 234, 0.3);
    }
    
    /* Response Section */
    .swagger-ui .response { 
        border-radius: 6px;
        margin-top: 10px;
        background: var(--swagger-card-bg);
        border: 1px solid var(--swagger-border);
    }
    
    /* Model Section */
    .swagger-ui .model { 
        border-radius: 6px;
        background: var(--swagger-code-bg);
        border: 1px solid var(--swagger-border);
    }
    
    .swagger-ui .model-title { 
        font-weight: 600;
        color: var(--swagger-text);
    }
    
    /* Parameters */
    .swagger-ui .parameter__name { 
        font-weight: 600;
        color: var(--swagger-text);
    }
    
    .swagger-ui .parameter__type {
        color: var(--swagger-primary);
        font-weight: 500;
    }
    
    .swagger-ui .response-col_status {
        font-weight: 700;
    }
    
    .swagger-ui .responses-inner h4 { 
        font-size: 16px;
        font-weight: 600;
        margin: 20px 0 10px 0;
        color: var(--swagger-text);
    }
    
    /* Markdown */
    .swagger-ui .markdown p { 
        line-height: 1.6;
        margin: 10px 0;
        color: var(--swagger-text-muted);
    }
    
    .swagger-ui .markdown code {
        background: var(--swagger-code-bg);
        padding: 2px 6px;
        border-radius: 4px;
        font-size: 14px;
        color: var(--swagger-primary);
        border: 1px solid var(--swagger-border);
    }
    
    /* Search/Filter */
    .swagger-ui .filter-container input {
        border-radius: 6px;
        border: 2px solid var(--swagger-border);
        padding: 10px 15px;
        font-size: 14px;
        background: var(--swagger-bg);
        color: var(--swagger-text);
    }
    
    .swagger-ui .filter-container input:focus {
        border-color: var(--swagger-primary);
        outline: none;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Authorization Button */
    .swagger-ui .btn.authorize {
        background-color: var(--swagger-success);
        border-color: var(--swagger-success);
        color: white;
    }
    
    .swagger-ui .btn.authorize:hover {
        background-color: var(--swagger-success);
        opacity: 0.9;
    }
    
    /* Tag Sections */
    .swagger-ui .opblock-tag {
        font-size: 20px;
        font-weight: 700;
        color: var(--swagger-text);
        border-bottom: 2px solid var(--swagger-border);
        padding: 15px 0;
        margin: 30px 0 20px 0;
    }
    
    /* Table Styles */
    .swagger-ui table {
        background: var(--swagger-card-bg);
        border: 1px solid var(--swagger-border);
    }
    
    .swagger-ui table thead tr {
        background: var(--swagger-code-bg);
    }
    
    .swagger-ui table tbody tr {
        border-bottom: 1px solid var(--swagger-border);
    }
    
    .swagger-ui table tbody tr td {
        color: var(--swagger-text);
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .swagger-ui .info .title { font-size: 28px; }
        .swagger-ui .opblock-tag { font-size: 18px; }
        .theme-switcher { font-size: 12px; padding: 6px 12px; }
    }
'''

# JavaScript for theme switching
swagger_js = '''
<script>
(function() {
    // Get current theme from localStorage or default to light
    function getTheme() {
        return localStorage.getItem('swagger-theme') || 'light';
    }
    
    // Set theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('swagger-theme', theme);
        
        // Update theme switcher button
        const switcher = document.querySelector('.theme-switcher');
        if (switcher) {
            switcher.innerHTML = theme === 'dark' 
                ? '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg> Light'
                : '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg> Dark';
        }
        
        // Save to backend if authenticated
        saveThemePreference(theme);
    }
    
    // Save theme preference to backend
    async function saveThemePreference(theme) {
        try {
            const response = await fetch('/api/settings/theme', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme: theme })
            });
            
            if (!response.ok && response.status !== 401) {
                console.warn('Failed to save theme preference');
            }
        } catch (error) {
            // Silently fail - user might not be authenticated
        }
    }
    
    // Load theme preference from backend
    async function loadThemePreference() {
        try {
            const response = await fetch('/api/settings/theme');
            if (response.ok) {
                const data = await response.json();
                if (data.theme) {
                    setTheme(data.theme);
                    return;
                }
            }
        } catch (error) {
            // Fall back to localStorage
        }
        
        // Use localStorage theme
        const theme = getTheme();
        setTheme(theme);
    }
    
    // Initialize theme when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            loadThemePreference();
        });
    } else {
        loadThemePreference();
    }
    
    // Create theme switcher button
    function createThemeSwitcher() {
        const topbar = document.querySelector('.swagger-ui .topbar');
        if (!topbar) return;
        
        // Check if switcher already exists
        if (document.querySelector('.theme-switcher')) return;
        
        const switcher = document.createElement('button');
        switcher.className = 'theme-switcher';
        switcher.onclick = function() {
            const currentTheme = getTheme();
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        };
        
        const currentTheme = getTheme();
        switcher.innerHTML = currentTheme === 'dark'
            ? '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg> Light'
            : '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg> Dark';
        
        topbar.appendChild(switcher);
    }
    
    // Wait for Swagger UI to load
    const checkSwaggerUI = setInterval(function() {
        if (document.querySelector('.swagger-ui .topbar')) {
            clearInterval(checkSwaggerUI);
            createThemeSwitcher();
        }
    }, 100);
    
    // Also try after a delay
    setTimeout(function() {
        clearInterval(checkSwaggerUI);
        createThemeSwitcher();
    }, 2000);
})();
</script>
'''

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "GateKeeper API Documentation",
        'docExpansion': 'list',
        'defaultModelsExpandDepth': 3,
        'defaultModelExpandDepth': 3,
        'displayRequestDuration': True,
        'filter': True,
        'showExtensions': True,
        'showCommonExtensions': True,
        'tryItOutEnabled': True,
        'requestSnippetsEnabled': True,
        'persistAuthorization': True,
        'displayOperationId': False,
        'deepLinking': True,
        'syntaxHighlight': {
            'activate': True,
            'theme': 'monokai'
        },
        'layout': 'BaseLayout',
        'validatorUrl': None,
        'customCss': swagger_css,
        'customJsUrl': '/api/swagger-theme.js'
    }
)


@bp.route('/swagger.json')
def swagger_spec():
    """Return the OpenAPI specification as JSON"""
    return jsonify(SWAGGER_SPEC)


@bp.route('/swagger-theme.js')
def swagger_theme_js():
    """Return theme switcher JavaScript"""
    js_content = '''
(function() {
    // Get current theme from localStorage or default to light
    function getTheme() {
        return localStorage.getItem('swagger-theme') || 'light';
    }
    
    // Set theme
    function setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('swagger-theme', theme);
        
        // Update theme switcher button
        const switcher = document.querySelector('.theme-switcher');
        if (switcher) {
            switcher.innerHTML = theme === 'dark' 
                ? '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg> Light'
                : '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg> Dark';
        }
        
        // Save to backend if authenticated
        saveThemePreference(theme);
    }
    
    // Save theme preference to backend
    async function saveThemePreference(theme) {
        try {
            const response = await fetch('/api/settings/theme', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ theme: theme })
            });
            
            if (!response.ok && response.status !== 401) {
                console.warn('Failed to save theme preference');
            }
        } catch (error) {
            // Silently fail - user might not be authenticated
        }
    }
    
    // Load theme preference from backend
    async function loadThemePreference() {
        try {
            const response = await fetch('/api/settings/theme');
            if (response.ok) {
                const data = await response.json();
                if (data.theme) {
                    setTheme(data.theme);
                    return;
                }
            }
        } catch (error) {
            // Fall back to localStorage
        }
        
        // Use localStorage theme
        const theme = getTheme();
        setTheme(theme);
    }
    
    // Initialize theme when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            loadThemePreference();
        });
    } else {
        loadThemePreference();
    }
    
    // Create theme switcher button
    function createThemeSwitcher() {
        const topbar = document.querySelector('.swagger-ui .topbar');
        if (!topbar) return;
        
        // Check if switcher already exists
        if (document.querySelector('.theme-switcher')) return;
        
        const switcher = document.createElement('button');
        switcher.className = 'theme-switcher';
        switcher.onclick = function() {
            const currentTheme = getTheme();
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            setTheme(newTheme);
        };
        
        const currentTheme = getTheme();
        switcher.innerHTML = currentTheme === 'dark'
            ? '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg> Light'
            : '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" style="width: 16px; height: 16px;"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg> Dark';
        
        topbar.appendChild(switcher);
    }
    
    // Wait for Swagger UI to load
    const checkSwaggerUI = setInterval(function() {
        if (document.querySelector('.swagger-ui .topbar')) {
            clearInterval(checkSwaggerUI);
            createThemeSwitcher();
        }
    }, 100);
    
    // Also try after a delay
    setTimeout(function() {
        clearInterval(checkSwaggerUI);
        createThemeSwitcher();
    }, 2000);
    })();
'''
    return Response(js_content, mimetype='application/javascript')

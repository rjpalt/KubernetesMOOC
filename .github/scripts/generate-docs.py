#!/usr/bin/env python3
"""Generate documentation site from templates and OpenAPI specs."""

import json
import shutil
from datetime import datetime
from pathlib import Path
from string import Template

def load_template(template_path: Path) -> Template:
    """Load a template file."""
    return Template(template_path.read_text())

def generate_swagger_ui(output_path: Path, title: str, openapi_url: str):
    """Generate a Swagger UI page."""
    template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>$title</title>
    <link rel="stylesheet" type="text/css" href="../../assets/swagger-ui-bundle.css" />
    <style>
        html { box-sizing: border-box; overflow: -moz-scrollbars-vertical; overflow-y: scroll; }
        *, *:before, *:after { box-sizing: inherit; }
        body { margin:0; background: #fafafa; }
    </style>
</head>
<body>
    <div id="swagger-ui"></div>
    <script src="../../assets/swagger-ui-bundle.js"></script>
    <script>
        SwaggerUIBundle({
            url: '$openapi_url',
            dom_id: '#swagger-ui',
            deepLinking: true,
            presets: [
                SwaggerUIBundle.presets.apis,
                SwaggerUIBundle.presets.standalone
            ],
            plugins: [
                SwaggerUIBundle.plugins.DownloadUrl
            ],
            layout: "StandaloneLayout"
        });
    </script>
</body>
</html>""")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(template.substitute(title=title, openapi_url=openapi_url))

def generate_main_index(output_path: Path):
    """Generate the main documentation index."""
    template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Todo Microservices - Documentation</title>
    <link rel="stylesheet" href="assets/styles.css">
</head>
<body>
    <div class="header">
        <h1>📚 Todo Microservices Documentation</h1>
        <p>API specifications and test coverage for the Kubernetes MOOC project</p>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>🔧 Backend API</h2>
            <p>REST API service providing todo CRUD operations with PostgreSQL persistence, validation, and health monitoring.</p>
            <a href="api/todo-backend/" class="btn">View API Docs</a>
            <a href="api/todo-backend/openapi.json" class="btn secondary">OpenAPI JSON</a>
        </div>
        
        <div class="card">
            <h2>🎨 Frontend API</h2>
            <p>Frontend application with HTMX UI, image caching, and backend service integration for the complete user experience.</p>
            <a href="api/todo-app/" class="btn">View API Docs</a>
            <a href="api/todo-app/openapi.json" class="btn secondary">OpenAPI JSON</a>
        </div>
        
        <div class="card">
            <h2>📊 Test Coverage</h2>
            <p>Code coverage reports from the comprehensive test suite including unit tests, integration tests, and API contract validation.</p>
            <a href="coverage/" class="btn">View Coverage</a>
        </div>
        
        <div class="card">
            <h2>🚀 Project Info</h2>
            <p>Kubernetes MOOC course project demonstrating microservices architecture, CI/CD pipelines, and container orchestration.</p>
            <a href="https://github.com/rjpalt/KubernetesMOOC" class="btn">GitHub Repository</a>
        </div>
    </div>
    
    <div class="footer">
        <p>Generated automatically from main branch • Last updated: $timestamp</p>
    </div>
</body>
</html>""")
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    output_path.write_text(template.substitute(timestamp=timestamp))

def generate_coverage_index(output_path: Path):
    """Generate coverage reports index."""
    template = Template("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Test Coverage Reports</title>
    <link rel="stylesheet" href="../assets/styles.css">
</head>
<body>
    <h1>📊 Test Coverage Reports</h1>
    <div class="card">
        <h2>Backend Coverage</h2>
        <p>Test coverage for todo-backend microservice</p>
        <a href="../api/todo-backend/" class="btn">Backend API Docs</a>
    </div>
    <div class="card">
        <h2>Frontend Coverage</h2>
        <p>Test coverage for todo-app frontend service</p>
        <a href="../api/todo-app/" class="btn">Frontend API Docs</a>
    </div>
    <p><a href="../">← Back to Documentation Home</a></p>
</body>
</html>""")
    
    output_path.write_text(template.substitute())

def generate_css(output_path: Path):
    """Generate the main CSS file."""
    css_content = """
body { 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 1200px; margin: 0 auto; padding: 2rem;
    background: #fafafa; color: #333;
}

.header { text-align: center; margin-bottom: 3rem; }
.header h1 { color: #2c3e50; margin-bottom: 0.5rem; }
.header p { color: #7f8c8d; font-size: 1.1rem; }

.grid { 
    display: grid; 
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
    gap: 2rem; 
}

.card { 
    background: white; border-radius: 8px; padding: 2rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1); border: 1px solid #e1e8ed;
}

.card h2 { color: #2c3e50; margin-top: 0; }
.card p { color: #7f8c8d; line-height: 1.6; }

.btn {
    display: inline-block; padding: 0.75rem 1.5rem; 
    background: #3498db; color: white; text-decoration: none;
    border-radius: 4px; margin: 0.25rem 0.5rem 0.25rem 0;
    transition: background 0.2s;
}

.btn:hover { background: #2980b9; }
.btn.secondary { background: #95a5a6; }
.btn.secondary:hover { background: #7f8c8d; }

.footer { 
    text-align: center; margin-top: 3rem; padding-top: 2rem;
    border-top: 1px solid #e1e8ed; color: #7f8c8d;
}

/* Coverage page styles */
h1 { color: #2c3e50; }
"""
    output_path.write_text(css_content)

def main():
    """Generate the complete documentation site."""
    docs_dir = Path("docs")
    docs_dir.mkdir(exist_ok=True)
    
    # Create directory structure
    (docs_dir / "api" / "todo-backend").mkdir(parents=True, exist_ok=True)
    (docs_dir / "api" / "todo-app").mkdir(parents=True, exist_ok=True)
    (docs_dir / "coverage").mkdir(parents=True, exist_ok=True)
    (docs_dir / "assets").mkdir(parents=True, exist_ok=True)
    
    # Generate CSS
    generate_css(docs_dir / "assets" / "styles.css")
    
    # Generate Swagger UI pages
    generate_swagger_ui(
        docs_dir / "api" / "todo-backend" / "index.html",
        "Todo Backend API Documentation",
        "./openapi.json"
    )
    
    generate_swagger_ui(
        docs_dir / "api" / "todo-app" / "index.html", 
        "Todo Frontend API Documentation",
        "./openapi.json"
    )
    
    # Generate main pages
    generate_main_index(docs_dir / "index.html")
    
    # Generate coverage index if coverage artifacts exist
    if Path("coverage-artifacts").exists():
        generate_coverage_index(docs_dir / "coverage" / "index.html")
    
    print("✅ Documentation site generated successfully!")

if __name__ == "__main__":
    main()

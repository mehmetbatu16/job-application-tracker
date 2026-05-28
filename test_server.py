import http.server
import socketserver
import re
from pathlib import Path
import urllib.parse

USER_DATABASE = {}

class TrackerTestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith('/static/') or self.path == '/static/style.css':
            return super().do_GET()
            
        page_name = self.path.strip('/')
        if not page_name:
            page_name = 'index.html'
        elif not page_name.endswith('.html') and not '.' in page_name:
            page_name += '.html'
            
        p = Path('templates') / page_name
        if not p.exists():
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()
            return
            
        self.render_and_send(p, status_code=200)

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        fields = urllib.parse.parse_qs(post_data)
        
        username = fields.get('username', [''])[0]
        password = fields.get('password', [''])[0]
        
        if self.path == '/register':
            if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
                error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Password must contain at least one uppercase letter and one number!</div>"
                self.render_and_send(Path('templates/register.html'), error_message=error_html, status_code=200)
                return
                
            USER_DATABASE[username] = password
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
            
        if self.path == '/login':
            if username in USER_DATABASE and USER_DATABASE[username] == password:
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                return
            else:
                error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Invalid username or password!</div>"
                self.render_and_send(Path('templates/login.html'), error_message=error_html, status_code=200)
                return

        self.send_response(302)
        self.send_header('Location', '/')
        self.end_headers()

    def render_and_send(self, file_path, error_message="", status_code=200):
        html = file_path.read_text(encoding='utf-8')
        base_path = Path('templates/base.html')
        base = base_path.read_text(encoding='utf-8') if base_path.exists() else ''
        
        title_match = re.search(r'{% block title %}(.*?){% endblock %}', html)
        content_match = re.search(r'{% block content %}(.*?){% endblock %}', html, re.DOTALL)
        
        title = title_match.group(1) if title_match else 'Job Application Tracker'
        content = content_match.group(1) if content_match else html
        
        if error_message:
            content = error_message + content
        
        if base:
            res = re.sub(r'{% block title %}.*?{% endblock %}', title, base)
            res = re.sub(r'{% block content %}.*?{% endblock %}', content, res)
        else:
            res = html
            
        res = re.sub(r'{% if session.*?{% else %}.*?{% endif %}', '<a href="/login">Login</a><a href="/register">Register</a>', res, flags=re.DOTALL)
        res = re.sub(r'{%.*?%}', '', res)
        res = re.sub(r'{{.*?}}', '', res)
        
        self.send_response(status_code)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(res.encode('utf-8'))

if __name__ == '__main__':
    print("Server started successfully: http://127.0.0.1:5003")
    socketserver.TCPServer(('', 5003), TrackerTestHandler).serve_forever()
import http.server
import socketserver
import re
from pathlib import Path
import urllib.parse

USER_DATABASE = {}
USER_APPLICATIONS = {}
CURRENT_SESSION_USER = None

class TrackerTestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global CURRENT_SESSION_USER
        if self.path.startswith('/static/') or self.path == '/static/style.css':
            return super().do_GET()
            
        parsed_url = urllib.parse.urlparse(self.path)
        page_name = parsed_url.path.strip('/')
        
        if self.path == '/logout':
            CURRENT_SESSION_USER = None
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return

        if not page_name:
            page_name = 'index.html'
        elif page_name.startswith('dashboard') or 'dashboard' in page_name:
            if not CURRENT_SESSION_USER:
                self.send_response(302)
                self.send_header('Location', '/login')
                self.end_headers()
                return
            page_name = 'dashboard.html'
        elif not page_name.endswith('.html') and not '.' in page_name:
            page_name += '.html'
            
        p = Path('templates') / page_name
        if not p.exists():
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
            return
            
        self.render_and_send(p, status_code=200)

    def do_POST(self):
        global CURRENT_SESSION_USER
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        fields = urllib.parse.parse_qs(post_data)
        
        username = fields.get('username', [''])[0]
        password = fields.get('password', [''])[0]
        
        if self.path.startswith('/register'):
            if not re.search(r'[A-Z]', password) or not re.search(r'[0-9]', password):
                error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Password must contain at least one uppercase letter and one number!</div>"
                self.render_and_send(Path('templates/register.html'), error_message=error_html, status_code=200)
                return
                
            USER_DATABASE[username] = password
            if username not in USER_APPLICATIONS:
                USER_APPLICATIONS[username] = []
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return
            
        if self.path.startswith('/login'):
            if username in USER_DATABASE and USER_DATABASE[username] == password:
                CURRENT_SESSION_USER = username
                if CURRENT_SESSION_USER not in USER_APPLICATIONS:
                    USER_APPLICATIONS[CURRENT_SESSION_USER] = []
                self.send_response(302)
                self.send_header('Location', '/dashboard')
                self.end_headers()
                return
            else:
                error_html = "<div style='background:#e74c3c;color:#fff;padding:15px;border-radius:5px;margin-bottom:20px;font-weight:bold;text-align:center;'>Invalid username or password!</div>"
                self.render_and_send(Path('templates/login.html'), error_message=error_html, status_code=200)
                return

        if not CURRENT_SESSION_USER:
            self.send_response(302)
            self.send_header('Location', '/login')
            self.end_headers()
            return

        if 'delete' in self.path or 'remove' in self.path:
            parsed_url = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_url.query)
            app_idx = int(query_params.get('id', [-1])[0])
            user_apps = USER_APPLICATIONS.get(CURRENT_SESSION_USER, [])
            if 0 <= app_idx < len(user_apps):
                user_apps.pop(app_idx)
            self.send_response(302)
            self.send_header('Location', '/dashboard')
            self.end_headers()
            return

        company = fields.get('company', fields.get('company_name', ['']))[0]
        position = fields.get('position', [''])[0]
        status = fields.get('status', ['Applied'])[0]
        date = fields.get('date', ['2026-05-28'])[0]
        notes = fields.get('notes', [''])[0]

        if company or position:
            USER_APPLICATIONS[CURRENT_SESSION_USER].append({
                'company': company,
                'position': position,
                'status': status,
                'date': date,
                'notes': notes
            })

        self.send_response(302)
        self.send_header('Location', '/dashboard')
        self.end_headers()

    def render_and_send(self, file_path, error_message="", status_code=200):
        global CURRENT_SESSION_USER
        html = file_path.read_text(encoding='utf-8')
        base_path = Path('templates/base.html')
        base = base_path.read_text(encoding='utf-8') if base_path.exists() else ''
        
        title_match = re.search(r'{% block title %}(.*?){% endblock %}', html)
        content_match = re.search(r'{% block content %}(.*?){% endblock %}', html, re.DOTALL)
        
        title = title_match.group(1) if title_match else 'Job Application Tracker'
        content = content_match.group(1) if content_match else html
        
        if error_message:
            content = error_message + content
            
        if file_path.name == 'dashboard.html' and CURRENT_SESSION_USER:
            content = content.replace('Welcome, !', f'Welcome, {CURRENT_SESSION_USER}!')
            
            user_apps = USER_APPLICATIONS.get(CURRENT_SESSION_USER, [])
            table_rows = ""
            for idx, app in enumerate(user_apps):
                table_rows += f"""
                <tr class="job-row">
                    <td>{app['company']}</td>
                    <td>{app['position']}</td>
                    <td><span class="badge" style="background-color:#3498db; color:white; padding:5px 10px; border-radius:4px; font-weight:bold; display:inline-block;">{app['status']}</span></td>
                    <td>{app['date']}</td>
                    <td>{app['notes']}</td>
                    <td><form method="POST" action="/delete?id={idx}" style="margin:0;"><button type="submit" class="btn btn-danger btn-sm" style="background-color:#e74c3c; color:white; border:none; padding:5px 10px; border-radius:3px; cursor:pointer;">Delete</button></form></td>
                </tr>
                """
            
            if user_apps:
                content = re.sub(r'<tr>\s*<td[^>]*>.*?</td>\s*</tr>', table_rows, content, flags=re.DOTALL)

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
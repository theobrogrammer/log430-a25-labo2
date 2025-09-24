"""
Store manager application
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import os
from urllib.parse import parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
from views.template_view import show_main_menu, show_404_page
from views.user_view import show_user_form, register_user, remove_user
from views.product_view import show_product_form, register_product, remove_product
from views.order_view import show_order_form, register_order, remove_order
from views.report_view import show_highest_spending_users, show_best_sellers

class StoreManager(BaseHTTPRequestHandler):
    def do_GET(self):
        """ Handle GET requests received by the http.server """
        id = self.path.split("/")[-1]
        if self.path == "/" or self.path == "/home":
            self._send_html(show_main_menu())
            return
        if self.path == "/debug":
            self._send_html(self._debug_connections())
            return
        if self.path == "/users":
            self._send_html(show_user_form())
        elif self.path.startswith("/users/remove/"):
            response = remove_user(id)
            self._send_html(response)
        elif self.path == "/products":
            self._send_html(show_product_form())
        elif self.path.startswith("/products/remove/"):
            response = remove_product(id)
            self._send_html(response)
        elif self.path == "/orders":
            self._send_html(show_order_form())
        elif self.path.startswith("/orders/remove/"):
            response = remove_order(id)
            self._send_html(response)
        elif self.path == "/orders/reports/highest_spenders":
            self._send_html(show_highest_spending_users())
        elif self.path == "/orders/reports/best_sellers":
            self._send_html(show_best_sellers())
        elif "/assets" in self.path: # load assets such as images, CSS, etc.
            self.load_asset()      
        else:
            self._send_html(show_404_page(), status=404)

    def do_POST(self):
        """ Handle POST requests received by the http.server """
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode("utf-8")
        params = parse_qs(body)
        if self.path == "/users/add":
            response = register_user(params)
            self._send_html(response)
        elif self.path == "/products/add":
            response = register_product(params)
            self._send_html(response)
        elif self.path == "/orders/add":
            response = register_order(params)
            self._send_html(response)
        else:
            self._send_html(show_404_page(), status=404)

    def load_asset(self):
        """ Load assets from disk based on requested path, then send file contents as a response to the client """
        path_parts = self.path.split(".")
        extension = path_parts[1] if len(path_parts) >= 2 else None
        base_directory = os.path.dirname(__file__)
        with open(base_directory + self.path, "r") as file:
            css = "".join(file.readlines())
            self.send_response(200)
            self.send_header("Content-type", self.get_mimetype(extension))
            self.end_headers()
            self.wfile.write(css.encode("utf-8"))

    def get_mimetype(self, extension):
        """ Get mimetype (https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/MIME_types/Common_types) """
        if (extension == "html"):
            return "text/html"
        elif (extension == "css"):
            return "text/css"
        elif (extension == "js"):
            return "text/javascript"
        elif (extension == "svg"):
            return "image/svg+xml"
        else:
            return "application/octet-stream"

    def _send_html(self, html, status=200):
        """ Send given HTML string as a response to the client """
        self.send_response(status)
        self.send_header("Content-type", self.get_mimetype("html"))
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _debug_connections(self):
        """ Debug endpoint to test database connections """
        import os
        from dotenv import load_dotenv
        
        debug_output = ["<h1>Debug Connexions</h1>"]
        
        # Test config loading
        debug_output.append("<h2>1. Configuration</h2>")
        try:
            load_dotenv('../a.env')
            debug_output.append(f"<p>DB_HOST: {os.getenv('DB_HOST')}</p>")
            debug_output.append(f"<p>DB_PORT: {os.getenv('DB_PORT')}</p>")
            debug_output.append(f"<p>DB_NAME: {os.getenv('DB_NAME')}</p>")
            debug_output.append(f"<p>DB_USER: {os.getenv('DB_USER')}</p>")
            debug_output.append(f"<p>DB_PASS: {'***' if os.getenv('DB_PASS') else 'NON TROUVÉ'}</p>")
            debug_output.append(f"<p>REDIS_HOST: {os.getenv('REDIS_HOST')}</p>")
            debug_output.append(f"<p>REDIS_PORT: {os.getenv('REDIS_PORT')}</p>")
            debug_output.append(f"<p>REDIS_DB: {os.getenv('REDIS_DB')}</p>")
        except Exception as e:
            debug_output.append(f"<p style='color:red'>Erreur config: {e}</p>")
        
        # Test MySQL
        debug_output.append("<h2>2. Test MySQL</h2>")
        try:
            import mysql.connector
            import config
            conn = mysql.connector.connect(
                host=config.DB_HOST,
                port=config.DB_PORT,
                user=config.DB_USER,
                password=config.DB_PASS,
                database=config.DB_NAME
            )
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            result = cursor.fetchone()
            debug_output.append(f"<p style='color:green'>✓ MySQL OK - {result[0]} utilisateurs</p>")
            conn.close()
        except Exception as e:
            debug_output.append(f"<p style='color:red'>✗ MySQL Erreur: {e}</p>")
        
        # Test Redis
        debug_output.append("<h2>3. Test Redis</h2>")
        try:
            import redis
            import config
            r = redis.Redis(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB, decode_responses=True)
            r.ping()
            keys = r.keys("*")
            debug_output.append(f"<p style='color:green'>✓ Redis OK - {len(keys)} clés</p>")
        except Exception as e:
            debug_output.append(f"<p style='color:red'>✗ Redis Erreur: {e}</p>")
        
        # Test SQLAlchemy
        debug_output.append("<h2>4. Test SQLAlchemy</h2>")
        try:
            from sqlalchemy import text
            from db import get_sqlalchemy_session
            session = get_sqlalchemy_session()
            result = session.execute(text("SELECT COUNT(*) FROM users"))
            count = result.fetchone()[0]
            debug_output.append(f"<p style='color:green'>✓ SQLAlchemy OK - {count} utilisateurs</p>")
            session.close()
        except Exception as e:
            debug_output.append(f"<p style='color:red'>✗ SQLAlchemy Erreur: {e}</p>")
        
        debug_output.append("<p><a href='/'>Retour</a></p>")
        return "".join(debug_output)

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 5000), StoreManager)
    print("Server running on http://0.0.0.0:5000")
    server.serve_forever()

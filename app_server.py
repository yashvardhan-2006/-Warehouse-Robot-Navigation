import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8000

class QuietHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        # Suppress routine GET request logs for a cleaner terminal
        pass

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    handler = QuietHTTPRequestHandler
    
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        url = f"http://localhost:{PORT}"
        print("==================================================================")
        print("AMR Warehouse Robot Pathfinding Visualizer Web Application")
        print("==================================================================")
        print(f"Server is listening at: {url}")
        print("Press Ctrl+C to stop the server.")
        print("==================================================================")
        
        try:
            webbrowser.open(url)
        except Exception:
            pass

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
            sys.exit(0)

if __name__ == "__main__":
    main()

import http.server
import random
import time
from prometheus_client import start_http_server,Counter,Gauge



# 'app_name','endpoint' are labels. 
REQUEST_COUNT = Counter('app_requests_count','total all http request [count]',['app_name','endpoint'])
RANDOM_COUNT = Counter('app_random_count','increment counter by random value')

REQUEST_INPROGRESS = Gauge('app_requests_in_progress','number of application requests in progress')
REQUEST_LAST_SERVED = Gauge('app_last_served','Time application was last served')

class HandleRequests(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        REQUEST_COUNT.labels('prom_python_app',self.path).inc()
        RANDOM_COUNT.inc(random.random()*10)
        
        REQUEST_INPROGRESS.inc()
        time.sleep(5)

        self.send_response(200)
        self.send_header("Content-type","text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head>Header2 </head><body>Content2</body></html>","utf-8"))
        self.wfile.close()
        REQUEST_LAST_SERVED.set(time.time())
        REQUEST_INPROGRESS.dec()

if __name__ == "__main__":
    start_http_server(8001)
    server = http.server.HTTPServer(('localhost', 8000), HandleRequests)
    server.serve_forever()
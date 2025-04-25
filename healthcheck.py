import yaml, time, threading, logging, socket, json, os, subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

CONFIG_FILE = "/app/config.yaml"
CHECK_INTERVAL = 60
HEALTH_PORT = 8000
SUPERVISOR_DIR = "/etc/supervisor/conf.d"
stream_health = {}
lock = threading.Lock()

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

def check_udp_port(host: str, port: int) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((host, port))
        sock.settimeout(3)
        data, _ = sock.recvfrom(2048)
        sock.close()
        return bool(data)
    except Exception:
        return False

def check_srt_port(host: str, port: int, mode: str) -> bool:
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        if mode == "listener":
            sock.bind((host, port))
            sock.listen(1)
        else:
            sock.connect((host, port))
        sock.close()
        return True
    except Exception:
        return False

def extract_info(url: str):
    parts = urlparse(url)
    host = parts.hostname or "0.0.0.0"
    port = parts.port or 9000
    return host, port

def reload_config():
    try:
        with open(CONFIG_FILE) as f:
            config = yaml.safe_load(f) or {}
        for f in os.listdir(SUPERVISOR_DIR):
            if f.endswith(".conf") and not f.startswith("healthcheck"):
                os.remove(os.path.join(SUPERVISOR_DIR, f))
        for s in config.get("streams", []):
            name = s["name"]
            output = s["output"]
            input_ = s["input"]
            subprocess.run(["python3", "/app/restreamer.py"])
        subprocess.call(["supervisorctl", "reread"])
        subprocess.call(["supervisorctl", "update"])
        return {"status": "reloaded"}
    except Exception as exc:
        return {"error": str(exc)}

def health_loop():
    while True:
        try:
            with open(CONFIG_FILE) as f:
                config = yaml.safe_load(f) or {}
        except Exception as e:
            logging.error("Error loading config.yaml: %s", e)
            time.sleep(CHECK_INTERVAL)
            continue

        for s in config.get("streams", []):
            name = s["name"]
            input_url = s["input"]
            output_url = s["output"]

            if input_url.startswith("srt://"):
                host, port = extract_info(input_url)
                status = check_srt_port(host, port, mode="listener")
            elif output_url.startswith("srt://"):
                host, port = extract_info(output_url)
                status = check_srt_port(host, port, mode="caller")
            else:
                _, port = extract_info(output_url)
                status = check_udp_port("0.0.0.0", port)

            with lock:
                stream_health[name] = {
                    "status": "healthy" if status else "unhealthy",
                    "last_checked": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "output": output_url
                }

        time.sleep(CHECK_INTERVAL)

class Handler(BaseHTTPRequestHandler):
    def _send_json(self, data):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write((json.dumps(data, indent=2) + "\n").encode())

    def do_GET(self):
        if self.path == "/healthz":
            with lock:
                self._send_json(stream_health)
        elif self.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            with lock:
                for name, info in stream_health.items():
                    metric = f'stream_health{{name="{name}"}} {1 if info["status"] == "healthy" else 0}'
                    self.wfile.write(metric.encode())
        elif self.path == "/swagger":
            try:
                with open("/app/swagger.yaml") as f:
                    spec = f.read()
                self.send_response(200)
                self.send_header("Content-Type", "application/x-yaml")
                self.end_headers()
                self.wfile.write(spec.encode())
            except FileNotFoundError:
                self.send_error(404)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/reload":
            result = reload_config()
            self._send_json(result)
        else:
            self.send_error(404)

def main():
    threading.Thread(target=health_loop, daemon=True).start()
    HTTPServer(("", HEALTH_PORT), Handler).serve_forever()

if __name__ == "__main__":
    main()
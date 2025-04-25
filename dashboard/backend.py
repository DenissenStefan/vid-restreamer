from flask import Flask, request, jsonify, send_from_directory
import yaml, os, requests

app = Flask(__name__)
CONFIG_PATH = "/app/config.yaml"

@app.route("/")
def index():
    return send_from_directory("/app/dashboard", "ui.html")

@app.route("/config", methods=["GET"])
def get_config():
    with open(CONFIG_PATH) as f:
        return f.read(), 200, {"Content-Type": "text/plain"}

@app.route("/config", methods=["PUT"])
def update_config():
    with open(CONFIG_PATH, "w") as f:
        f.write(request.data.decode())
    return "OK", 200

@app.route("/stream/<name>", methods=["DELETE"])
def remove_stream(name):
    with open(CONFIG_PATH) as f:
        config = yaml.safe_load(f)
    config['streams'] = [s for s in config.get('streams', []) if s['name'] != name]
    with open(CONFIG_PATH, "w") as f:
        yaml.safe_dump(config, f)
    os.system("curl -X POST http://localhost:8000/reload")
    return jsonify({"status": f"stream '{name}' removed and config reloaded"})

@app.route("/reload", methods=["POST"])
def reload():
    res = os.system("curl -X POST http://localhost:8000/reload")
    return jsonify({"status": "reloaded" if res == 0 else "error"})

@app.route("/healthz")
def proxy_health():
    try:
        resp = requests.get("http://localhost:8000/healthz", timeout=2)
        data = resp.text.strip().replace("%", "")  # remove trailing % if any
        return jsonify(resp.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 503

if __name__ == "__main__":
    print("📡 Flask dashboard running on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000)

from flask import Flask, request, render_template_string, abort
import logging, datetime, os

# Log file (stored next to the script)
LOG_FILE = os.path.join(os.path.dirname(__file__), "decoy_access.log")

# Simple logging setup: each access is one JSON-ish line
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(message)s'
)

app = Flask(__name__)

# Minimal decoy HTML (non-malicious)
DECOY_HTML = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Company Portal</title>
    <style>
      body{font-family: Arial, Helvetica, sans-serif; margin:2rem;}
      .card{border:1px solid #ddd; padding:1rem; border-radius:6px; max-width:600px;}
      h1{margin-top:0;}
    </style>
  </head>
  <body>
    <div class="card">
      <h1>Welcome</h1>
      <p>This is an internal demo portal. If you reached this page and you are not authorized, your activity is being logged.</p>
      <p><small>Contact: security@example.local</small></p>
    </div>
  </body>
</html>
"""

def log_visit():
    entry = {
        "time_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "ip": request.remote_addr,
        "method": request.method,
        "path": request.path,
        "user_agent": request.headers.get("User-Agent", ""),
        "query": dict(request.args)
    }
    # Write a simple single-line JSON-like entry
    logging.info(repr(entry))

@app.route("/", methods=["GET","POST"])
def index():
    log_visit()
    return render_template_string(DECOY_HTML)

# A safe admin endpoint to read the log, reachable only from localhost
@app.route("/__view-logs-localonly")
def view_logs():
    # Prevent remote access to logs by allowing only local requests
    if request.remote_addr not in ("127.0.0.1", "::1"):
        abort(403)
    if not os.path.exists(LOG_FILE):
        return "No logs yet.", 200
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        return "<pre>{}</pre>".format(f.read()), 200

if __name__ == "__main__":
    # WARNING: built-in Flask server is for development only.
    # Listen on all interfaces in internal lab; use a firewall to restrict exposure.
    app.run(host="0.0.0.0", port=5000, debug=False)

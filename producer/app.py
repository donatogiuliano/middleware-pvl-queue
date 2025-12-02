import os
import json
import uuid
import time
import datetime
from flask import Flask, request, render_template_string, redirect, url_for, flash, jsonify, Response
import redis

# --- CONFIGURATION ---
POLLING_INTERVAL_MS = 1000  # Update UI every 1 second

# --- REDIS CONFIGURATION ---
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
QUEUE_NAME = 'potentiation_queue'
RESULTS_KEY = 'latest_results'
CONTROL_KEY = 'consumer_control'

try:
    r = redis.Redis(host=REDIS_HOST, port=6379, db=0, decode_responses=True)
    r.ping()
    # Set default control status
    if r.get(CONTROL_KEY) is None:
        r.set(CONTROL_KEY, 'RUNNING')
    print("INFO: Producer successfully connected to Redis.")
except Exception as e:
    print(f"ERROR: Producer could not reach Redis: {e}")
    r = None

app = Flask(__name__)
app.secret_key = b'secret_key_simple_pvl' 

# --- API ---
@app.route('/status_api', methods=['GET'])
def status_api():
    if r:
        queue_count = r.llen(QUEUE_NAME)
        # Get visual items (first 10)
        raw_items = r.lrange(QUEUE_NAME, 0, 9)
        queue_items = []
        for item in raw_items:
            try:
                data = json.loads(item)
                queue_items.append(data)
            except:
                pass

        results = r.hgetall(RESULTS_KEY)
        processed_results = []
        for key, value in results.items():
            obj = json.loads(value)
            if 'timestamp' not in obj:
                obj['timestamp'] = "N/A"
            processed_results.append(obj)
        processed_results.sort(key=lambda x: x.get('timestamp', '0'), reverse=True)
        
        return jsonify({
            'queue_count': queue_count,
            'queue_items': queue_items,
            'is_running': r.get(CONTROL_KEY) == 'RUNNING',
            'results': processed_results[:5] 
        })
    return jsonify({'queue_count': 0, 'queue_items': [], 'is_running': False, 'results': []})

@app.route('/control/<action>', methods=['POST'])
def control(action):
    if r:
        if action == 'stop':
            r.set(CONTROL_KEY, 'STOPPED')
        elif action == 'start':
            r.set(CONTROL_KEY, 'RUNNING')
    return redirect(url_for('index'))

@app.route('/export', methods=['GET'])
def export_queue():
    if r:
        queue_content = [json.loads(i) for i in r.lrange(QUEUE_NAME, 0, -1)]
        results_content = [json.loads(i) for i in r.hgetall(RESULTS_KEY).values()]
        data = {"queue": queue_content, "history": results_content}
        return Response(
            json.dumps(data, indent=4),
            mimetype='application/json',
            headers={'Content-Disposition': 'attachment;filename=export.json'}
        )
    return "Redis Error", 500

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit_task():
    try:
        x = int(request.form.get('number_x'))
        task = {'id': str(uuid.uuid4()), 'x': x, 'timestamp': time.time()}
        if r:
            r.lpush(QUEUE_NAME, json.dumps(task))
    except:
        pass
    return redirect(url_for('index'))


# --- UI TEMPLATE (ENGLISH) ---
HTML_TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Distributed System Demo</title>
<style>
    :root {
        --bg: #f1f5f9;
        --card-bg: #ffffff;
        --primary: #2563eb;
        --queue-color: #f59e0b;
        --success: #16a34a;
        --danger: #dc2626;
        --text: #334155;
    }

    body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); padding: 20px; display: flex; flex-direction: column; align-items: center; }
    h1 { color: #0f172a; margin-bottom: 5px; }
    p.sub { color: #64748b; margin-top: 0; margin-bottom: 30px; }

    .main-container { max-width: 1000px; width: 100%; }

    /* ROW 1: Producer & Consumer */
    .top-row { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px; }
    
    .card { background: var(--card-bg); border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); border: 1px solid #e2e8f0; position: relative; overflow: hidden; }
    .card h2 { margin-top: 0; font-size: 1.1rem; color: #475569; text-transform: uppercase; letter-spacing: 1px; }
    
    .producer { border-top: 5px solid var(--primary); }
    .consumer { border-top: 5px solid var(--success); }

    /* Inputs & Buttons */
    input[type=number] { padding: 10px; border-radius: 6px; border: 1px solid #cbd5e1; width: 60%; font-size: 1rem; }
    .btn { padding: 10px 15px; border-radius: 6px; border: none; font-weight: bold; cursor: pointer; color: white; transition: 0.2s; }
    .btn-submit { background: var(--primary); width: 35%; }
    .btn-submit:hover { background: #1d4ed8; }
    
    .ctrl-grp { display: flex; gap: 10px; margin-top: 10px; }
    .btn-stop { background: var(--danger); flex: 1; }
    .btn-start { background: var(--success); flex: 1; }

    /* ROW 2: The Visual Queue */
    .queue-section {
        background: var(--card-bg);
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        border: 2px dashed var(--queue-color);
        margin-bottom: 20px;
        overflow-x: auto;
    }
    
    .queue-header { display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px; }
    .queue-title-group h2 { margin: 0; color: #475569; text-transform: uppercase; letter-spacing: 1px; font-size: 1.1rem; }
    .queue-update-info { font-size: 0.8rem; color: #94a3b8; margin-top: 2px; font-style: italic; }
    .queue-stats { font-weight: bold; color: var(--queue-color); font-size: 1.2rem; }
    
    /* Queue Track */
    .queue-track {
        display: flex;
        flex-direction: row-reverse; 
        justify-content: flex-end;
        align-items: center;
        gap: 10px;
        min-height: 80px;
        background: #fffbeb;
        border-radius: 8px;
        padding: 10px;
    }

    .q-item {
        background: white;
        border: 2px solid var(--queue-color);
        color: var(--text);
        border-radius: 8px;
        width: 60px;
        height: 60px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: slideIn 0.3s ease-out;
        flex-shrink: 0;
    }
    .q-item small { font-size: 0.6rem; color: #94a3b8; font-weight: normal; }
    .q-item span { font-size: 1.2rem; }

    .empty-msg { width: 100%; text-align: center; color: #94a3b8; font-style: italic; }

    @keyframes slideIn { from { transform: scale(0.5); opacity: 0; } to { transform: scale(1); opacity: 1; } }

    /* Results */
    .history { margin-top: 20px; max-width: 800px; width: 100%; }
    .res-row { 
        background: white; border-bottom: 1px solid #e2e8f0; padding: 10px; 
        display: flex; justify-content: space-between; font-family: monospace;
    }
    .res-row:first-child { border-top-left-radius: 8px; border-top-right-radius: 8px; }
    .res-row:last-child { border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }

</style>
</head>
<body>

    <div class="main-container">
        <div style="text-align:center;">
            <h1>Resilient Task Processing with Redis</h1>
            <p class="sub">Demonstration of a durable Producer-Consumer architecture.</p>
        </div>

        <div class="top-row">
            <div class="card producer">
                <h2>Task Producer</h2>
                <p>Generates a calculation task (x²).</p>
                <form method="POST" action="/submit">
                    <input type="number" name="number_x" value="10" placeholder="Number..." required>
                    <button class="btn btn-submit">Submit Task ➔</button>
                </form>
            </div>

            <div class="card consumer">
                <h2>Worker (Consumer)</h2>
                <div id="status-badge" style="margin-bottom:10px;">Status: <strong>Checking...</strong></div>
                <p style="font-size:0.9rem">Simulated Latency: 6s per task.</p>
                
                <div class="ctrl-grp">
                    <form action="/control/stop" method="post" style="flex:1"><button class="btn btn-stop">🛑 Stop</button></form>
                    <form action="/control/start" method="post" style="flex:1"><button class="btn btn-start">▶ Start</button></form>
                </div>
            </div>
        </div>

        <div class="queue-section">
            <div class="queue-header">
                <div class="queue-title-group">
                    <h2>Redis Persistent Queue</h2>
                    <div class="queue-update-info">Live View: updates every 1s</div>
                </div>
                <div class="queue-stats">Buffered: <span id="q-count-val">0</span></div>
            </div>
            
            <div class="queue-track" id="visual-queue">
                <div class="empty-msg">Queue is empty.</div>
            </div>
            
            <div style="text-align:right; margin-top:5px;">
                <a href="/export" style="font-size:0.8rem; color:#64748b;">⬇ Download JSON</a>
            </div>
        </div>
        
        <h3>Processing History (Last 5)</h3>
        <div class="history" id="results-list"></div>
    </div>

    <script>
        function update() {
            fetch('/status_api')
            .then(r => r.json())
            .then(data => {
                // 1. Queue Counter
                document.getElementById('q-count-val').innerText = data.queue_count;

                // 2. Queue Visuals
                const track = document.getElementById('visual-queue');
                track.innerHTML = ''; 
                
                if (data.queue_items.length === 0) {
                    track.innerHTML = '<div class="empty-msg">Queue is empty.</div>';
                } else {
                    data.queue_items.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'q-item';
                        div.innerHTML = `<small>x=</small><span>${item.x}</span>`;
                        div.title = `ID: ${item.id}`;
                        track.appendChild(div);
                    });
                    
                    if (data.queue_count > 10) {
                        const more = document.createElement('div');
                        more.style.color = '#94a3b8';
                        more.innerText = `+${data.queue_count - 10} more...`;
                        track.appendChild(more);
                    }
                }

                // 3. Status
                const badge = document.getElementById('status-badge');
                if (data.is_running) {
                    badge.innerHTML = 'Status: <span style="color:var(--success)">● Active</span>';
                } else {
                    badge.innerHTML = 'Status: <span style="color:var(--danger)">● Paused</span>';
                }

                // 4. Results
                const hist = document.getElementById('results-list');
                hist.innerHTML = '';
                if(data.results.length === 0) hist.innerHTML = '<div class="res-row" style="color:#aaa">No results yet</div>';
                
                data.results.forEach(res => {
                    const row = document.createElement('div');
                    row.className = 'res-row';
                    row.innerHTML = `<span>[${res.timestamp}] ${res.x}²</span> <span>= <strong>${res.result}</strong></span>`;
                    hist.appendChild(row);
                });
            });
        }
        
        setInterval(update, 1000); 
        update();
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
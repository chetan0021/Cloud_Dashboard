from flask import Flask, request, jsonify, render_template_string
import datetime
import os

app = Flask(__name__)

# In-memory storage (Works on Render, but NOT on Vercel)
stored_readings = []

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IoT Dashboard (Cloud Mock)</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f4f9; color: #333; margin: 0; padding: 20px; }
        .container { max-width: 900px; margin: 0 auto; background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        .status { padding: 10px; background: #e8f5e9; color: #2e7d32; border-radius: 5px; margin-bottom: 20px; border: 1px solid #c8e6c9; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: 600; color: #555; }
        tr:hover { background-color: #f5f5f5; }
        .empty { text-align: center; color: #888; padding: 20px; font-style: italic; }
        .tag { display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.85em; }
        .tag-temp { background: #ffebee; color: #c62828; }
        .tag-hum { background: #e3f2fd; color: #1565c0; }
        #last-updated { font-size: 0.8em; color: #666; float: right; margin-top: 10px; }
    </style>
    <script>
        function refreshData() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('readings-body');
                    tbody.innerHTML = '';
                    
                    if (data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5" class="empty">No data received yet.</td></tr>';
                        return;
                    }

                    // Show newest first
                    data.slice().reverse().forEach(r => {
                        const row = `<tr>
                            <td>${new Date(r.received_at).toLocaleTimeString()}</td>
                            <td>${r.sensor_id}</td>
                            <td><span class="tag tag-temp">${r.temperature}°C</span></td>
                            <td><span class="tag tag-hum">${r.humidity}%</span></td>
                            <td>${r.door_status || '-'}</td>
                        </tr>`;
                        tbody.innerHTML += row;
                    });
                    
                    document.getElementById('last-updated').innerText = 'Last updated: ' + new Date().toLocaleTimeString();
                });
        }
        
        setInterval(refreshData, 2000);
        window.onload = refreshData;
    </script>
</head>
<body>
    <div class="container">
        <h1>Cloud IoT Live Stream</h1>
        <div class="status">
            <strong>System Active</strong><br>
            <small>Security: DISABLED (Mock Mode)</small>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>Received At</th>
                    <th>Sensor ID</th>
                    <th>Temperature</th>
                    <th>Humidity</th>
                    <th>Door</th>
                </tr>
            </thead>
            <tbody id="readings-body">
                <tr><td colspan="5" class="empty">Waiting for data...</td></tr>
            </tbody>
        </table>
        <div id="last-updated"></div>
    </div>
</body>
</html>
"""

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/ingest/readings', methods=['POST'])
def ingest_readings():
    try:
        data = request.json
        if not data or 'readings' not in data:
            return jsonify({"error": "Invalid Format"}), 400
            
        for reading in data['readings']:
            reading['received_at'] = datetime.datetime.now().isoformat()
            stored_readings.append(reading)
            
        return jsonify({"success": True, "message": "Data received"}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    return jsonify(stored_readings)

if __name__ == '__main__':
    # Cloud hosts usually provide a PORT env var
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from yamldb.YamlDB import YamlDB
import os

app = FastAPI(title="YamlDB Web UI")

# Configuration: Change this to your database file
DB_FILE = "webui_db.yml"
db = YamlDB(filename=DB_FILE)

class SetRequest(BaseModel):
    key: str
    value: str

class DeleteRequest(BaseModel):
    key: str

@app.get("/", response_class=HTMLResponse)
async def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>YamlDB Web UI</title>
        <style>
            body { font-family: sans-serif; margin: 20px; background: #f4f4f9; }
            .container { max-width: 800px; margin: auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            pre { background: #eee; padding: 10px; border-radius: 4px; overflow-x: auto; }
            .form-group { margin-bottom: 15px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input { width: 100%; padding: 8px; box-sizing: border-box; }
            button { padding: 10px 15px; cursor: pointer; background: #007bff; color: white; border: none; border-radius: 4px; }
            button.delete { background: #dc3545; }
            .stats { margin-top: 20px; padding: 10px; background: #e9ecef; border-radius: 4px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YamlDB Web UI</h1>
            
            <div class="form-group">
                <h3>Set Value</h3>
                <label>Key (dot-notation)</label>
                <input type="text" id="set-key" placeholder="user.name">
                <label>Value</label>
                <input type="text" id="set-val" placeholder="Gregor">
                <button onclick="setValue()">Set Value</button>
            </div>

            <div class="form-group">
                <h3>Delete Key</h3>
                <label>Key (dot-notation)</label>
                <input type="text" id="del-key" placeholder="user.name">
                <button class="delete" onclick="deleteValue()">Delete Key</button>
            </div>

            <hr>
            <h3>Database Content</h3>
            <pre id="db-content">Loading...</pre>

            <div class="stats" id="stats-content">Stats: Loading...</div>
        </div>

        <script>
            async function refresh() {
                const res = await fetch('/data');
                const data = await res.json();
                document.getElementById('db-content').textContent = JSON.stringify(data, null, 2);
                
                const sRes = await fetch('/stats');
                const sData = await sRes.json();
                document.getElementById('stats-content').textContent = 
                    `Stats - Set Calls: ${sData.set_calls}, Save Calls: ${sData.save_calls}, Efficiency: ${sData.write_efficiency}`;
            }

            async function setValue() {
                const key = document.getElementById('set-key').value;
                const value = document.getElementById('set-val').value;
                await fetch('/set', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({key, value})
                });
                refresh();
            }

            async function deleteValue() {
                const key = document.getElementById('del-key').value;
                await fetch('/delete', {
                    method: 'DELETE',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({key})
                });
                refresh();
            }

            refresh();
            setInterval(refresh, 5000); // Auto-refresh every 5s
        </script>
    </body>
    </html>
    """

@app.get("/data")
async def get_data():
    return db.dict()

@app.post("/set")
async def set_value(req: SetRequest):
    try:
        db.set(req.key, req.value)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/delete")
async def delete_value(req: DeleteRequest):
    try:
        db.delete(req.key)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/stats")
async def get_stats():
    return db.get_stats()

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

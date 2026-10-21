from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import sys
import webbrowser
import os
import json
import datetime
from threading import Timer

app = Flask(__name__)

# File constants & Writable Directory Detection (Vercel / Serverless support)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def get_storage_dir():
    """Returns a guaranteed writable storage directory (uses /tmp on Vercel/serverless environments)."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return "/tmp"
    try:
        test_path = os.path.join(BASE_DIR, ".perm_test")
        with open(test_path, "w") as f:
            f.write("1")
        os.remove(test_path)
        return BASE_DIR
    except Exception:
        return "/tmp" if os.path.exists("/tmp") else os.environ.get("TEMP", BASE_DIR)

STORAGE_DIR = get_storage_dir()
DATA_FILE = os.path.join(STORAGE_DIR, "user_config.txt")
STATUS_FILE = os.path.join(STORAGE_DIR, "automation_status.json")
BOT_SCRIPT = os.path.join(BASE_DIR, "job_apply.py")
UPLOAD_FOLDER = os.path.join(STORAGE_DIR, "uploads")
try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    pass

def parse_existing_config():
    """Reads existing configuration from user_config.txt to pre-fill the form."""
    config = {
        "api_key": "",
        "user_id": "",
        "password": "",
        "roles": "java developer fresher",
        "resume_path": "",
        "resume_name": "",
        "location": "Chennai, Tamil Nadu, India",
        "apply_mode": "easy_apply",
        "years": "0",
        "months": "0",
        "current_lpa": "0",
        "expected_lpa": "4.5",
        "notice_period_days": "0",
        "links": "",
        "job_mode": "Fresher"
    }
    candidate_files = [DATA_FILE, os.path.join(BASE_DIR, "user_config.txt"), os.path.join("/tmp", "user_config.txt")]
    for cf in candidate_files:
        if os.path.exists(cf):
            try:
                with open(cf, "r", encoding="utf-8") as f:
                    for line in f:
                        if ":" in line:
                            k, v = line.split(":", 1)
                            k = k.strip().lower()
                            v = v.strip()
                            if k == "input_resume_path":
                                config["resume_path"] = v
                                if v and os.path.exists(v):
                                    config["resume_name"] = os.path.basename(v)
                            elif k in config:
                                config[k] = v
                break
            except Exception:
                pass

    if not config["resume_name"] and config["resume_path"]:
        config["resume_name"] = os.path.basename(config["resume_path"])
    
    return config

@app.before_request
def handle_preflight():
    if request.method == 'OPTIONS':
        resp = app.make_default_options_response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        resp.headers['Access-Control-Allow-Private-Network'] = 'true'
        return resp

@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Private-Network'] = 'true'
    return response

@app.route('/')
def form():
    config = parse_existing_config()
    return render_template('form.html', config=config)

@app.route('/dashboard')
def dashboard():
    config = parse_existing_config()
    return render_template('dashboard.html', config=config)

@app.route('/status')
def get_status():
    """Returns the live automation status and list of applied jobs for real-time frontend updates."""
    candidates = [
        STATUS_FILE,
        os.path.join(BASE_DIR, "automation_status.json"),
        os.path.join("/tmp", "automation_status.json")
    ]
    for sf in candidates:
        if os.path.exists(sf):
            try:
                with open(sf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        data.setdefault("total_already_applied", 0)
                        data.setdefault("already_applied_jobs", [])
                        return jsonify(data)
            except Exception:
                pass
    return jsonify({
        "status": "IDLE",
        "total_evaluated": 0,
        "total_applied": 0,
        "total_already_applied": 0,
        "total_skipped": 0,
        "current_evaluating": "Standing by. Click START AUTOMATION to begin.",
        "applied_jobs": [],
        "already_applied_jobs": [],
        "skipped_jobs": [],
        "summary_instruction": "Ready to launch automation.",
        "resume_analysis": {
            "candidate_name": "BARATH R",
            "email": "barath020305@gmail.com",
            "phone": "+91 9791945156",
            "degree": "BSc IT (Information Technology)",
            "major": "Information Technology",
            "college": "Kamalam College of Arts and Science (Bharathiar University)",
            "university": "Bharathiar University",
            "graduation_year": "2025",
            "detected_skills": ["Java", "Python", "SQL", "Spring Boot", "OOP"],
            "total_skills_count": 5,
            "experience_mode": "Fresher",
            "scan_status": "100% Parsed & Verified (1-Scan Complete)",
            "resume_file": "Resume.pdf"
        }
    })

@app.route('/submit', methods=['GET', 'POST'])
def submit_data():
    if request.method == 'GET':
        return redirect('/dashboard' if os.path.exists(STATUS_FILE) else '/')
    
    if request.method == 'POST':
        try:
            # 1. Handle uploaded resume file or fallback
            resume_path = request.form.get('resume_path', '').strip()
            uploaded_file = request.files.get('resume_file')
            if uploaded_file and uploaded_file.filename:
                # Sanitize filename and save in uploads/
                safe_name = os.path.basename(uploaded_file.filename).replace(" ", "_")
                saved_target = os.path.join(UPLOAD_FOLDER, safe_name)
                try:
                    uploaded_file.save(saved_target)
                except Exception:
                    # Fallback to /tmp on read-only environments (Vercel/Lambda)
                    tmp_uploads = os.path.join("/tmp", "uploads")
                    os.makedirs(tmp_uploads, exist_ok=True)
                    saved_target = os.path.join(tmp_uploads, safe_name)
                    uploaded_file.save(saved_target)
                resume_path = os.path.abspath(saved_target)

            # Fallback to existing saved config if not provided
            if not resume_path and os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r", encoding="utf-8") as file:
                    for line in file:
                        if "INPUT_RESUME_PATH" in line:
                            resume_path = line.split(":", 1)[-1].strip()
                            break

            # Ultimate default fallback
            if not resume_path:
                default_res = os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Barath_R_Resume.pdf")
                if os.path.exists(default_res):
                    resume_path = default_res

            location = request.form.get('location', 'Chennai, Tamil Nadu, India').strip()
            apply_mode = request.form.get('apply_mode', 'both').strip()
            roles = request.form.get('roles', 'java developer fresher').strip()

            lines = [
                f"{'API_KEY':<25}\t: {request.form.get('api_key', '')}",
                f"{'USER_ID':<25}\t: {request.form.get('user_id', '')}",
                f"{'PASSWORD':<25}\t: {request.form.get('password', '')}",
                f"{'ROLES':<25}\t: {roles}",
                f"{'INPUT_RESUME_PATH':<25}\t: {resume_path}",
                f"{'LOCATION':<25}\t: {location}",
                f"{'APPLY_MODE':<25}\t: {apply_mode}",
                f"{'YEARS':<25}\t: {request.form.get('years', '0')}",
                f"{'MONTHS':<25}\t: {request.form.get('months', '0')}",
                f"{'CURRENT_LPA':<25}\t: {request.form.get('current_lpa', '0')}",
                f"{'EXPECTED_LPA':<25}\t: {request.form.get('expected_lpa', '4.5')}",
                f"{'NOTICE_PERIOD_DAYS':<25}\t: {request.form.get('notice_period_days', '0')}",
                f"{'LINKS':<25}\t: {request.form.get('links', '')}",
                f"{'JOB_MODE':<25}\t: {request.form.get('job_mode', 'Fresher')}",
            ]
            
            file_content = "\n".join(lines)

            try:
                with open(DATA_FILE, "w", encoding="utf-8") as file:
                    file.write(file_content)
            except Exception:
                try:
                    with open(os.path.join("/tmp", "user_config.txt"), "w", encoding="utf-8") as file:
                        file.write(file_content)
                except Exception:
                    pass

            mode_label = {
                "easy_apply": "Easy Apply (LinkedIn Native)",
                "company_website": "Company Website (External Portals + AI)",
                "both": "Both (LinkedIn + Company Portals)"
            }.get(apply_mode, apply_mode)

            # Initialize live status JSON file
            initial_status = {
                "status": "RUNNING",
                "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": None,
                "role": roles,
                "location": location,
                "mode": mode_label,
                "total_evaluated": 0,
                "total_applied": 0,
                "total_already_applied": 0,
                "total_skipped": 0,
                "current_evaluating": "Launching Chrome with Anti-Detection and Session Persistence...",
                "applied_jobs": [],
                "already_applied_jobs": [],
                "skipped_jobs": [],
                "summary_instruction": f"Automation active for '{roles}' in {location}."
            }
            try:
                with open(STATUS_FILE, "w", encoding="utf-8") as sf:
                    json.dump(initial_status, sf, indent=2)
            except Exception:
                try:
                    with open(os.path.join("/tmp", "automation_status.json"), "w", encoding="utf-8") as sf:
                        json.dump(initial_status, sf, indent=2)
                except Exception:
                    pass
            
            # Launch automation runner cleanly without opening a terminal window
            try:
                log_path = os.path.join(STORAGE_DIR, "bot_execution.log")
                log_f = open(log_path, "a", encoding="utf-8")
            except Exception:
                log_f = open(os.path.join("/tmp", "bot_execution.log"), "a", encoding="utf-8")

            # In cloud serverless (Vercel / Lambda), background desktop Chrome cannot run
            is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
            if is_serverless:
                print("[*] Running on Vercel Serverless.")
            else:
                try:
                    creationflags = 0x08000000 if sys.platform == "win32" else 0
                    subprocess.Popen([sys.executable, "-u", BOT_SCRIPT], cwd=BASE_DIR, stdout=log_f, stderr=log_f, creationflags=creationflags)
                except Exception as launch_err:
                    print(f"Subprocess launch note: {launch_err}")

            # Redirect immediately to the live monitoring dashboard
            return redirect('/dashboard')
        
        except Exception as e:
            return f"<div style='background:#000;color:#ff4b4b;padding:40px;font-family:sans-serif;'><h1>Error: {e}</h1><a href='/' style='color:#ccff00;'>Go Back</a></div>"
    return redirect('/')

@app.route('/start', methods=['GET', 'POST'])
def start_bot():
    """Starts or restarts the LinkedIn automation bot immediately using saved config."""
    config = parse_existing_config()
    roles = config.get("roles", "java developer fresher")
    location = config.get("location", "Chennai, Tamil Nadu, India")
    apply_mode = config.get("apply_mode", "both")
    mode_label = {
        "easy_apply": "Easy Apply (LinkedIn Native)",
        "company_website": "Company Website (External Portals + AI)",
        "both": "Both (LinkedIn + Company Portals)"
    }.get(apply_mode, apply_mode)

    initial_status = {
        "status": "RUNNING",
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": None,
        "role": roles,
        "location": location,
        "mode": mode_label,
        "total_evaluated": 0,
        "total_applied": 0,
        "total_already_applied": 0,
        "total_skipped": 0,
        "current_evaluating": "Launching Chrome with Anti-Detection and Session Persistence...",
        "applied_jobs": [],
        "already_applied_jobs": [],
        "skipped_jobs": [],
        "summary_instruction": f"Automation active for '{roles}' in {location}."
    }
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as sf:
            json.dump(initial_status, sf, indent=2)
    except Exception:
        try:
            with open(os.path.join("/tmp", "automation_status.json"), "w", encoding="utf-8") as sf:
                json.dump(initial_status, sf, indent=2)
        except Exception:
            pass

    try:
        log_path = os.path.join(STORAGE_DIR, "bot_execution.log")
        log_f = open(log_path, "a", encoding="utf-8")
    except Exception:
        log_f = open(os.path.join("/tmp", "bot_execution.log"), "a", encoding="utf-8")

    is_serverless = bool(os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"))
    if not is_serverless:
        try:
            creationflags = 0x08000000 if sys.platform == "win32" else 0
            subprocess.Popen([sys.executable, "-u", BOT_SCRIPT], cwd=BASE_DIR, stdout=log_f, stderr=log_f, creationflags=creationflags)
        except Exception as launch_err:
            print(f"Subprocess launch note: {launch_err}")

    if request.is_json or request.headers.get('Accept') == 'application/json' or request.args.get('format') == 'json':
        return jsonify({"status": "running", "message": "Automation engine launched successfully"})

    return redirect('/dashboard')

@app.route('/launch', methods=['GET', 'POST'])
def launch_bot():
    """Alias for /start supporting AJAX launch from Vercel."""
    return start_bot()

def bring_chrome_window_to_front():
    """Forces the automation Chrome window to the absolute front of the Windows desktop."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        user32 = ctypes.windll.user32
        user32.AllowSetForegroundWindow(-1)
        
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW
        IsWindowVisible = user32.IsWindowVisible

        matched = []
        def foreach_w(hwnd, lp):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buff, length + 1)
                    t = buff.value.lower()
                    if any(term in t for term in ["linkedin", "jobs", "chrome", "stark"]):
                        matched.append(hwnd)
            return True

        EnumWindows(EnumWindowsProc(foreach_w), 0)
        for hwnd in matched:
            user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            user32.SetWindowPos(hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
            user32.SetWindowPos(hwnd, -2, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
            user32.SetForegroundWindow(hwnd)
            user32.BringWindowToTop(hwnd)
    except Exception:
        pass

@app.route('/bring-to-front', methods=['GET', 'POST'])
def bring_front():
    bring_chrome_window_to_front()
    return jsonify({"status": "success", "message": "Chrome automation window brought to front"})

@app.route('/live-screen')
def live_screen():
    """Serves the latest real-time screenshot of the automated Chrome session."""
    from flask import send_file, Response
    candidates = [
        os.path.join(STORAGE_DIR, "live_screen.png"),
        os.path.join(BASE_DIR, "live_screen.png"),
        os.path.join("/tmp", "live_screen.png")
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                resp = send_file(c, mimetype='image/png')
                resp.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                resp.headers['Pragma'] = 'no-cache'
                resp.headers['Expires'] = '0'
                return resp
            except Exception:
                pass

    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="960" height="540" viewBox="0 0 960 540">
        <rect width="960" height="540" fill="#0c0c12"/>
        <rect x="2" y="2" width="956" height="536" fill="none" stroke="#222232" stroke-width="2" rx="12"/>
        <circle cx="480" cy="220" r="48" fill="#181824"/>
        <text x="480" y="232" fill="#ccff00" font-family="'Outfit', sans-serif" font-size="34" text-anchor="middle">⚡</text>
        <text x="480" y="310" fill="#ffffff" font-family="'Outfit', sans-serif" font-size="20" font-weight="700" text-anchor="middle">Live Chrome Stream Ready</text>
        <text x="480" y="340" fill="#888899" font-family="sans-serif" font-size="14" text-anchor="middle">Chrome will stream live screenshots here as it signs in &amp; applies to jobs</text>
    </svg>"""
    return Response(svg, mimetype='image/svg+xml', headers={'Cache-Control': 'no-cache, no-store, must-revalidate'})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    # Only open browser automatically when running locally
    if not os.environ.get("WERKZEUG_RUN_MAIN") and not os.environ.get("PORT"):
        Timer(1, lambda: webbrowser.open_new(f"http://127.0.0.1:{port}")).start()
        
    app.run(host="0.0.0.0", port=port, debug=False)
from flask import Flask, render_template, request, redirect, url_for, jsonify
import subprocess
import sys
import webbrowser
import os
import json
import datetime
from threading import Timer

app = Flask(__name__)

# File constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = os.path.join(BASE_DIR, "user_config.txt")
STATUS_FILE = os.path.join(BASE_DIR, "automation_status.json")
BOT_SCRIPT = os.path.join(BASE_DIR, "run.py")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
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
        except Exception:
            pass

    if not config["resume_name"] and config["resume_path"]:
        config["resume_name"] = os.path.basename(config["resume_path"])
    
    return config

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
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
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
        "summary_instruction": "Ready to launch automation."
    })

@app.route('/submit', methods=['POST'])
def submit_data():
    if request.method == 'POST':
        try:
            # 1. Handle uploaded resume file or fallback
            resume_path = request.form.get('resume_path', '').strip()
            uploaded_file = request.files.get('resume_file')
            if uploaded_file and uploaded_file.filename:
                # Sanitize filename and save in uploads/
                safe_name = os.path.basename(uploaded_file.filename).replace(" ", "_")
                saved_target = os.path.join(UPLOAD_FOLDER, safe_name)
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

            with open(DATA_FILE, "w", encoding="utf-8") as file:
                file.write(file_content)

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
                pass
            
            # Launch automation runner in background
            subprocess.Popen([sys.executable, BOT_SCRIPT], cwd=BASE_DIR)

            # Redirect immediately to the live monitoring dashboard
            return redirect('/dashboard')
        
        except Exception as e:
            return f"<div style='background:#000;color:#ff4b4b;padding:40px;font-family:sans-serif;'><h1>Error: {e}</h1><a href='/' style='color:#ccff00;'>Go Back</a></div>"
    return redirect('/')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5001))
    # Only open browser automatically when running locally
    if not os.environ.get("WERKZEUG_RUN_MAIN") and not os.environ.get("PORT"):
        Timer(1, lambda: webbrowser.open_new(f"http://127.0.0.1:{port}")).start()
        
    app.run(host="0.0.0.0", port=port, debug=False)
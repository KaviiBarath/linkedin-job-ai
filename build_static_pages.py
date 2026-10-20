import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Process form.html -> index.html
form_path = os.path.join(base_dir, "templates", "form.html")
with open(form_path, "r", encoding="utf-8") as f:
    form_html = f.read()

# Replace Jinja control blocks
form_html = form_html.replace("{% if config and config.apply_mode == 'easy_apply' or not config or not config.apply_mode %}active{% endif %}", "active")
form_html = form_html.replace("{% if config and config.apply_mode == 'easy_apply' or not config or not config.apply_mode %}checked{% endif %}", "checked")
form_html = form_html.replace("{% if config and config.apply_mode == 'company_website' %}active{% endif %}", "")
form_html = form_html.replace("{% if config and config.apply_mode == 'company_website' %}checked{% endif %}", "")
form_html = form_html.replace("{% if config and config.apply_mode == 'both' %}active{% endif %}", "")
form_html = form_html.replace("{% if config and config.apply_mode == 'both' %}checked{% endif %}", "")
form_html = form_html.replace("{% if not config or config.job_mode == 'Fresher' %}active{% endif %}", "active")
form_html = form_html.replace("{% if not config or config.job_mode == 'Fresher' %}checked{% endif %}", "checked")
form_html = form_html.replace("{% if config and config.job_mode == 'Experienced' %}active{% endif %}", "")
form_html = form_html.replace("{% if config and config.job_mode == 'Experienced' %}checked{% endif %}", "")
form_html = form_html.replace("{% if not config or config.job_mode != 'Experienced' %}hidden-exp{% endif %}", "hidden-exp")
form_html = form_html.replace("{{ config.years if config else '0' }}", "0")
form_html = form_html.replace("{{ config.months if config else '0' }}", "0")
form_html = form_html.replace("{{ config.roles if config else 'java developer fresher' }}", "java developer fresher")
form_html = form_html.replace("{{ config.current_lpa if config and config.current_lpa else '0' }}", "0")
form_html = form_html.replace("{{ config.expected_lpa if config and config.expected_lpa else '4.5 LPA' }}", "4.5 LPA")
form_html = form_html.replace("{{ config.notice_period_days if config and config.notice_period_days else '0' }}", "0")
form_html = form_html.replace("{{ config.location if config else 'Chennai, Tamil Nadu, India' }}", "Chennai, Tamil Nadu, India")
form_html = form_html.replace("{{ config.user_id if config else '' }}", "")
form_html = form_html.replace("{{ config.password if config else '' }}", "")
form_html = form_html.replace("{{ config.api_key if config else '' }}", "")
form_html = form_html.replace("{{ config.resume_path if config else '' }}", "")
form_html = re.sub(r'\{%\s*if config and config\.resume_name\s*%\}.*?\{%\s*endif\s*%\}', '', form_html, flags=re.DOTALL)

# Add Netlify / External Engine Bridge script into index.html
netlify_enhancement = """
        // Netlify & Cloud Engine Bridge
        function getBackendBaseUrl() {
            if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
                return '';
            }
            const stored = localStorage.getItem('stark_engine_url');
            if (stored) return stored.replace(/\\/+$/, '');
            return 'http://localhost:5001';
        }

        function saveEngineUrl() {
            const input = document.getElementById('engine_url_input');
            if (input && input.value) {
                const clean = input.value.trim().replace(/\\/+$/, '');
                localStorage.setItem('stark_engine_url', clean);
                alert('Saved Automation Engine URL: ' + clean);
                checkEngineHealth();
            }
        }

        async function checkEngineHealth() {
            const baseUrl = getBackendBaseUrl();
            const indicator = document.getElementById('engine_status_indicator');
            if (!indicator) return;
            try {
                const res = await fetch(baseUrl + '/status', { method: 'GET', mode: 'cors' });
                if (res.ok) {
                    indicator.textContent = '● Engine Online (Ready)';
                    indicator.style.color = '#ccff00';
                } else {
                    indicator.textContent = '○ Engine Offline';
                    indicator.style.color = '#ef4444';
                }
            } catch (e) {
                indicator.textContent = '○ Engine Offline (Start py app.py)';
                indicator.style.color = '#f59e0b';
            }
        }

        window.addEventListener('DOMContentLoaded', () => {
            const isExternalHost = window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1';
            const engineBar = document.getElementById('engine_bar');
            if (isExternalHost && engineBar) {
                engineBar.style.display = 'block';
                const input = document.getElementById('engine_url_input');
                if (input) {
                    input.value = localStorage.getItem('stark_engine_url') || 'http://localhost:5001';
                }
                checkEngineHealth();
            }

            // Intercept form submit when on Netlify / external host
            const form = document.getElementById('starkForm');
            if (form && isExternalHost) {
                form.addEventListener('submit', async function(e) {
                    e.preventDefault();
                    const btn = document.getElementById('start_btn');
                    btn.innerHTML = '<span>DISPATCHING TO AUTOMATION ENGINE...</span> <span>⏳</span>';
                    btn.style.opacity = '0.85';
                    btn.style.pointerEvents = 'none';

                    const baseUrl = getBackendBaseUrl();
                    const formData = new FormData(form);
                    try {
                        const resp = await fetch(baseUrl + '/submit', {
                            method: 'POST',
                            body: formData,
                            mode: 'cors'
                        });
                        window.location.href = '/dashboard.html';
                    } catch (err) {
                        alert('Could not connect to Automation Engine at ' + baseUrl + '\\nMake sure \"py app.py\" or your cloud engine is running!');
                        btn.innerHTML = '<span>START AUTOMATION</span> <span>🚀</span>';
                        btn.style.opacity = '1';
                        btn.style.pointerEvents = 'auto';
                    }
                });
            }
        });
"""

# Insert engine bar HTML in container
engine_bar_html = """
        <!-- Netlify Cloud Engine Connector Bar -->
        <div class="engine-bar" id="engine_bar" style="display:none; background:#18181b; border:1px solid #27272a; border-radius:12px; padding:12px 14px; margin-bottom:20px; font-size:12px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#9e9ea7; font-weight:600;">🌐 Netlify Connected Portal</span>
                <span id="engine_status_indicator" style="color:#ccff00; font-weight:700;">● Checking Engine...</span>
            </div>
            <div style="margin-top:8px; display:flex; gap:8px;">
                <input type="text" id="engine_url_input" placeholder="Automation Engine URL (e.g. http://localhost:5001 or Cloud URL)" style="flex:1; background:#0d0d0f; border:1px solid #3f3f46; color:#fff; padding:6px 10px; border-radius:8px; font-size:11px;" value="http://localhost:5001">
                <button type="button" onclick="saveEngineUrl()" style="background:#ccff00; color:#000; border:none; padding:6px 12px; border-radius:8px; font-weight:700; font-size:11px; cursor:pointer;">Connect</button>
            </div>
        </div>
"""

form_html = form_html.replace('<form action="/submit"', engine_bar_html + '\n        <form action="/submit"')
form_html = form_html.replace('</script>', netlify_enhancement + '\n    </script>')

index_path = os.path.join(base_dir, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(form_html)
print("Created index.html:", len(form_html))


# 2. Process dashboard.html -> dashboard.html in root
dash_path = os.path.join(base_dir, "templates", "dashboard.html")
with open(dash_path, "r", encoding="utf-8") as f:
    dash_html = f.read()

dash_html = dash_html.replace("{{ config.roles if config else 'Java Developer Fresher' }}", "Java Developer Fresher")
dash_html = dash_html.replace("{{ config.location if config else 'Chennai, Tamil Nadu, India' }}", "Chennai, Tamil Nadu, India")
dash_html = dash_html.replace("{{ config.apply_mode if config else 'Both' }}", "Both")
dash_html = dash_html.replace("{{ config.job_mode if config else 'Fresher' }}", "Fresher")

# Update fetch('/status') in dashboard to use getBackendBaseUrl()
dash_engine_helper = """
    function getBackendBaseUrl() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return '';
        }
        const stored = localStorage.getItem('stark_engine_url');
        if (stored) return stored.replace(/\\/+$/, '');
        return 'http://localhost:5001';
    }
"""

dash_html = dash_html.replace("async function fetchAutomationStatus() {", dash_engine_helper + "\n    async function fetchAutomationStatus() {")
dash_html = dash_html.replace("const res = await fetch('/status');", "const res = await fetch(getBackendBaseUrl() + '/status', { mode: 'cors' });")

root_dash_path = os.path.join(base_dir, "dashboard.html")
with open(root_dash_path, "w", encoding="utf-8") as f:
    f.write(dash_html)
print("Created root dashboard.html:", len(dash_html))

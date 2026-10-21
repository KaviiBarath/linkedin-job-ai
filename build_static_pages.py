import re
import os

base_dir = os.path.dirname(os.path.abspath(__file__))

# 1. Process templates/form.html -> index.html
form_path = os.path.join(base_dir, "templates", "form.html")
with open(form_path, "r", encoding="utf-8") as f:
    form_html = f.read()

# Replace Jinja control blocks with clean defaults
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

index_path = os.path.join(base_dir, "index.html")
with open(index_path, "w", encoding="utf-8") as f:
    f.write(form_html)
print(f"Generated index.html ({len(form_html)} bytes)")

# 2. Process templates/dashboard.html -> dashboard.html in root
dash_path = os.path.join(base_dir, "templates", "dashboard.html")
with open(dash_path, "r", encoding="utf-8") as f:
    dash_html = f.read()

dash_html = dash_html.replace("{{ config.roles if config else 'Java Developer Fresher' }}", "Java Developer Fresher")
dash_html = dash_html.replace("{{ config.location if config else 'Chennai, Tamil Nadu, India' }}", "Chennai, Tamil Nadu, India")
dash_html = dash_html.replace("{{ config.apply_mode if config else 'Both' }}", "Both")
dash_html = dash_html.replace("{{ config.job_mode if config else 'Fresher' }}", "Fresher")

root_dash_path = os.path.join(base_dir, "dashboard.html")
with open(root_dash_path, "w", encoding="utf-8") as f:
    f.write(dash_html)
print(f"Generated root dashboard.html ({len(dash_html)} bytes)")

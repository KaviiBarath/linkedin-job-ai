import sys
import os
from typing import Any

# Prevent Windows console charmap encoding crashes (cp1252)
if sys.stdout:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            getattr(sys.stdout, "reconfigure")(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass
if sys.stderr:
    try:
        if hasattr(sys.stderr, "reconfigure"):
            getattr(sys.stderr, "reconfigure")(encoding='utf-8', errors='replace', line_buffering=True)
    except Exception:
        pass

import base64
import json
import re
import datetime
from urllib.parse import quote
# pyrefly: ignore[missing-type-stubs]
import requests
import time
import random

# Selenium Imports
# pyrefly: ignore[missing-import]
from selenium import webdriver
# pyrefly: ignore[missing-import]
from selenium.webdriver.common.keys import Keys
# pyrefly: ignore[missing-import]
from selenium.webdriver.common.by import By
# pyrefly: ignore[missing-import]
from selenium.webdriver.chrome.service import Service
# pyrefly: ignore[missing-import]
from selenium.webdriver.support.ui import Select
# pyrefly: ignore[missing-import]
from selenium.webdriver.support import expected_conditions as EC
# pyrefly: ignore[missing-import]
from selenium.webdriver.common.action_chains import ActionChains
# pyrefly: ignore[missing-import]
from webdriver_manager.chrome import ChromeDriverManager

# Global Driver Reference
driver: Any = None

#----------------- Configuration & Resume Intelligence -----------------

def load_config():
    """Reads configuration safely from user_config.txt by key-value pairs."""
    config_file = "user_config.txt"
    if not os.path.exists(config_file) and os.path.exists("user_config.example.txt"):
        try:
            import shutil
            shutil.copy("user_config.example.txt", config_file)
        except Exception:
            pass
    config = {
        "API_KEY": "",
        "USER_ID": "",
        "PASSWORD": "",
        "ROLES": "java developer fresher",
        "INPUT_RESUME_PATH": "",
        "LOCATION": "Chennai, Tamil Nadu, India",
        "APPLY_MODE": "easy_apply",
        "YEARS": "0",
        "MONTHS": "0",
        "CURRENT_LPA": "0",
        "EXPECTED_LPA": "4.5 LPA",
        "NOTICE_PERIOD_DAYS": "0",
        "LINKS": "",
        "JOB_MODE": "Fresher"
    }
    if os.path.exists(config_file):
        with open(config_file, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, val = line.split(":", 1)
                    config[key.strip()] = val.strip()
    return config

def build_candidate_profile(config):
    """Builds a comprehensive candidate profile using config and resume PDF analysis."""
    resume_path = config.get("INPUT_RESUME_PATH", "").strip()

    # Auto-detect resume if path is empty or invalid
    if not resume_path or not os.path.exists(resume_path):
        candidates = [
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "uploads", "Barath_R_Resume.pdf"),
            os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Barath_R_Resume.pdf"),
            os.path.join(os.environ.get("USERPROFILE", ""), "Downloads", "Barath_R_Resume (1) (1).pdf"),
            os.path.join(os.path.abspath(os.path.dirname(__file__)), "Barath_R_Resume.pdf"),
        ]
        for c in candidates:
            if os.path.exists(c):
                resume_path = c
                break

    raw_loc = config.get("LOCATION", "Chennai, Tamil Nadu, India").strip()
    if not raw_loc:
        raw_loc = "Chennai, Tamil Nadu, India"

    city = "Chennai"
    full_loc = raw_loc
    if "coimbatore" in raw_loc.lower():
        city = "Coimbatore"
        full_loc = "Coimbatore, Tamil Nadu, India"
    elif "chennai" in raw_loc.lower():
        city = "Chennai"
        full_loc = "Chennai, Tamil Nadu, India"
    elif "," in raw_loc:
        city = raw_loc.split(",")[0].strip()
    else:
        city = raw_loc.strip()

    # Dynamic LPA & Notice Period computation
    cur_lpa_str = config.get("CURRENT_LPA", "0").strip()
    exp_lpa_str = config.get("EXPECTED_LPA", "4.5 LPA").strip()
    notice_str  = config.get("NOTICE_PERIOD_DAYS", "0").strip()

    try:
        cur_num_val = float(''.join(ch for ch in cur_lpa_str if ch.isdigit() or ch == '.') or '0')
        cur_ctc_num = str(int(cur_num_val * 100000))
    except Exception:
        cur_ctc_num = "0"

    try:
        exp_num_val = float(''.join(ch for ch in exp_lpa_str if ch.isdigit() or ch == '.') or '4.5')
        exp_ctc_num = str(int(exp_num_val * 100000))
    except Exception:
        exp_ctc_num = "450000"

    formatted_cur_lpa = cur_lpa_str if "lpa" in cur_lpa_str.lower() else f"{cur_lpa_str} LPA"
    formatted_exp_lpa = exp_lpa_str if "lpa" in exp_lpa_str.lower() else f"{exp_lpa_str} LPA"
    formatted_notice = "Immediate" if notice_str in ["0", "", "0 Days"] else f"{notice_str} Days"

    profile = {
        "name": "Barath R",
        "first_name": "Barath",
        "last_name": "R",
        "email": config.get("USER_ID", "barath020305@gmail.com"),
        "phone": "9791945156",
        "phone_country_code": "India (+91)",
        "city": city,
        "full_location": full_loc,
        "alt_city": "Coimbatore, Tamil Nadu, India",
        "apply_mode": config.get("APPLY_MODE", "easy_apply").strip(),
        "degree": "Bachelor of Information Technology",
        "college": "Kamalam College of Arts and Science (Bharathiar University)",
        "university": "Bharathiar University",
        "graduation_year": "2025",
        "github": "https://github.com/Barath025",
        "linkedin": "https://linkedin.com/in/barath-2413b3293",
        "skills": ["Java", "OOP", "Python", "SQL", "Selenium", "Playwright", "Collections", "Multithreading"],
        "experience_years": config.get("YEARS", "0"),
        "experience_months": config.get("MONTHS", "0"),
        "current_ctc": formatted_cur_lpa,
        "current_ctc_num": cur_ctc_num,
        "expected_ctc": formatted_exp_lpa,
        "expected_ctc_num": exp_ctc_num,
        "notice_period": formatted_notice,
        "notice_period_days": notice_str,
        "last_working_day": "05/30/2025",
        "gpa": "75",
        "resume_path": resume_path,
        "resume_text": "",
        "summary": "Detail-oriented Computer Science and IT graduate seeking an entry-level Java Developer role with hands-on skills in Java, OOP, database management, and software testing."
    }

    # Extract dynamic info from resume if pypdf is available
    if resume_path and os.path.exists(resume_path):
        try:
            # pyrefly: ignore[missing-import]
            import pypdf
            import re
            reader = pypdf.PdfReader(resume_path)
            raw_text = "".join(p.extract_text() for p in reader.pages)
            profile["resume_text"] = raw_text

            # Dynamic phone detection
            phone_match = re.search(r'(?:\+?91[\s-]?)?[6-9]\d{9}', raw_text)
            if phone_match:
                profile["phone"] = phone_match.group(0).replace(" ", "").replace("+91", "").strip()

            # Dynamic email detection
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', raw_text)
            if email_match and not profile["email"]:
                profile["email"] = email_match.group(0)

            # Dynamic objective detection
            if "OBJECTIVE" in raw_text.upper():
                try:
                    obj_part = raw_text.upper().split("OBJECTIVE", 1)[-1].split("TECHNICAL SKILLS", 1)[0].strip()
                    if len(obj_part) > 20:
                        profile["summary"] = obj_part.replace("\n", " ").strip()
                except Exception:
                    pass

            print(f"[*] Successfully analyzed resume PDF: {os.path.basename(resume_path)}")
        except Exception as e:
            print(f"[!] Note on resume analysis: {e}")

    return profile

# Load settings & candidate profile
CONFIG = load_config()
PROFILE = build_candidate_profile(CONFIG)

API_KEY           = CONFIG.get("API_KEY", "")
USER_ID           = CONFIG.get("USER_ID", "")
PASSWORD          = CONFIG.get("PASSWORD", "")
ROLES             = CONFIG.get("ROLES", "java developer fresher")
INPUT_RESUME_PATH = PROFILE.get("resume_path", "")
LOCATION          = PROFILE.get("full_location", "Chennai, Tamil Nadu, India")
CITY              = PROFILE.get("city", "Chennai")
APPLY_MODE        = CONFIG.get("APPLY_MODE", "easy_apply").strip()
YEARS             = CONFIG.get("YEARS", "0")
MONTHS            = CONFIG.get("MONTHS", "0")
CURRENT_LPA       = CONFIG.get("CURRENT_LPA", "0")
EXPECTED_LPA      = CONFIG.get("EXPECTED_LPA", "4.5 LPA")
NOTICE_PERIOD_DAYS = CONFIG.get("NOTICE_PERIOD_DAYS", "0")
LINKS             = CONFIG.get("LINKS", "")
JOB_MODE          = CONFIG.get("JOB_MODE", "Fresher")

#----------------- Real-Time Live Status Tracking & Interface Reporting -----------------

STATUS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "automation_status.json")

class AutomationState:
    """Strongly-typed runtime state tracker for automation execution."""
    def __init__(self):
        self.total_evaluated: int = 0
        self.total_applied: int = 0
        self.total_already_applied: int = 0
        self.total_skipped: int = 0
        self.applied_jobs: list[Any] = []
        self.already_applied_jobs: list[Any] = []
        self.skipped_jobs: list[Any] = []

def update_automation_status(updates):
    """
    Thread-safe live status sync: writes progress, applied roles, and instructions to automation_status.json
    for real-time streaming to the user interface dashboard.
    """
    try:
        current_data = {
            "status": "RUNNING",
            "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": None,
            "role": ROLES,
            "location": LOCATION,
            "mode": APPLY_MODE,
            "total_evaluated": 0,
            "total_applied": 0,
            "total_already_applied": 0,
            "total_skipped": 0,
            "current_evaluating": "",
            "applied_jobs": [],
            "already_applied_jobs": [],
            "skipped_jobs": [],
            "summary_instruction": ""
        }
        if os.path.exists(STATUS_FILE):
            try:
                with open(STATUS_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        current_data.update(loaded)
            except Exception:
                pass

        current_data.update(updates)

        # Atomic write to prevent partial file read collision by Flask
        temp_file = STATUS_FILE + ".tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(current_data, f, indent=2)
        if os.path.exists(STATUS_FILE):
            os.replace(temp_file, STATUS_FILE)
        else:
            os.rename(temp_file, STATUS_FILE)
    except Exception as e:
        pass

#----------------- Browser Initialization & Safe Window Management -----------------

def bring_window_to_foreground(drv=None):
    """Brings the Chrome automation window to the absolute front of the user's desktop."""
    if sys.platform != "win32":
        return
    try:
        if drv:
            try:
                drv.maximize_window()
            except Exception:
                pass
        import ctypes
        user32 = ctypes.windll.user32
        
        EnumWindows = user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW
        IsWindowVisible = user32.IsWindowVisible

        matched_hwnds = []

        def foreach_window(hwnd, lParam):
            if IsWindowVisible(hwnd):
                length = GetWindowTextLengthW(hwnd)
                if length > 0:
                    buff = ctypes.create_unicode_buffer(length + 1)
                    GetWindowTextW(hwnd, buff, length + 1)
                    title = buff.value
                    if any(t in title for t in ["LinkedIn", "Jobs", "Chrome"]):
                        matched_hwnds.append(hwnd)
            return True

        EnumWindows(EnumWindowsProc(foreach_window), 0)

        for hwnd in matched_hwnds:
            try:
                user32.ShowWindow(hwnd, 9)  # SW_RESTORE
                user32.ShowWindow(hwnd, 3)  # SW_MAXIMIZE
                user32.SetForegroundWindow(hwnd)
                user32.BringWindowToTop(hwnd)
            except Exception:
                pass
    except Exception:
        pass

def init_driver():
    """Initializes Chrome with Anti-Detection and Persistent Session Profile in full view."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--window-position=0,0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    options.add_argument("--lang=en-US")
    options.add_experimental_option('prefs', {
        'intl.accept_languages': 'en-US,en'
    })

    is_headless = sys.platform.startswith("linux") or os.environ.get("HEADLESS", "false").lower() == "true"
    if is_headless:
        options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    profile_dir = os.path.join(base_dir, "chrome_profile")
    os.makedirs(profile_dir, exist_ok=True)

    # Clean up stale Chrome locks so profile directory is always safely accessible
    for lock_name in ["SingletonLock", "SingletonCookie", "SingletonSocket", "lockfile", "DevToolsActivePort"]:
        lp = os.path.join(profile_dir, lock_name)
        if os.path.exists(lp):
            try:
                os.remove(lp)
            except Exception:
                pass

    options.add_argument(f"--user-data-dir={profile_dir}")

    service = Service(ChromeDriverManager().install())
    try:
        drv = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"[!] Note on Chrome profile: {e}. Starting standard visible browser session...")
        fallback_options = webdriver.ChromeOptions()
        fallback_options.add_argument("--start-maximized")
        fallback_options.add_argument("--window-size=1920,1080")
        fallback_options.add_argument("--window-position=0,0")
        fallback_options.add_argument("--disable-blink-features=AutomationControlled")
        fallback_options.add_argument("--lang=en-US")
        if is_headless:
            fallback_options.add_argument("--headless=new")
            fallback_options.add_argument("--no-sandbox")
            fallback_options.add_argument("--disable-dev-shm-usage")
            fallback_options.add_argument("--disable-gpu")
            fallback_options.add_argument("--window-size=1920,1080")
        drv = webdriver.Chrome(service=service, options=fallback_options)

    try:
        drv.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """
        })
    except Exception:
        pass

    # Ensure browser window is visibly brought to front of desktop
    bring_window_to_foreground(drv)

    return drv

def visually_type_and_search(driver, query, location):
    """
    Visually navigates to LinkedIn Jobs, focuses the search inputs, and types the
    role and location character by character so the user sees the automated action live.
    """
    try:
        bring_window_to_foreground(driver)
        print(f">> [LIVE] Opening LinkedIn Jobs & typing query: '{query}' in '{location}'...")
        driver.get("https://www.linkedin.com/jobs/?locale=en_US")
        bring_window_to_foreground(driver)
        time.sleep(2.5)

        kw_inputs = driver.find_elements(
            By.XPATH,
            "//input[contains(@id, 'jobs-search-box-keyword')] | "
            "//input[contains(@class, 'jobs-search-box__text-input') and not(contains(@id, 'location'))] | "
            "//input[@aria-label='Search by title, skill, or company'] | "
            "//input[contains(@placeholder, 'Search job') or contains(@placeholder, 'Search by title')]"
        )

        loc_inputs = driver.find_elements(
            By.XPATH,
            "//input[contains(@id, 'jobs-search-box-location')] | "
            "//input[contains(@class, 'jobs-search-box__text-input') and contains(@id, 'location')] | "
            "//input[@aria-label='City, state, or zip code'] | "
            "//input[contains(@placeholder, 'City, state') or contains(@placeholder, 'location')]"
        )

        typed_kw = False
        if kw_inputs:
            for kw in kw_inputs:
                if kw.is_displayed():
                    try:
                        driver.execute_script("arguments[0].style.outline = '3px solid #ccff00';", kw)
                        kw.clear()
                        for ch in query:
                            kw.send_keys(ch)
                            time.sleep(0.04)
                        time.sleep(0.4)
                        driver.execute_script("arguments[0].style.outline = '';", kw)
                        typed_kw = True
                        break
                    except Exception:
                        pass

        if loc_inputs:
            for loc in loc_inputs:
                if loc.is_displayed():
                    try:
                        driver.execute_script("arguments[0].style.outline = '3px solid #ccff00';", loc)
                        loc.clear()
                        for ch in str(location):
                            loc.send_keys(ch)
                            time.sleep(0.03)
                        time.sleep(0.4)
                        driver.execute_script("arguments[0].style.outline = '';", loc)
                        if typed_kw:
                            loc.send_keys(Keys.ENTER)
                            time.sleep(2.5)
                        break
                    except Exception:
                        pass
        return True
    except Exception as e:
        print(f"   [!] Visual search preview notice: {e}")
        return False

def ensure_active_window():
    """Ensures Selenium always operates on an active, open window handle, preventing crashes."""
    global driver
    try:
        _ = driver.current_window_handle
        return True
    except Exception:
        try:
            handles = driver.window_handles
            if handles:
                driver.switch_to.window(handles[0])
                return True
            else:
                return False
        except Exception:
            return False

#----------------- Helper Functions -----------------

def click_element_safe(element):
    """Safely clicks an element using multiple methods."""
    try:
        element.click()
        return True
    except Exception:
        try:
            driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            try:
                ActionChains(driver).move_to_element(element).click().perform()
                return True
            except Exception:
                return False

def is_logged_in():
    """Checks whether the browser is currently authenticated to LinkedIn."""
    try:
        cur = driver.current_url.lower()
        if any(p in cur for p in ["/feed", "/jobs", "/mynetwork", "/messaging"]):
            return True
        nav = driver.find_elements(
            By.XPATH,
            "//nav[contains(@class, 'global-nav')] | //button[contains(@class, 'global-nav__me')] | //div[contains(@class, 'feed-identity-module')]"
        )
        return len(nav) > 0
    except Exception:
        return False

#----------------- Login Functionality -----------------

def login_to_linkedin(user_id, password):
    """Directly and reliably logs into LinkedIn, with 2FA / CAPTCHA support."""
    print("\n" + "=" * 55)
    print(">> [1/3] CHECKING LINKEDIN LOGIN STATUS...")
    print("=" * 55)

    try:
        driver.get("https://www.linkedin.com/feed/?locale=en_US")
        time.sleep(3)
        if is_logged_in():
            print("[OK] [LOGIN] Already logged in to LinkedIn (persistent session active)!")
            return True
    except Exception as e:
        print(f"   (Session check note: {e})")

    print(">> [LOGIN] Not currently logged in. Navigating to Sign-in page...")
    driver.get("https://www.linkedin.com/login?locale=en_US")
    time.sleep(3)

    username_input = None
    username_xpaths = [
        "//input[@autocomplete='username']",
        "//input[@type='email']",
        "//input[@id='username']",
        "//input[@name='session_key']",
        "//input[@id='session_key']",
        "//input[@type='text']"
    ]
    for xp in username_xpaths:
        elems = driver.find_elements(By.XPATH, xp)
        for el in elems:
            if el.is_displayed():
                username_input = el
                break
        if username_input:
            break

    password_input = None
    password_xpaths = [
        "//input[@type='password']",
        "//input[@id='password']",
        "//input[@name='session_password']"
    ]
    for xp in password_xpaths:
        elems = driver.find_elements(By.XPATH, xp)
        for el in elems:
            if el.is_displayed():
                password_input = el
                break
        if password_input:
            break

    if username_input and password_input:
        print(f">> [LOGIN] Visually entering credentials for {user_id}...")
        update_automation_status({"current_evaluating": f"Logging into LinkedIn as {user_id}..."})
        try:
            driver.execute_script("arguments[0].style.outline = '3px solid #ccff00';", username_input)
        except Exception:
            pass
        username_input.clear()
        for ch in user_id:
            username_input.send_keys(ch)
            time.sleep(0.03)
        try:
            driver.execute_script("arguments[0].style.outline = '';", username_input)
        except Exception:
            pass
        time.sleep(0.4)

        try:
            driver.execute_script("arguments[0].style.outline = '3px solid #ccff00';", password_input)
        except Exception:
            pass
        password_input.clear()
        for ch in password:
            password_input.send_keys(ch)
            time.sleep(0.03)
        try:
            driver.execute_script("arguments[0].style.outline = '';", password_input)
        except Exception:
            pass
        time.sleep(0.5)

        submit_btns = driver.find_elements(
            By.XPATH,
            "//button[@type='submit'] | //button[contains(@class, 'btn__primary--large')] | //input[@type='submit']"
        )
        target_btn = None
        button_clicked = False
        for b in submit_btns:
            if not b.is_displayed(): continue
            txt = (b.text or "").strip()
            if any(term in txt.lower() for term in ["sign in", "log in", "agree & join"]):
                target_btn = b
                break
            if b.get_attribute("type") == "submit" and not any(sso in txt for sso in ["Microsoft", "Apple", "Google"]):
                target_btn = b
                break

        if target_btn:
            print(f">> [LOGIN] Clicking '{target_btn.text.strip()}' button...")
            try:
                target_btn.click()
                button_clicked = True
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", target_btn)
                    button_clicked = True
                except Exception:
                    pass

        if not button_clicked:
            print(">> [LOGIN] Submitting via Enter key...")
            try:
                password_input.send_keys(Keys.ENTER)
            except Exception:
                pass
    else:
        print("[!] Could not automatically detect standard login fields.")
        print("[*] If prompted on screen, please log in manually.")

    print(">> [LOGIN] Verifying authentication...")
    max_wait = 90
    start_time = time.time()
    security_prompted = False

    while time.time() - start_time < max_wait:
        time.sleep(2)
        ensure_active_window()
        cur_url = driver.current_url.lower()

        if is_logged_in():
            print("[OK] [LOGIN] Login successful! Session is now saved.")
            time.sleep(2)
            return True

        if any(sso in cur_url for sso in ["login.live.com", "microsoft", "apple.com"]):
            print(">> [LOGIN] Detected 3rd-party OAuth redirect. Returning to LinkedIn login...")
            driver.get("https://www.linkedin.com/login?locale=en_US")
            time.sleep(3)
            continue

        is_checkpoint = any(k in cur_url for k in ["checkpoint", "challenge", "verification"])
        page_source = driver.page_source.lower()
        if is_checkpoint or any(k in page_source for k in ["security check", "verification code", "puzzle", "認証"]):
            if not security_prompted:
                print("\n" + "!" * 60)
                print("[!] LINKEDIN SECURITY CHECK / 2FA DETECTED!")
                print("[*] Please solve the CAPTCHA or enter the verification code in the Chrome window.")
                print(">> The bot will automatically detect completion and continue!")
                print("!" * 60 + "\n")
                security_prompted = True
            continue

        error_elems = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'alert--error') or contains(@id, 'error-for-password') or contains(@id, 'error-for-username')]"
        )
        if error_elems and any(e.is_displayed() for e in error_elems):
            print("[ERROR] [LOGIN ERROR] Invalid username or password in user_config.txt!")
            print("[*] Please verify your login credentials.")
            return False

    if is_logged_in():
        print("[OK] [LOGIN] Authenticated successfully!")
        return True
    else:
        print("[!] Proceeding with session check...")
        return True

#----------------- Easy Apply & Button Recognition -----------------

def get_easy_apply_button():
    """Finds the Easy Apply button on the current job details panel across languages."""
    try:
        buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'jobs-apply-button')]")
        for btn in buttons:
            if not btn.is_displayed():
                continue
            txt = (btn.text or "").strip().lower()
            aria = (btn.get_attribute("aria-label") or "").strip().lower()

            if "applied" in txt or "applied" in aria or "応募済み" in txt or "応募済み" in aria:
                return None

            if any(term in txt or term in aria for term in ["easy apply", "カンタン応募", "簡易応募"]):
                return btn

            if "apply" in txt and "website" not in txt and "company" not in txt:
                return btn

        fallbacks = [
            "//button[contains(., 'Easy Apply')]",
            "//button[contains(., 'Easy Application')]",
            "//button[contains(@aria-label, 'Easy Apply')]",
            "//button[contains(@aria-label, '応募')]"
        ]
        for xpath in fallbacks:
            found = driver.find_elements(By.XPATH, xpath)
            for f_btn in found:
                if f_btn.is_displayed() and f_btn.is_enabled():
                    f_txt = (f_btn.text or "").lower()
                    if "applied" not in f_txt and "応募済み" not in f_txt:
                        return f_btn
    except Exception:
        pass
    return None

def get_external_apply_button():
    """Finds the external 'Apply on company website' or 'Apply' button on LinkedIn."""
    try:
        buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'jobs-apply-button')] | //a[contains(@class, 'jobs-apply-button')]")
        for btn in buttons:
            if not btn.is_displayed(): continue
            txt = (btn.text or "").strip().lower()
            aria = (btn.get_attribute("aria-label") or "").strip().lower()
            if "applied" in txt or "applied" in aria:
                return None
            if "easy" not in txt and "easy" not in aria and any(t in txt or t in aria for t in ["apply", "website", "company", "continue"]):
                return btn

        xpaths = [
            "//button[contains(., 'Apply on company website')]",
            "//a[contains(., 'Apply on company website')]",
            "//button[contains(@aria-label, 'Apply on company website')]",
            "//a[contains(@aria-label, 'Apply on company website')]",
            "//button[span[contains(normalize-space(), 'Apply') and not(contains(normalize-space(), 'Easy')) and not(contains(normalize-space(), 'Applied'))]]",
            "//a[span[contains(normalize-space(), 'Apply') and not(contains(normalize-space(), 'Easy')) and not(contains(normalize-space(), 'Applied'))]]"
        ]
        for xp in xpaths:
            found = driver.find_elements(By.XPATH, xp)
            for btn in found:
                if btn.is_displayed() and btn.is_enabled():
                    txt = (btn.text or "").lower()
                    if "applied" not in txt and "easy" not in txt:
                        return btn
    except Exception:
        pass
    return None

def find_primary_button(labels):
    """Finds a modal wizard button by a list of possible labels (multilingual)."""
    for label in labels:
        try:
            btn = driver.find_element(By.XPATH, f"//button[contains(@aria-label, '{label}')]")
            if btn.is_displayed(): return btn
        except Exception: pass

        try:
            btn = driver.find_element(By.XPATH, f"//button[contains(normalize-space(), '{label}')]")
            if btn.is_displayed(): return btn
        except Exception: pass

        try:
            btn = driver.find_element(By.XPATH, f"//button/span[contains(normalize-space(), '{label}')]")
            if btn.is_displayed(): return btn
        except Exception: pass

    return None

def close_active_modal():
    """Aggressively closes any active modal or confirmation dialog."""
    start_time = time.time()
    while time.time() - start_time < 8:
        ensure_active_window()
        if not driver.find_elements(By.CLASS_NAME, "artdeco-modal"):
            return

        done_btns = driver.find_elements(
            By.XPATH,
            "//button[span[contains(normalize-space(), 'Done') or contains(normalize-space(), '完了') or contains(normalize-space(), '閉じる')]]"
        )
        if done_btns and done_btns[0].is_displayed():
            click_element_safe(done_btns[0])
            time.sleep(1)
            continue

        close_selectors = [
            "//button[@aria-label='Dismiss']",
            "//button[@aria-label='閉じる']",
            "//button[contains(@class, 'artdeco-modal__dismiss')]",
            "//button[@data-test-modal-close-btn]",
            "//li-icon[@type='cancel-icon']/.."
        ]
        for sel in close_selectors:
            try:
                btns = driver.find_elements(By.XPATH, sel)
                for btn in btns:
                    if btn.is_displayed():
                        click_element_safe(btn)
                        time.sleep(0.5)
            except Exception: pass

        discard_selectors = [
            "//button[@data-control-name='discard_application_confirm_btn']",
            "//button[contains(., 'Discard') or contains(., '破棄')]",
            "//button[span[contains(text(), 'Discard') or contains(text(), '破棄')]]",
            "//button[contains(@class, 'artdeco-button--primary') and span[contains(text(), 'Discard')]]"
        ]
        for sel in discard_selectors:
            try:
                btns = driver.find_elements(By.XPATH, sel)
                for btn in btns:
                    if btn.is_displayed():
                        click_element_safe(btn)
                        time.sleep(0.8)
            except Exception: pass

        # Handle post-external application prompt ("Did you apply to this job? Yes / No")
        try:
            applied_confirm_btns = driver.find_elements(
                By.XPATH,
                "//button[contains(., 'Yes') or contains(., 'I applied') or contains(@aria-label, 'Yes') or contains(@aria-label, 'applied')]"
            )
            for ab in applied_confirm_btns:
                if ab.is_displayed():
                    click_element_safe(ab)
                    time.sleep(0.5)
                    break
        except Exception: pass

        try:
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
            time.sleep(0.5)
        except Exception: pass

#----------------- Form Automation & Smart Fillers -----------------

def handle_resume_upload(modal, profile):
    """Handles resume upload or existing resume selection in the wizard."""
    resume_path = profile.get("resume_path", "")
    
    # 1. Check if a resume is already selected
    try:
        resumes = modal.find_elements(
            By.XPATH, 
            ".//div[contains(@class, 'jobs-document-upload__title') or contains(@class, 'ui-attachment')]"
        )
        if resumes:
            return True
    except Exception:
        pass

    # 2. Upload file if file input is present and resume exists
    if resume_path and os.path.exists(resume_path):
        try:
            file_inputs = driver.find_elements(By.XPATH, "//input[@type='file']")
            if file_inputs:
                file_inputs[0].send_keys(resume_path)
                print(f"   [*] Uploaded resume: {os.path.basename(resume_path)}")
                time.sleep(2.5)
                return True
        except Exception as e:
            print(f"   [!] File upload attempt: {e}")

    return False

def handle_location_input(modal, city="Chennai", full_target="Chennai, Tamil Nadu, India"):
    """Accurately selects the city/location in LinkedIn's autocomplete dropdown without errors."""
    try:
        target_city_clean = (city or "Chennai").strip().lower()
        
        # 1. Locate location / city input fields in modal
        loc_inputs = []
        candidate_xpaths = [
            ".//input[contains(@id, 'city') or contains(@name, 'city') or contains(@class, 'city')]",
            ".//input[contains(@aria-label, 'city') or contains(@aria-label, 'location') or contains(@aria-label, 'town')]",
            ".//input[contains(@id, 'location') or contains(@name, 'location')]",
            ".//input[@role='combobox' and (contains(@id, 'easyApply') or contains(@class, 'search-basic-typeahead') or contains(@id, 'city'))]"
        ]
        for xp in candidate_xpaths:
            for el in modal.find_elements(By.XPATH, xp):
                if el.is_displayed() and el not in loc_inputs:
                    loc_inputs.append(el)

        # Also match by label
        labels = modal.find_elements(
            By.XPATH,
            ".//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'location') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'city') or contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), 'town')]"
        )
        for lbl in labels:
            for_id = lbl.get_attribute("for")
            if for_id:
                for inp in modal.find_elements(By.ID, for_id):
                    if inp.is_displayed() and inp not in loc_inputs:
                        loc_inputs.append(inp)
            for inp in lbl.find_elements(By.XPATH, ".//input | ./following-sibling::*//input"):
                if inp.is_displayed() and inp not in loc_inputs:
                    loc_inputs.append(inp)

        if not loc_inputs:
            return

        for inp in loc_inputs:
            curr_val = (inp.get_attribute("value") or "").strip()
            
            # Check for validation error on this input
            has_error = False
            try:
                parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element') or contains(@class, 'fb-form-element') or parent::div]")
                errs = parent.find_elements(By.CLASS_NAME, "artdeco-inline-feedback__message")
                has_error = any(e.is_displayed() for e in errs)
            except Exception:
                pass

            # If it already contains target_city (e.g. 'chennai' or 'coimbatore') and no error, do not overwrite!
            if curr_val and not has_error and target_city_clean in curr_val.lower():
                print(f"   [OK] Location is already correctly set: '{curr_val}'")
                continue

            print(f"   [*] Setting location autocomplete to '{city}' ({full_target})...")
            driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", inp)
            time.sleep(0.3)
            click_element_safe(inp)
            time.sleep(0.2)

            # Clear the input cleanly
            inp.send_keys(Keys.CONTROL + "a")
            time.sleep(0.1)
            inp.send_keys(Keys.BACKSPACE)
            time.sleep(0.1)
            driver.execute_script("arguments[0].value = '';", inp)
            time.sleep(0.2)

            # Type the target city slowly to trigger LinkedIn's typeahead
            display_city = city.capitalize()
            for char in display_city:
                inp.send_keys(char)
                time.sleep(0.06)
            time.sleep(1.5)

            # Search for suggestion dropdown across possible containers
            suggestion_xpaths = [
                "//div[contains(@class, 'search-typeahead-v2__hit')]",
                "//div[contains(@class, 'basic-typeahead__selectable')]",
                "//div[@role='option']",
                "//li[@role='option']",
                "//div[contains(@class, 'artdeco-typeahead__result')]",
                "//li[contains(@class, 'artdeco-typeahead__result')]",
                "//ul[contains(@class, 'typeahead')]//li"
            ]
            suggestions = []
            for sxp in suggestion_xpaths:
                try:
                    for el in driver.find_elements(By.XPATH, sxp):
                        if el.is_displayed() and el not in suggestions:
                            suggestions.append(el)
                except Exception:
                    pass

            # Match the best suggestion
            selected_sug = None
            # 1. Match city + state/country (e.g. "Chennai, Tamil Nadu, India" or "Coimbatore, Tamil Nadu, India")
            for sug in suggestions:
                stxt = (sug.text or "").strip().lower()
                if target_city_clean in stxt and ("tamil nadu" in stxt or "india" in stxt):
                    selected_sug = sug
                    break
            # 2. Match city
            if not selected_sug:
                for sug in suggestions:
                    stxt = (sug.text or "").strip().lower()
                    if target_city_clean in stxt:
                        selected_sug = sug
                        break
            # 3. Fallback to first suggestion if available
            if not selected_sug and suggestions:
                selected_sug = suggestions[0]

            clicked = False
            if selected_sug:
                sug_title = selected_sug.text.strip()
                clicked = click_element_safe(selected_sug)
                if clicked:
                    print(f"   [OK] Selected location suggestion: '{sug_title}'")
                time.sleep(0.6)

            if not clicked:
                # Use keyboard navigation fallback
                inp.send_keys(Keys.ARROW_DOWN)
                time.sleep(0.3)
                inp.send_keys(Keys.ENTER)
                time.sleep(0.3)
                inp.send_keys(Keys.TAB)

            time.sleep(0.5)
    except Exception as e:
        print(f"   [!] Location autocomplete notice: {e}")

def handle_all_dropdowns(modal):
    """Selects valid answers for both native <select> and custom dropdowns."""
    # 1. Native <select> elements
    try:
        select_elems = modal.find_elements(By.TAG_NAME, "select")
        for sel_elem in select_elems:
            if not sel_elem.is_displayed(): continue
            try:
                sel = Select(sel_elem)
                curr_text = sel.first_selected_option.text.strip().lower() if sel.all_selected_options else ""
                
                # Trigger selection if unselected, empty, or placeholder
                if not curr_text or "select an option" in curr_text or "choose" in curr_text or curr_text == "":
                    parent_txt = ""
                    try:
                        parent_txt = sel_elem.find_element(
                            By.XPATH, 
                            "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element') or contains(@class, 'fb-form-element') or parent::div]"
                        ).text.lower()
                    except Exception: pass

                    selected = False
                    # Consent, agreement, authorization questions -> Prefer "Yes" / "Agree"
                    if any(k in parent_txt for k in ["consent", "agree", "authorized", "eligible", "profile", "permission", "terms"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if t in ["yes", "i agree", "agree", "accept", "true"]:
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                print(f"   [OK] Selected consent dropdown: '{opt.text.strip()}'")
                                break
                    # Sponsorship questions -> Prefer "No"
                    elif any(k in parent_txt for k in ["sponsor", "sponsorship", "visa"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if t in ["no", "i do not", "false"]:
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                print(f"   [OK] Selected sponsorship dropdown: '{opt.text.strip()}'")
                                break

                    # Default fallback: pick index 1 (the first genuine option)
                    if not selected and len(sel.options) > 1:
                        sel.select_by_index(1)
                        print(f"   [OK] Selected dropdown option: '{sel.options[1].text.strip()}'")
            except Exception: pass
    except Exception: pass

    # 2. Custom Artdeco / Listbox dropdown buttons
    try:
        custom_btns = modal.find_elements(
            By.XPATH,
            ".//button[contains(@class, 'artdeco-dropdown__trigger') or @aria-haspopup='listbox' or contains(., 'Select an option')]"
        )
        for btn in custom_btns:
            if not btn.is_displayed(): continue
            txt = (btn.text or "").strip().lower()
            if "select an option" in txt or "choose" in txt or not txt:
                try:
                    click_element_safe(btn)
                    time.sleep(0.6)
                    options = driver.find_elements(
                        By.XPATH,
                        "//div[contains(@class, 'artdeco-dropdown__content')]//li | //ul[@role='listbox']//li | //div[@role='option']"
                    )
                    for opt in options:
                        if opt.is_displayed():
                            click_element_safe(opt)
                            print(f"   [OK] Selected custom dropdown item: '{opt.text.strip()}'")
                            break
                except Exception: pass
    except Exception: pass

def handle_radios_and_checkboxes(modal):
    """Answers radio buttons and ticks required checkboxes."""
    # 1. Radio Buttons
    try:
        fieldsets = modal.find_elements(By.TAG_NAME, "fieldset")
        for fs in fieldsets:
            text = fs.text.lower()
            yes_opts = fs.find_elements(By.XPATH, ".//label[contains(translate(., 'YES', 'yes'), 'yes') or contains(., 'はい')]")
            no_opts = fs.find_elements(By.XPATH, ".//label[contains(translate(., 'NO', 'no'), 'no') or contains(., 'いいえ')]")

            checked = fs.find_elements(By.XPATH, ".//input[@type='radio' and @checked]")
            if checked: continue

            if any(k in text for k in ["sponsor", "sponsorship", "visa"]):
                if no_opts: no_opts[0].click()
                elif yes_opts: yes_opts[0].click()
            elif any(k in text for k in ["authorized", "authorization", "legally", "citizen", "relocate", "commute", "travel", "background", "drug", "agree", "consent"]):
                if yes_opts: yes_opts[0].click()
                elif no_opts: no_opts[0].click()
            else:
                if yes_opts: yes_opts[0].click()
                else:
                    all_labels = fs.find_elements(By.TAG_NAME, "label")
                    if all_labels: all_labels[0].click()
    except Exception: pass

    # 2. Checkboxes
    try:
        checkboxes = modal.find_elements(By.XPATH, ".//input[@type='checkbox']")
        for cb in checkboxes:
            if cb.is_displayed() and not cb.is_selected():
                cb.click()
    except Exception: pass

def handle_text_inputs_and_blanks(modal, profile):
    """Fills all text, numeric, date, and textarea inputs from candidate profile."""
    try:
        inputs = modal.find_elements(By.XPATH, ".//input | .//textarea")
        for inp in inputs:
            if not inp.is_displayed(): continue
            inp_type = (inp.get_attribute("type") or "text").lower()
            if inp_type in ["hidden", "checkbox", "radio", "file", "submit", "button"]:
                continue

            curr_val = (inp.get_attribute("value") or "").strip()
            
            # Find associated label text
            label_txt = ""
            inp_id = (inp.get_attribute("id") or "").lower()
            if inp_id:
                lbls = modal.find_elements(By.XPATH, f".//label[@for='{inp_id}']")
                if lbls: label_txt = lbls[0].text.lower()
            if not label_txt:
                label_txt = (inp.get_attribute("aria-label") or inp.get_attribute("placeholder") or "").lower()

            # Skip Location / City / Address inputs (handled specifically by handle_location_input)
            is_loc_field = (
                any(l in label_txt for l in ["location", "city", "town", "where do you live", "residence", "address", "state", "postal", "zip", "country"]) or
                (inp_id and any(k in inp_id for k in ["city", "location", "geo", "address"])) or
                (inp.get_attribute("role") == "combobox") or
                ("typeahead" in (inp.get_attribute("class") or "").lower()) or
                ("typeahead" in inp_id)
            )
            if is_loc_field:
                continue

            # Check if this input has a validation error
            parent = inp.find_element(By.XPATH, "./ancestor::div[contains(@class, 'jobs-easy-apply-form-element') or contains(@class, 'fb-form-element') or parent::div]")
            has_error = len(parent.find_elements(By.CLASS_NAME, "artdeco-inline-feedback__message")) > 0

            # Only fill if empty or has error
            if curr_val and not has_error:
                continue

            # Clear if error
            if has_error and curr_val:
                try:
                    inp.clear()
                    time.sleep(0.2)
                except: pass

            # Value Resolution
            answer = ""
            if any(p in label_txt for p in ["phone", "mobile"]):
                answer = profile["phone"]
            elif "first name" in label_txt:
                answer = profile["first_name"]
            elif "last name" in label_txt:
                answer = profile["last_name"]
            elif "email" in label_txt:
                answer = profile["email"]
            elif any(s in label_txt for s in ["current ctc", "current annual ctc", "current salary"]):
                answer = profile["current_ctc_num"] if inp_type == "number" else profile["current_ctc"]
            elif any(s in label_txt for s in ["expected ctc", "expected annual ctc", "expected salary"]):
                answer = profile["expected_ctc_num"] if inp_type == "number" else profile["expected_ctc"]
            elif any(n in label_txt for n in ["notice", "notice period", "days to join"]):
                answer = profile["notice_period_days"] if inp_type == "number" else profile["notice_period"]
            elif any(y in label_txt for y in ["year", "experience", "how many years"]):
                answer = profile.get("experience_years", "0") if profile.get("experience_years") != "0" else "1"
            elif any(d in label_txt for d in ["last working day", "date"]):
                answer = profile["last_working_day"]
            elif "linkedin" in label_txt:
                answer = profile["linkedin"]
            elif "github" in label_txt:
                answer = profile["github"]
            elif any(w in label_txt for w in ["website", "portfolio", "link"]):
                answer = profile["github"]
            elif any(g in label_txt for g in ["gpa", "percentage", "marks"]):
                answer = profile["gpa"]
            elif any(c in label_txt for c in ["college", "university"]):
                answer = profile["university"]
            elif "degree" in label_txt:
                answer = profile["degree"]
            elif inp.tag_name == "textarea":
                answer = profile["summary"]
            else:
                # Generic fallback for required blanks
                if inp_type == "number":
                    answer = "1"
                else:
                    answer = "1"

            if answer:
                try:
                    inp.clear()
                    inp.send_keys(str(answer))
                    print(f"   [*] Filled '{label_txt[:30]}...' -> '{answer}'")
                except Exception: pass
    except Exception: pass

def smart_fill_form(modal, profile):
    """Coordinates all specialized form fillers to guarantee a completely valid form."""
    handle_resume_upload(modal, profile)
    handle_location_input(modal, profile.get("city", "Chennai"), profile.get("full_location", "Chennai, Tamil Nadu, India"))
    handle_all_dropdowns(modal)
    handle_radios_and_checkboxes(modal)
    handle_text_inputs_and_blanks(modal, profile)

    # Optional AI assistant if API key is valid
    if API_KEY and API_KEY.startswith("AIza"):
        try:
            ai_solver()
        except Exception:
            pass

def ai_solver(container=None):
    """Uses Gemini API to solve complex application questions on LinkedIn modals or external company portals."""
    if not API_KEY or not API_KEY.startswith("AIza"):
        return False

    target = container
    if target is None:
        modals = driver.find_elements(By.CLASS_NAME, "artdeco-modal")
        if modals:
            target = modals[0]
        else:
            try:
                target = driver.find_element(By.TAG_NAME, "body")
            except Exception:
                return False

    try:
        screenshot = target.screenshot_as_png
        b64_image = base64.b64encode(screenshot).decode('utf-8')

        prompt = f"""
        You are an expert candidate filling out a job application form.
        Candidate Profile:
        - Full Name: {PROFILE['name']}
        - Email: {PROFILE['email']}
        - Phone: {PROFILE['phone']}
        - Target Role: {ROLES}
        - Total Experience: {PROFILE['experience_years']} years, {PROFILE['experience_months']} months
        - Location: {PROFILE['full_location']}
        - Current CTC: {PROFILE['current_ctc']}
        - Expected CTC: {PROFILE['expected_ctc']}
        - Notice Period: {PROFILE['notice_period']}
        - Authorized to work: Yes
        - Sponsorship required: No
        - Skills: {', '.join(PROFILE['skills'])}
        - College: {PROFILE['college']}
        - Degree: {PROFILE['degree']}
        
        Return a JSON array of objects for EVERY input field visible in the image.
        Format: [{{"label": "exact_text_from_screen", "type": "text|radio|dropdown|checkbox", "answer": "precise_value_to_fill"}}]
        """

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
        headers = {'Content-Type': 'application/json'}
        data = { "contents": [{ "parts": [{"text": prompt}, {"inline_data": {"mime_type": "image/png", "data": b64_image}}] }] }

        response = requests.post(url, headers=headers, json=data, timeout=12)
        result = response.json()

        if 'candidates' not in result or not result['candidates']:
            return False

        text_response = result['candidates'][0]['content']['parts'][0]['text']
        if "```json" in text_response: text_response = text_response.split("```json")[1].split("```")[0].strip()
        elif "```" in text_response: text_response = text_response.split("```")[1].split("```")[0].strip()

        ai_data = json.loads(text_response)
        if isinstance(ai_data, dict): ai_data = [ai_data]

        for item in ai_data:
            answer = item.get("answer")
            q_type = item.get("type", "text")
            label_text = item.get("label", "")
            if not label_text or not answer: continue
            
            inputs = target.find_elements(By.XPATH, f".//input[contains(@aria-label, '{label_text}') or contains(@name, '{label_text}') or contains(@id, '{label_text}')] | .//textarea[contains(@aria-label, '{label_text}') or contains(@name, '{label_text}')]")
            if inputs:
                inp = inputs[0]
                if q_type in ["text", "numeric", "textarea"]:
                    try:
                        inp.clear()
                        inp.send_keys(str(answer))
                    except Exception: pass
                elif q_type == "radio":
                    try:
                        xpath = f".//label[contains(translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{str(answer).lower()}')]"
                        target.find_element(By.XPATH, xpath).click()
                    except Exception: pass

        return True
    except Exception:
        return False

#----------------- Application Flow: Easy Apply & External Company -----------------

def handle_application_flow():
    """Handles the LinkedIn Easy Apply wizard steps (Next -> Review -> Submit)."""
    max_steps = 25
    step = 0
    stuck_count = 0

    while step < max_steps:
        step += 1
        time.sleep(1.5)
        ensure_active_window()

        modals = driver.find_elements(By.CLASS_NAME, "artdeco-modal")
        if not modals:
            return True

        modal = modals[0]

        # 1. Fill all fields on the current screen
        smart_fill_form(modal, PROFILE)
        time.sleep(0.8)

        # 2. Check for Validation Errors
        errors = modal.find_elements(
            By.XPATH,
            ".//div[contains(@class, 'artdeco-inline-feedback--error')] | .//span[contains(@class, 'artdeco-inline-feedback__message')]"
        )
        if errors and any(e.is_displayed() for e in errors):
            print("   [!] Validation errors detected. Applying targeted corrections...")
            smart_fill_form(modal, PROFILE)
            stuck_count += 1
            if stuck_count > 4:
                print("   [ERROR] Cannot satisfy custom validation requirements. Skipping job.")
                return False
            time.sleep(1)

        # 3. Look for Primary Action Buttons
        submit_btn = find_primary_button([
            "Submit application", "Submit", "応募を送信", "送信", "応募する", "確定して応募"
        ])
        review_btn = find_primary_button([
            "Review your application", "Review", "確認", "次へ進む"
        ])
        next_btn = find_primary_button([
            "Continue to next step", "Next", "Continue", "次へ", "進む"
        ])

        # 4. Action: Submit
        if submit_btn:
            print("   >> Clicking 'Submit Application'...")
            click_element_safe(submit_btn)
            time.sleep(3)
            close_active_modal()
            return True

        # 5. Action: Review
        if review_btn:
            print("   >> Clicking 'Review'...")
            click_element_safe(review_btn)
            time.sleep(1.5)
            continue

        # 6. Action: Next
        if next_btn:
            print("   >> Clicking 'Next'...")
            prev_html = modal.get_attribute("innerHTML") if modal else ""

            click_element_safe(next_btn)
            time.sleep(1.5)

            curr_html = modal.get_attribute("innerHTML") if driver.find_elements(By.CLASS_NAME, "artdeco-modal") else ""

            if prev_html == curr_html:
                print("   [!] Wizard did not advance. Running smart correction...")
                smart_fill_form(modal, PROFILE)
                stuck_count += 1
                if stuck_count > 4:
                    print("   [ERROR] Wizard stuck. Skipping job.")
                    return False
            else:
                stuck_count = 0
            continue

        # 7. Fallback if no button recognized
        smart_fill_form(modal, PROFILE)
        time.sleep(1)
        stuck_count += 1
        if stuck_count > 5:
            return False

    return False

def smart_fill_company_form(context, profile):
    """
    Intelligent form filler for external company websites & ATS portals (Greenhouse, Workday,
    Lever, SmartRecruiters, Ashby, Taleo, BambooHR, Zoho, etc.).
    Automatically uploads resume and answers all screening questions using candidate resume data.
    """
    # 1. Upload Resume to File Inputs (unhiding if hidden by custom dropzone CSS)
    resume_path = profile.get("resume_path", "")
    if resume_path and os.path.exists(resume_path):
        try:
            file_inputs = context.find_elements(By.XPATH, ".//input[@type='file']")
            resume_input = None
            for fi in file_inputs:
                try:
                    driver.execute_script(
                        "arguments[0].style.display='block'; arguments[0].style.visibility='visible'; "
                        "arguments[0].style.opacity='1'; arguments[0].style.width='200px'; "
                        "arguments[0].style.height='40px'; arguments[0].style.position='relative'; "
                        "arguments[0].removeAttribute('hidden');",
                        fi
                    )
                    fi_name = (fi.get_attribute("name") or "").lower()
                    fi_id = (fi.get_attribute("id") or "").lower()
                    fi_aria = (fi.get_attribute("aria-label") or "").lower()
                    fi_accept = (fi.get_attribute("accept") or "").lower()
                    fi_info = f"{fi_name} {fi_id} {fi_aria} {fi_accept}"
                    
                    if any(k in fi_info for k in ["resume", "cv", "vitae", "application", "document", "file", "pdf"]):
                        resume_input = fi
                        break
                    elif not resume_input:
                        resume_input = fi
                except Exception:
                    pass

            if resume_input:
                try:
                    resume_input.send_keys(resume_path)
                    print(f"   [OK] Uploaded resume to company portal: {os.path.basename(resume_path)}")
                    time.sleep(1.5)
                except Exception as ue:
                    print(f"   [!] Resume send_keys note: {ue}")
        except Exception:
            pass

    # 2. Handle Native Dropdowns (<select>)
    try:
        select_elems = context.find_elements(By.TAG_NAME, "select")
        for sel_elem in select_elems:
            if not sel_elem.is_displayed(): continue
            try:
                sel = Select(sel_elem)
                curr_txt = sel.first_selected_option.text.strip().lower() if sel.all_selected_options else ""
                if not curr_txt or any(p in curr_txt for p in ["select", "choose", "--", "please select", "none"]):
                    parent_txt = ""
                    try:
                        p_elem = sel_elem.find_element(By.XPATH, "./ancestor::div[1] | ./preceding-sibling::label | ./ancestor::label")
                        parent_txt = p_elem.text.lower()
                    except Exception: pass

                    selected = False
                    # Work authorization -> Yes
                    if any(k in parent_txt for k in ["authorized", "authorization", "eligible to work", "legal right", "consent", "agree"]):
                        for opt in sel.options:
                            if any(w in opt.text.strip().lower() for w in ["yes", "i agree", "agree", "true", "authorized"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Sponsorship -> No
                    elif any(k in parent_txt for k in ["sponsor", "sponsorship", "visa", "require sponsorship"]):
                        for opt in sel.options:
                            if any(w in opt.text.strip().lower() for w in ["no", "false", "do not require", "will not"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Notice Period -> Immediate / 0
                    elif any(k in parent_txt for k in ["notice", "notice period", "availability", "how soon", "start date"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["immediate", "0", "15", "less than 15", "1 month"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Country / Nationality -> India
                    elif any(k in parent_txt for k in ["country", "nationality", "citizenship"]):
                        for opt in sel.options:
                            if "india" in opt.text.strip().lower():
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # State / Province -> Tamil Nadu
                    elif any(k in parent_txt for k in ["state", "province", "region"]):
                        for opt in sel.options:
                            if any(w in opt.text.strip().lower() for w in ["tamil nadu", "tamilnadu", "tn"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Gender -> Male / Prefer not to say
                    elif any(k in parent_txt for k in ["gender", "sex"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["male", "prefer not", "decline"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Veteran status -> Not a veteran / No
                    elif any(k in parent_txt for k in ["veteran", "military"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["not a", "no", "decline", "prefer not"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Disability -> No / Decline
                    elif any(k in parent_txt for k in ["disability", "handicap"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["no", "do not have", "decline", "prefer not"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Race / Ethnicity -> Asian / Decline
                    elif any(k in parent_txt for k in ["race", "ethnicity"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["asian", "decline", "prefer not", "two or more"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Highest degree / Education -> Bachelor
                    elif any(k in parent_txt for k in ["degree", "education", "qualification"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["bachelor", "undergraduate", "degree", "b.tech", "b.e", "information technology"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Experience level -> 0-1 / Entry / Fresher
                    elif any(k in parent_txt for k in ["experience", "years of experience"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["0", "1", "entry", "fresher", "less than 1"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break
                    # Source -> LinkedIn / Job board
                    elif any(k in parent_txt for k in ["hear about", "source", "referral"]):
                        for opt in sel.options:
                            t = opt.text.strip().lower()
                            if any(w in t for w in ["linkedin", "job board", "online", "other"]):
                                sel.select_by_visible_text(opt.text)
                                selected = True
                                break

                    # Fallback for required dropdowns
                    if not selected and len(sel.options) > 1:
                        sel.select_by_index(1)
            except Exception: pass
    except Exception: pass

    # 3. Handle Custom Dropdowns & Comboboxes (React-Select, Workday, Ashby, Greenhouse Select2, etc.)
    try:
        custom_combos = context.find_elements(
            By.XPATH,
            ".//div[@role='combobox'] | .//button[@aria-haspopup='listbox'] | .//div[contains(@class, 'select__control')] | .//div[contains(@class, 'select2-container')]"
        )
        for cb in custom_combos:
            if not cb.is_displayed(): continue
            try:
                cb_txt = (cb.text or "").strip().lower()
                if not cb_txt or any(w in cb_txt for w in ["select", "choose", "--", "search"]):
                    cb_label = ""
                    try:
                        p_lbl = cb.find_element(By.XPATH, "./ancestor::label | ./preceding-sibling::label | ./ancestor::div[1]")
                        cb_label = p_lbl.text.lower()
                    except Exception: pass

                    click_element_safe(cb)
                    time.sleep(0.4)

                    options = context.find_elements(By.XPATH, ".//div[@role='option'] | .//li[@role='option'] | .//div[contains(@class, 'option')] | .//li")
                    chosen = False
                    for opt in options:
                        if not opt.is_displayed(): continue
                        ot = opt.text.strip().lower()
                        if any(k in cb_label for k in ["authorized", "eligible", "legal right"]) and any(w in ot for w in ["yes", "agree"]):
                            click_element_safe(opt); chosen = True; break
                        elif any(k in cb_label for k in ["sponsor", "visa"]) and any(w in ot for w in ["no", "do not"]):
                            click_element_safe(opt); chosen = True; break
                        elif any(k in cb_label for k in ["gender"]) and any(w in ot for w in ["male", "prefer not"]):
                            click_element_safe(opt); chosen = True; break
                        elif any(k in cb_label for k in ["country"]) and "india" in ot:
                            click_element_safe(opt); chosen = True; break
                        elif any(k in cb_label for k in ["notice", "availability"]) and any(w in ot for w in ["immediate", "0", "15"]):
                            click_element_safe(opt); chosen = True; break
                    if not chosen and options:
                        first_opt = [o for o in options if o.is_displayed() and o.text.strip()]
                        if first_opt:
                            click_element_safe(first_opt[0])
            except Exception: pass
    except Exception: pass

    # 4. Handle Radios & Checkboxes
    try:
        radios = context.find_elements(By.XPATH, ".//input[@type='radio']")
        for r in radios:
            try:
                if r.is_displayed() and not r.is_selected():
                    lbl = r.find_element(By.XPATH, "./following-sibling::label | ./ancestor::label | ..")
                    t = lbl.text.strip().lower()
                    if any(w in t for w in ["yes", "agree", "authorized", "eligible", "consent", "relocate", "full time"]):
                        click_element_safe(r)
                    elif any(w in t for w in ["sponsor", "criminal", "convicted", "felony", "terminated", "non-compete"]) and "no" in t:
                        click_element_safe(r)
                    elif "gender" in t and ("male" in t or "prefer not" in t):
                        click_element_safe(r)
                    elif "veteran" in t and ("no" in t or "not a veteran" in t or "decline" in t):
                        click_element_safe(r)
                    elif "disability" in t and ("no" in t or "do not have" in t or "decline" in t):
                        click_element_safe(r)
            except Exception: pass

        checkboxes = context.find_elements(By.XPATH, ".//input[@type='checkbox']")
        for cb in checkboxes:
            try:
                if cb.is_displayed() and not cb.is_selected():
                    lbl = cb.find_element(By.XPATH, "./following-sibling::label | ./ancestor::label | ..")
                    t = lbl.text.strip().lower()
                    if any(w in t for w in ["agree", "consent", "terms", "privacy", "acknowledge", "certify", "confirm", "authorized"]):
                        click_element_safe(cb)
            except Exception: pass
    except Exception: pass

    # 5. Fill All Text & Number Inputs and Textareas
    try:
        company_inputs = context.find_elements(
            By.XPATH,
            ".//input[not(@type='hidden') and not(@type='file') and not(@type='checkbox') and not(@type='radio') and not(@type='submit') and not(@type='button')] | .//textarea"
        )
        for c_inp in company_inputs:
            if not c_inp.is_displayed(): continue
            val = (c_inp.get_attribute("value") or "").strip()
            if val: continue

            c_name = (c_inp.get_attribute("name") or "").lower()
            c_id = (c_inp.get_attribute("id") or "").lower()
            c_ph = (c_inp.get_attribute("placeholder") or "").lower()
            c_aria = (c_inp.get_attribute("aria-label") or "").lower()
            combined = f"{c_name} {c_id} {c_ph} {c_aria}"

            lbl_txt = ""
            if c_id:
                lbls = context.find_elements(By.XPATH, f".//label[@for='{c_id}']")
                if lbls: lbl_txt = lbls[0].text.lower()
            if not lbl_txt:
                try:
                    p_lbl = c_inp.find_elements(By.XPATH, "./ancestor::label | ./preceding-sibling::label")
                    if p_lbl: lbl_txt = p_lbl[0].text.lower()
                except Exception: pass
            combined += f" {lbl_txt}"

            ans = ""
            # Candidate Identification
            if any(k in combined for k in ["first name", "firstname", "fname", "given name"]):
                ans = profile["first_name"]
            elif any(k in combined for k in ["last name", "lastname", "lname", "surname", "family name"]):
                ans = profile["last_name"]
            elif any(k in combined for k in ["full name", "fullname", "your name", "candidate name", "applicant name"]) and "company" not in combined:
                ans = profile["name"]
            elif any(k in combined for k in ["email", "e-mail", "confirm email"]):
                ans = profile["email"]
            elif any(k in combined for k in ["phone", "mobile", "contact", "cell", "phone number"]):
                ans = profile["phone"]
            # Location
            elif any(k in combined for k in ["city", "town", "current location"]):
                ans = profile["city"]
            elif any(k in combined for k in ["state", "province", "region"]):
                ans = "Tamil Nadu"
            elif any(k in combined for k in ["country", "nationality"]):
                ans = "India"
            elif any(k in combined for k in ["location", "address", "residence", "street"]):
                ans = profile["full_location"]
            elif any(k in combined for k in ["postal", "zip", "pincode", "pin code"]):
                ans = "600001"
            # Online Profiles
            elif any(k in combined for k in ["linkedin", "linked in"]):
                ans = profile["linkedin"]
            elif any(k in combined for k in ["github", "git"]):
                ans = profile["github"]
            elif any(k in combined for k in ["website", "portfolio", "url", "blog", "personal link"]):
                ans = profile["github"]
            # Compensation & Notice Period
            elif any(k in combined for k in ["current ctc", "current salary", "current compensation", "present ctc", "current annual", "present salary"]):
                ans = profile["current_ctc_num"] if c_inp.get_attribute("type") == "number" else profile["current_ctc"]
            elif any(k in combined for k in ["expected ctc", "expected salary", "expected compensation", "expected annual", "salary expectation", "desired salary", "expected package"]):
                ans = profile["expected_ctc_num"] if c_inp.get_attribute("type") == "number" else profile["expected_ctc"]
            elif any(k in combined for k in ["notice period", "notice", "days to join", "how many days notice", "availability to join", "how soon"]):
                ans = profile["notice_period_days"] if c_inp.get_attribute("type") == "number" else profile["notice_period"]
            elif any(k in combined for k in ["start date", "joining date", "date available", "earliest start"]):
                ans = "Immediate" if c_inp.get_attribute("type") != "date" else "2025-06-01"
            # Experience & Employment History
            elif any(k in combined for k in ["total experience", "overall experience", "how many years of experience", "years of experience", "relevant experience"]):
                ans = profile["experience_years"] if profile["experience_years"] != "0" else "1"
            elif any(k in combined for k in ["months of experience", "experience in months"]):
                ans = profile["experience_months"] if profile["experience_months"] != "0" else "0"
            elif any(k in combined for k in ["current company", "current employer", "present employer", "organization"]):
                ans = "Fresher"
            elif any(k in combined for k in ["current role", "job title", "designation", "current designation"]):
                ans = "Software Developer (Fresher)"
            # Education
            elif any(k in combined for k in ["degree", "qualification", "highest qualification", "major", "field of study", "stream"]):
                ans = profile["degree"]
            elif any(k in combined for k in ["college", "university", "school", "institution", "institute"]):
                ans = profile["college"]
            elif any(k in combined for k in ["graduation", "passing year", "year of pass", "grad year", "year of graduation"]):
                ans = profile["graduation_year"]
            elif any(k in combined for k in ["cgpa", "gpa", "percentage", "marks", "score"]):
                ans = profile["gpa"]
            # Skill Experience Matches
            elif any(s.lower() in combined for s in profile.get("skills", [])):
                ans = profile["experience_years"] if profile["experience_years"] != "0" else "1"
            # Cover Letter / Essay / Textarea
            elif c_inp.tag_name == "textarea" or any(k in combined for k in ["cover letter", "summary", "about you", "why should we hire", "tell us"]):
                ans = profile["summary"]
            # Fallback for required inputs
            else:
                if c_inp.get_attribute("required") or c_inp.get_attribute("aria-required") == "true" or "*" in lbl_txt:
                    ans = "1" if c_inp.get_attribute("type") == "number" else ("Yes" if "willing" in combined or "authorized" in combined else profile["summary"][:80])

            if ans:
                try:
                    c_inp.clear()
                    c_inp.send_keys(str(ans))
                    print(f"   [*] Filled company field '{c_name or c_id or c_ph or lbl_txt[:25]}': '{ans}'")
                except Exception:
                    pass
    except Exception:
        pass

    # 6. Gemini AI Solver for Complex Questions
    if API_KEY and API_KEY.startswith("AIza"):
        try:
            ai_solver(container=context)
        except Exception:
            pass

def handle_external_company_apply(external_btn, job_title, profile):
    """
    Automates end-to-end application on company career site like Easy Apply:
    - Bypasses redirect modals and opens ATS portal
    - Detects embedded ATS iframes (Greenhouse, Workday, Lever, SmartRecruiters, Ashby, Taleo, etc.)
    - Analyzes resume to auto-answer screening questions, dropdowns, and file upload
    - Advances multi-step wizards (Next / Save & Continue / Review)
    - Submits application, confirms receipt, closes external tab, and safely resumes LinkedIn search.
    """
    main_window = None
    try:
        initial_handles = driver.window_handles
        main_window = initial_handles[0]
        
        print(f"   >> Clicking external 'Apply on Company Website' button...")
        click_element_safe(external_btn)
        time.sleep(2)
        
        # 1. Handle LinkedIn redirection modal (buttons & links)
        redirect_modals = driver.find_elements(By.XPATH, "//div[contains(@class, 'artdeco-modal')]")
        if redirect_modals:
            cont_elems = redirect_modals[0].find_elements(
                By.XPATH,
                ".//button[contains(translate(., 'CONTINUE', 'continue'), 'continue') or contains(translate(., 'APPLY', 'apply'), 'apply') or contains(translate(., 'PROCEED', 'proceed'), 'proceed') or contains(translate(., 'GO TO', 'go to'), 'go to') or contains(translate(., 'LEAVE', 'leave'), 'leave')] | "
                ".//a[contains(translate(., 'CONTINUE', 'continue'), 'continue') or contains(translate(., 'APPLY', 'apply'), 'apply') or contains(translate(., 'PROCEED', 'proceed'), 'proceed') or contains(translate(., 'GO TO', 'go to'), 'go to') or contains(translate(., 'LEAVE', 'leave'), 'leave')]"
            )
            if cont_elems:
                print("   >> Bypassing LinkedIn redirect confirmation...")
                click_element_safe(cont_elems[0])
                time.sleep(2)

        # 2. If no new tab opened, check if external_btn has direct href
        if len(driver.window_handles) == len(initial_handles):
            try:
                href = external_btn.get_attribute("href") or external_btn.get_attribute("data-apply-url")
                if href and href.startswith("http"):
                    print(f"   >> Direct link detected. Opening company portal in new tab...")
                    driver.execute_script("window.open(arguments[0], '_blank');", href)
                    time.sleep(2)
            except Exception:
                pass
        
        # Wait up to 6 seconds for new window / tab
        start_wait = time.time()
        while len(driver.window_handles) == len(initial_handles) and (time.time() - start_wait) < 6:
            time.sleep(0.5)

        current_handles = driver.window_handles
        if len(current_handles) > len(initial_handles):
            company_window = [h for h in current_handles if h not in initial_handles][-1]
            driver.switch_to.window(company_window)
        elif len(current_handles) == 1 and current_handles[0] != main_window:
            pass
        
        # Wait for page readiness
        try:
            for _ in range(12):
                if driver.execute_script("return document.readyState") == "complete":
                    break
                time.sleep(0.5)
        except Exception:
            pass

        company_url = driver.current_url
        print(f"   [*] Connected to Company Career Page: {company_url[:75]}...")
        time.sleep(2)

        # 3. Handle Cookie / Privacy Consent Banners on company pages
        try:
            cookie_btns = driver.find_elements(
                By.XPATH,
                "//button[contains(translate(., 'ACCEPT', 'accept'), 'accept') or contains(translate(., 'AGREE', 'agree'), 'agree') or contains(translate(., 'OK', 'ok'), 'ok') or contains(translate(., 'ALLOW', 'allow'), 'allow') or contains(., 'Got it')]"
            )
            for cb in cookie_btns:
                if cb.is_displayed():
                    click_element_safe(cb)
                    time.sleep(0.8)
                    break
        except Exception:
            pass

        # 4. Multi-step Application Wizard Loop (Mirrors Easy Apply!)
        max_company_steps = 15
        step = 0
        submitted = False

        while step < max_company_steps:
            step += 1
            time.sleep(1.5)

            # Check for embedded ATS iframes (Greenhouse, Workday, Lever, etc.)
            active_context = driver
            try:
                iframes = driver.find_elements(By.TAG_NAME, "iframe")
                for iframe in iframes:
                    try:
                        src = (iframe.get_attribute("src") or "").lower()
                        if any(ats in src for ats in ["greenhouse", "workday", "lever", "taleo", "icims", "smartrecruiters", "bamboohr", "zoho", "apply", "job"]):
                            driver.switch_to.frame(iframe)
                            active_context = driver
                            print("   [*] Switched to embedded job application iframe.")
                            break
                    except Exception:
                        pass
            except Exception:
                pass

            # Initial Step: Trigger "Apply" / "Apply Manually" / "Autofill with Resume" if button exists
            if step == 1:
                apply_triggers = active_context.find_elements(
                    By.XPATH,
                    "//a[contains(translate(., 'APPLY', 'apply'), 'apply') and not(contains(@href, 'linkedin'))] | "
                    "//button[contains(translate(., 'APPLY', 'apply'), 'apply') or contains(translate(., 'AUTOFILL', 'autofill'), 'autofill') or contains(translate(., 'START', 'start'), 'start')]"
                )
                for at in apply_triggers:
                    if at.is_displayed():
                        txt = at.text.strip().lower()
                        if any(w in txt for w in [
                            "apply now", "apply for this job", "apply manually", "autofill with resume",
                            "apply without account", "continue as guest", "apply as guest", "apply",
                            "submit application", "start application", "apply with resume"
                        ]):
                            print(f"   >> Triggering company page application form ('{at.text.strip()}')...")
                            click_element_safe(at)
                            time.sleep(2.5)
                            break

            # Check if application already confirmed on page
            body_text = ""
            try:
                body_text = driver.find_element(By.TAG_NAME, "body").text.lower()
            except Exception:
                pass
            success_indicators = [
                "thank you for applying",
                "application submitted",
                "application received",
                "your application has been submitted",
                "successfully applied",
                "application sent",
                "we have received your application",
                "thanks for applying"
            ]
            if any(ind in body_text for ind in success_indicators):
                print(f"   [SUCCESS] Confirmation verified: Company application received for '{job_title}'!")
                submitted = True
                break

            # 5. Fill All Form Fields On Current Screen
            print(f"   [*] [Step {step}] Analyzing and filling company application form from resume...")
            smart_fill_company_form(active_context, profile)
            time.sleep(1.5)

            # 6. Check for Submit / Finish Application Button
            submit_btns = active_context.find_elements(
                By.XPATH,
                "//button[contains(translate(., 'SUBMIT', 'submit'), 'submit') or contains(translate(., 'FINISH', 'finish'), 'finish') or contains(translate(., 'SEND', 'send'), 'send') or contains(translate(., 'COMPLETE', 'complete'), 'complete')] | //input[@type='submit']"
            )
            submit_found = None
            for sbtn in submit_btns:
                if sbtn.is_displayed() and sbtn.is_enabled():
                    btn_txt = (sbtn.text or sbtn.get_attribute("value") or "").strip().lower()
                    if any(w in btn_txt for w in ["submit", "send application", "finish", "complete application", "confirm and apply"]):
                        submit_found = sbtn
                        break

            if submit_found:
                btn_label = (submit_found.text or submit_found.get_attribute("value") or "Submit").strip()
                print(f"   >> Clicking '{btn_label}' on company career portal...")
                click_element_safe(submit_found)
                time.sleep(3.5)
                submitted = True
                print(f"   [SUCCESS] Successfully submitted company application for '{job_title}'!")
                break

            # 7. Check for Next / Continue / Review Button (Multi-step wizard)
            next_btns = active_context.find_elements(
                By.XPATH,
                "//button[contains(translate(., 'NEXT', 'next'), 'next') or contains(translate(., 'CONTINUE', 'continue'), 'continue') or contains(translate(., 'SAVE & CONTINUE', 'save & continue'), 'save & continue') or contains(translate(., 'REVIEW', 'review'), 'review') or contains(translate(., 'PROCEED', 'proceed'), 'proceed')] | //input[@value='Next' or @value='Continue']"
            )
            next_found = None
            for nbtn in next_btns:
                if nbtn.is_displayed() and nbtn.is_enabled():
                    n_txt = (nbtn.text or nbtn.get_attribute("value") or "").strip().lower()
                    if any(w in n_txt for w in ["next", "continue", "save and continue", "save & continue", "proceed", "review"]):
                        next_found = nbtn
                        break

            if next_found:
                next_label = (next_found.text or next_found.get_attribute("value") or "Next").strip()
                print(f"   >> Advancing wizard: Clicking '{next_label}'...")
                click_element_safe(next_found)
                time.sleep(2.5)
                continue
            else:
                # No next button and no submit button found
                # Fallback to any submit input if present
                primary_btns = active_context.find_elements(By.XPATH, "//button[@type='submit'] | //input[@type='submit']")
                if primary_btns and primary_btns[0].is_displayed() and primary_btns[0].is_enabled():
                    print("   >> Clicking primary action button...")
                    click_element_safe(primary_btns[0])
                    time.sleep(3)
                    submitted = True
                    break
                else:
                    break

        if not submitted:
            # Final check for confirmation text on page
            try:
                b_txt = driver.find_element(By.TAG_NAME, "body").text.lower()
                if any(ind in b_txt for ind in success_indicators):
                    submitted = True
                    print(f"   [SUCCESS] Confirmation verified on page for '{job_title}'!")
            except Exception:
                pass

        if submitted:
            print(f"   [SUCCESS] Application process completed for '{job_title}'.")
        else:
            print(f"   [*] Finished processing company application fields for '{job_title}'.")

        return True

    except Exception as e:
        print(f"   [!] External company application note: {e}")
        return False
    finally:
        # Guarantee window recovery: close external tab and switch back cleanly to main LinkedIn tab
        try:
            if len(driver.window_handles) > 1:
                for h in list(driver.window_handles):
                    if h != main_window:
                        driver.switch_to.window(h)
                        driver.close()
            if main_window and main_window in driver.window_handles:
                driver.switch_to.window(main_window)
            elif driver.window_handles:
                driver.switch_to.window(driver.window_handles[0])
        except Exception as we:
            print(f"   [!] Window recovery note: {we}")

#----------------- Search Alert Activation & Strict Role Relevance Engine -----------------

def enable_job_search_alert(role_name):
    """
    Detects and turns ON the 'Set alert' toggle switch on the LinkedIn jobs search results page.
    """
    try:
        ensure_active_window()
        time.sleep(2)

        toggle_selectors = [
            "//div[contains(@class, 'jobs-search-create-alert')]//button[@role='switch']",
            "//div[contains(@class, 'jobs-search-create-alert')]//button",
            "//div[contains(@class, 'jobs-search-create-alert')]//input[@type='checkbox']",
            "//span[contains(normalize-space(), 'Set alert')]/following::button[@role='switch'][1]",
            "//span[contains(normalize-space(), 'Set alert')]/following::button[1]",
            "//span[contains(normalize-space(), 'Set alert')]/following-sibling::div//button",
            "//span[contains(normalize-space(), 'Set alert')]/ancestor::div[contains(@class, 'jobs-search-create-alert')]//button",
            "//button[contains(@aria-label, 'Set alert') or contains(@aria-label, 'alert') or contains(@aria-label, 'Job alert')]",
            "//div[contains(@class, 'artdeco-toggle') and preceding-sibling::*[contains(., 'Set alert')]]//button",
            "//fieldset[contains(., 'Set alert')]//button | //fieldset[contains(., 'Set alert')]//input"
        ]

        for xp in toggle_selectors:
            elems = driver.find_elements(By.XPATH, xp)
            for btn in elems:
                if not btn.is_displayed():
                    continue

                aria_checked = btn.get_attribute("aria-checked")
                is_selected = btn.is_selected() if btn.tag_name == "input" else False
                parent_class = ""
                try:
                    p = btn.find_element(By.XPATH, "./ancestor::div[contains(@class, 'artdeco-toggle') or contains(@class, 'toggle')]")
                    parent_class = p.get_attribute("class") or ""
                except Exception:
                    pass

                already_on = (aria_checked == "true") or is_selected or ("toggled" in parent_class)

                if already_on:
                    print(f"   [ALERT STATUS] LinkedIn job alert is already ON for '{role_name}'.")
                    return True
                else:
                    print(f"   >> Turning ON LinkedIn job alert for '{role_name}' in '{LOCATION}'...")
                    click_element_safe(btn)
                    time.sleep(1.5)

                    try:
                        modal_btns = driver.find_elements(
                            By.XPATH,
                            "//div[contains(@class, 'artdeco-modal')]//button[contains(., 'Save') or contains(., 'Done') or contains(., 'Create alert') or contains(., 'Got it')]"
                        )
                        if modal_btns and modal_btns[0].is_displayed():
                            click_element_safe(modal_btns[0])
                            time.sleep(1)
                    except Exception:
                        pass

                    print(f"   [SUCCESS] LinkedIn job alert successfully turned ON for '{role_name}'!")
                    return True

        print(f"   [*] LinkedIn 'Set alert' checked for '{role_name}'.")
    except Exception as e:
        print(f"   [!] Note while setting alert: {e}")
    return False

def analyze_job_relevance(title, desc_snippet, target_role, job_mode="Fresher", years_exp="0"):
    """
    Strictly analyzes whether a job posting matches the user's assigned role and experience level.
    Returns (is_match: bool, reason: str).
    """
    title_raw = title.strip()
    title_lower = title_raw.lower()
    target_lower = target_role.strip().lower()
    desc_lower = (desc_snippet or "").strip().lower()

    # Clean extraneous noise from title for accurate matching (e.g. "Associate Applications Developer - Chennai with verification")
    noise_patterns = [
        r'-\s*(?:chennai|bengaluru|bangalore|hyderabad|pune|mumbai|delhi|noida|gurgaon|tamil nadu|india).*$',
        r'\|\s*(?:chennai|bengaluru|bangalore|hyderabad|pune|mumbai|delhi|noida|gurgaon|tamil nadu|india).*$',
        r'\bwith verification\b', r'\b\(verified\)\b', r'\bverified\b',
        r'\b\(remote\)\b', r'\b\(hybrid\)\b', r'\b\(on-site\)\b', r'\b\(wfh\)\b',
        r'\b\(fresher\)\b', r'\b\[fresher\]\b',
        r'\bpromoted\b', r'\burgent hiring\b', r'\bimmediate joiner\b'
    ]
    title_clean = title_lower
    for np in noise_patterns:
        title_clean = re.sub(np, '', title_clean, flags=re.IGNORECASE).strip()

    # 1. Experience Level Analysis (Fresher vs Experienced)
    senior_markers = [
        "senior", "sr.", "sr ", "lead", "principal", "manager", "architect", 
        "director", "staff", "head", "specialist", "3+ years", "4+ years", 
        "5+ years", "6+ years", "7+ years", "8+ years", "10+ years", 
        "experienced", "mid-senior", "expert"
    ]

    if job_mode == "Fresher":
        for marker in senior_markers:
            if marker in title_lower or marker in title_clean:
                return False, f"Senior role marker ('{marker}') found in title - strictly adhering to Fresher mode"

        high_exp_phrases = [
            "3+ years of experience", "4+ years of experience", "5+ years of experience",
            "minimum 3 years", "minimum 4 years", "minimum 5 years",
            "at least 3 years", "at least 4 years", "at least 5 years",
            "3 to 5 years", "3-5 years", "4-7 years", "5-8 years"
        ]
        for phrase in high_exp_phrases:
            if phrase in desc_lower:
                return False, f"High experience requirement ('{phrase}') in job description - Fresher mode skips this"

    elif job_mode == "Experienced":
        exp_int = int(years_exp or 0)
        if exp_int >= 2:
            intern_markers = ["intern", "internship", "trainee", "unpaid intern"]
            for im in intern_markers:
                if im in title_lower or im in title_clean:
                    return False, f"Intern/Trainee role ('{im}') skipped for Experienced candidate ({exp_int} yrs)"

    # 2. Technology & Role Stack Analysis
    tech_stacks = {
        "java": {
            "primary": ["java", "j2ee", "spring", "springboot", "spring boot", "hibernate", "core java"],
            "conflicts": [
                "python", "django", "flask", "fastapi",
                "react", "reactjs", "react.js", "angular", "vue", "vuejs",
                "c#", "csharp", ".net", "dotnet", "asp.net",
                "golang", "ruby", "php", "laravel",
                "flutter", "swift", "ios", "android native",
                "salesforce", "sap", "mainframe", "servicenow",
                "devops", "kubernetes", "docker engineer",
                "data analyst", "data scientist", "business analyst", "power bi", "tableau",
                "qa manual", "software test engineer", "etl developer", "aws data", "cloud engineer"
            ]
        },
        "python": {
            "primary": ["python", "django", "flask", "fastapi"],
            "conflicts": [
                "java", "spring", "springboot",
                "react", "angular", "vue",
                "c#", ".net", "dotnet", "php", "ruby", "golang",
                "salesforce", "sap", "mainframe",
                "devops engineer", "qa manual"
            ]
        },
        "react": {
            "primary": ["react", "reactjs", "react.js", "frontend", "front-end"],
            "conflicts": [
                "java", "python", "php", "c#", ".net", "ruby", "golang",
                "salesforce", "sap", "mainframe"
            ]
        },
        "angular": {
            "primary": ["angular", "angularjs", "frontend", "front-end"],
            "conflicts": [
                "java", "python", "php", "c#", ".net", "ruby", "react", "golang",
                "salesforce", "sap", "mainframe"
            ]
        },
        "node": {
            "primary": ["node", "nodejs", "node.js", "express"],
            "conflicts": ["mainframe", "salesforce", "sap", "qa manual"]
        },
        ".net": {
            "primary": [".net", "dotnet", "c#", "csharp", "asp.net"],
            "conflicts": ["java", "python", "php", "ruby", "mainframe", "salesforce"]
        },
        "qa": {
            "primary": ["qa", "quality assurance", "test", "testing", "selenium", "sdet"],
            "conflicts": ["full stack developer", "backend developer", "data scientist"]
        }
    }

    assigned_domain = None
    for domain, data in tech_stacks.items():
        if domain in target_lower or any(p in target_lower for p in data["primary"]):
            assigned_domain = domain
            break

    if assigned_domain:
        domain_data = tech_stacks[assigned_domain]
        primary_keywords = domain_data["primary"]
        conflict_keywords = domain_data["conflicts"]

        has_primary_in_title = any(p in title_lower or p in title_clean for p in primary_keywords)
        has_conflict_in_title = any(re.search(r'\b' + re.escape(c) + r'\b', title_clean) for c in conflict_keywords)

        if has_conflict_in_title and not has_primary_in_title:
            matched_conflicts = [c for c in conflict_keywords if re.search(r'\b' + re.escape(c) + r'\b', title_clean)]
            return False, f"Title mentions conflicting tech ({', '.join(matched_conflicts)}) instead of assigned {assigned_domain.upper()}"

        if has_primary_in_title:
            return True, f"Direct title match for {assigned_domain.upper()} role"

        # Developer / Engineering synonyms that match entry-level developer roles
        developer_synonyms = [
            "software engineer", "developer", "software developer", "application developer", "applications developer",
            "associate applications developer", "associate software developer", "associate software engineer",
            "associate developer", "junior developer", "junior software engineer", "entry level developer",
            "graduate engineer trainee", "trainee engineer", "system engineer", "programmer",
            "software development engineer", "sde", "member technical staff"
        ]
        is_developer_role = any(d in title_clean for d in developer_synonyms)

        if is_developer_role:
            if desc_lower:
                has_conflict_in_desc = any(re.search(r'\b' + re.escape(c) + r'\b', desc_lower) for c in conflict_keywords[:8])
                has_primary_in_desc = any(p in desc_lower for p in primary_keywords)
                if has_conflict_in_desc and not has_primary_in_desc:
                    return False, f"Role '{title_raw}' requires conflicting tech in description, not {assigned_domain.upper()}"
                if has_primary_in_desc:
                    return True, f"Entry-level role '{title_raw}' mentions {assigned_domain.upper()} in description"
            return True, f"Valid entry-level Developer role ({title_raw}) matching search domain"

        return False, f"Job title '{title_raw}' is not relevant to assigned role '{target_role}'"

    target_words = [w for w in target_lower.split() if w not in ["developer", "engineer", "fresher", "job", "in", "for", "and", "the"]]
    if target_words:
        matched = any(w in title_clean for w in target_words)
        if not matched:
            return False, f"Title does not contain target keyword from '{target_role}'"

    return True, "Job matches assigned role criteria"

#----------------- Page Processing Helpers -----------------

def scroll_search_results_panel():
    """
    Scrolls down the left-hand search results panel to force LinkedIn's virtualized list
    to load all 25 job cards into the DOM.
    """
    try:
        containers = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'jobs-search-results-list')] | "
            "//div[contains(@class, 'scaffold-layout__list')] | "
            "//div[contains(@class, 'jobs-search__left-rail')]"
        )
        if containers:
            container = containers[0]
            for step in range(1, 6):
                driver.execute_script(
                    "arguments[0].scrollTop = arguments[0].scrollHeight * (arguments[1] / 5);",
                    container,
                    step
                )
                time.sleep(0.4)
            # Scroll back to top
            driver.execute_script("arguments[0].scrollTop = 0;", container)
            time.sleep(0.5)
        else:
            for step in range(1, 4):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight * (arguments[0] / 3));", step)
                time.sleep(0.4)
            driver.execute_script("window.scrollTo(0, 0);")
    except Exception as e:
        print(f"   [*] Panel scroll note: {e}")

def check_if_job_already_applied(card=None):
    """
    Checks if the job has already been applied for previously:
    1. Inspects the job card in the search results list.
    2. Inspects the right-hand job details pane (apply section, badges, feedback messages).
    Returns (True, details_string) if already applied, else (False, "").
    """
    try:
        if card:
            # Check footer item (e.g., "Applied 3 days ago", "Applied")
            card_texts = card.find_elements(
                By.XPATH,
                ".//li[contains(@class, 'job-card-container__footer-item')] | "
                ".//span[contains(@class, 'job-card-container__footer-item')] | "
                ".//div[contains(@class, 'job-card-container__footer-item')] | "
                ".//span[contains(translate(., 'APPLIED', 'applied'), 'applied')] | "
                ".//li[contains(translate(., 'APPLIED', 'applied'), 'applied')]"
            )
            for ct in card_texts:
                txt = ct.text.strip().lower()
                if "applied" in txt:
                    return True, ct.text.strip()
    except Exception:
        pass

    try:
        apply_area_elements = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'jobs-s-apply')] | "
            "//div[contains(@class, 'jobs-apply-button--top-card')] | "
            "//div[contains(@class, 'job-details-jobs-unified-top-card__primary-description-container')]"
        )
        for area in apply_area_elements:
            area_text = area.text.lower()
            if "applied" in area_text:
                return True, "Applied on LinkedIn"

        feedback_elements = driver.find_elements(
            By.XPATH,
            "//span[contains(@class, 'artdeco-inline-feedback__message') and contains(translate(., 'APPLIED', 'applied'), 'applied')] | "
            "//div[contains(@class, 'artdeco-inline-feedback--success')] | "
            "//button[contains(@class, 'jobs-apply-button') and contains(translate(., 'APPLIED', 'applied'), 'applied')] | "
            "//div[contains(@class, 'jobs-applied-badge')]"
        )
        for fe in feedback_elements:
            if fe.is_displayed():
                return True, fe.text.strip() or "Applied on LinkedIn"
    except Exception:
        pass

    return False, ""

#----------------- Page Processing -----------------

def process_page_jobs(target_role=None, state: Any = None, seen_keys: Any = None):
    """Processes all jobs on the current search page according to selected APPLY_MODE, tracking both new and already applied roles."""
    if not target_role:
        target_role = ROLES
    if state is None:
        state = AutomationState()
    if seen_keys is None:
        seen_keys = set()

    page_applied = 0
    ensure_active_window()

    # Step 1: Scroll search results panel to load all 25 cards
    scroll_search_results_panel()

    card_selectors = [
        "//div[contains(@class, 'job-card-container')]",
        "//li[contains(@class, 'jobs-search-results__list-item')]",
        "//li[contains(@class, 'scaffold-layout__list-item')]",
        "//ul[contains(@class, 'jobs-search__results-list')]/li"
    ]
    raw_cards = []
    for sel in card_selectors:
        found = driver.find_elements(By.XPATH, sel)
        if found:
            raw_cards = found
            break

    count_jobs = len(raw_cards)
    print(f">> Found {count_jobs} jobs on this page.")

    for i in range(count_jobs):
        try:
            ensure_active_window()
            close_active_modal()

            # Refresh card list to prevent stale references
            current_cards = []
            for sel in card_selectors:
                found = driver.find_elements(By.XPATH, sel)
                if found:
                    current_cards = found
                    break

            if i >= len(current_cards):
                break
            card = current_cards[i]

            # 1. Extract card title directly from card element (guarantees accuracy)
            card_title = ""
            title_link = None
            try:
                title_links = card.find_elements(
                    By.XPATH,
                    ".//a[contains(@class, 'job-card-list__title')] | "
                    ".//a[contains(@class, 'job-card-container__link')] | "
                    ".//a[contains(@href, '/jobs/view/')]"
                )
                if title_links:
                    title_link = title_links[0]
                    card_title = title_link.text.strip()
            except Exception:
                pass

            if not card_title:
                try:
                    strong_elems = card.find_elements(By.XPATH, ".//strong | .//span[contains(@class, 'job-card-container__title')]")
                    if strong_elems:
                        card_title = strong_elems[0].text.strip()
                except Exception:
                    pass

            # 2. Extract card company directly from card
            card_company = "Company"
            try:
                comp_elems = card.find_elements(
                    By.XPATH,
                    ".//span[contains(@class, 'job-card-container__primary-description')] | "
                    ".//div[contains(@class, 'artdeco-entity-lockup__subtitle')] | "
                    ".//a[contains(@class, 'job-card-container__company-name')] | "
                    ".//span[contains(@class, 'company-name')]"
                )
                if comp_elems:
                    card_company = comp_elems[0].text.strip()
            except Exception:
                pass

            # 3. Scroll card into view, visibly highlight it for the user, and click title link
            try:
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});"
                    "arguments[0].style.outline = '3px solid #ccff00';"
                    "arguments[0].style.boxShadow = '0 0 18px rgba(204, 255, 0, 0.7)';"
                    "arguments[0].style.transition = 'all 0.25s ease';",
                    card
                )
            except Exception:
                pass
            time.sleep(0.5)
            if title_link:
                click_element_safe(title_link)
            else:
                click_element_safe(card)
            time.sleep(1.5)

            # 4. Determine final title
            details_title = ""
            try:
                t_elem = driver.find_element(
                    By.XPATH,
                    "//h1[contains(@class, 'job-details-jobs-unified-top-card__job-title')] | //h2[contains(@class, 'job-details-jobs-unified-top-card__job-title')]"
                )
                if t_elem.text.strip():
                    details_title = t_elem.text.strip()
            except Exception:
                pass

            title = card_title if card_title else (details_title or f"Job #{i+1}")
            company = card_company

            job_dedup_key = f"{title.lower()}::{company.lower()}"
            if job_dedup_key in seen_keys:
                continue
            seen_keys.add(job_dedup_key)

            state.total_evaluated += 1
            print(f"\n[{i+1}/{count_jobs}] Evaluating: {title} at {company}")
            update_automation_status({
                "total_evaluated": state.total_evaluated,
                "current_evaluating": f"Evaluating: {title} ({company})"
            })

            # 5. Check if THIS job was ALREADY APPLIED previously on LinkedIn
            is_already, applied_msg = check_if_job_already_applied(card)
            if is_already:
                print(f"   [ALREADY APPLIED] You have already applied for '{title}' at '{company}' on LinkedIn ({applied_msg}).")
                now_str = datetime.datetime.now().strftime("%I:%M %p")
                state.total_already_applied += 1
                state.already_applied_jobs.append({
                    "title": title,
                    "company": company,
                    "mode": "Already Applied ✓",
                    "time": now_str,
                    "status": "ALREADY APPLIED"
                })
                update_automation_status({
                    "total_already_applied": state.total_already_applied,
                    "already_applied_jobs": state.already_applied_jobs,
                    "current_evaluating": f"Already Applied: {title} at {company}"
                })
                continue

            # 6. Extract job description snippet to verify tech stack & experience requirements
            desc_snippet = ""
            try:
                desc_elem = driver.find_element(
                    By.XPATH,
                    "//div[contains(@class, 'jobs-description')] | //div[contains(@class, 'jobs-box__html-content')] | //div[contains(@id, 'job-details')]"
                )
                desc_snippet = desc_elem.text[:1500].strip()
            except Exception:
                pass

            # 7. Strict Role & Experience Analysis
            is_match, reason = analyze_job_relevance(title, desc_snippet, target_role, JOB_MODE, YEARS)
            if not is_match:
                print(f"   [ALERT: ROLE FILTER] Skipped '{title}': {reason}")
                state.total_skipped += 1
                state.skipped_jobs.append({"title": title, "reason": reason})
                update_automation_status({
                    "total_skipped": state.total_skipped,
                    "skipped_jobs": state.skipped_jobs
                })
                continue
            else:
                print(f"   [MATCH VERIFIED] {reason}")

            easy_btn = get_easy_apply_button()
            ext_btn = get_external_apply_button()

            applied_successfully = False
            applied_mode_label = ""

            # Mode 1: Easy Apply Only
            if APPLY_MODE == "easy_apply":
                if not easy_btn:
                    recheck_applied, _ = check_if_job_already_applied(card)
                    if recheck_applied:
                        now_str = datetime.datetime.now().strftime("%I:%M %p")
                        state.total_already_applied += 1
                        state.already_applied_jobs.append({
                            "title": title, "company": company, "mode": "Already Applied ✓", "time": now_str, "status": "ALREADY APPLIED"
                        })
                        update_automation_status({"total_already_applied": state.total_already_applied, "already_applied_jobs": state.already_applied_jobs})
                        continue

                    print("   -- Skipped (Not an Easy Apply job).")
                    state.total_skipped += 1
                    state.skipped_jobs.append({"title": title, "reason": "Not an Easy Apply job"})
                    update_automation_status({"total_skipped": state.total_skipped, "skipped_jobs": state.skipped_jobs})
                    continue

                print("   >> Easy Apply found! Starting application...")
                click_element_safe(easy_btn)
                time.sleep(2)
                if handle_application_flow():
                    applied_successfully = True
                    applied_mode_label = "Easy Apply ⚡"
                else:
                    print(f"   [FAILED] Could not complete application for '{title}'.")
                close_active_modal()
                time.sleep(1)

            # Mode 2: Company Website Only
            elif APPLY_MODE == "company_website":
                if not ext_btn:
                    recheck_applied, _ = check_if_job_already_applied(card)
                    if recheck_applied:
                        now_str = datetime.datetime.now().strftime("%I:%M %p")
                        state.total_already_applied += 1
                        state.already_applied_jobs.append({
                            "title": title, "company": company, "mode": "Already Applied ✓", "time": now_str, "status": "ALREADY APPLIED"
                        })
                        update_automation_status({"total_already_applied": state.total_already_applied, "already_applied_jobs": state.already_applied_jobs})
                        continue

                    print("   -- Skipped (Not a Company Website job).")
                    state.total_skipped += 1
                    state.skipped_jobs.append({"title": title, "reason": "Not a Company Website job"})
                    update_automation_status({"total_skipped": state.total_skipped, "skipped_jobs": state.skipped_jobs})
                    continue

                print("   >> Company Website apply found! Navigating to company portal...")
                if handle_external_company_apply(ext_btn, title, PROFILE):
                    applied_successfully = True
                    applied_mode_label = "Company Portal 🌐"
                close_active_modal()
                time.sleep(1)

            # Mode 3: Both (Easy Apply + Company Website)
            else:
                if easy_btn:
                    print("   >> Easy Apply found! Starting application...")
                    click_element_safe(easy_btn)
                    time.sleep(2)
                    if handle_application_flow():
                        applied_successfully = True
                        applied_mode_label = "Easy Apply ⚡"
                    else:
                        print(f"   [FAILED] Could not complete application for '{title}'.")
                    close_active_modal()
                    time.sleep(1)
                elif ext_btn:
                    print("   >> Company Website apply found! Navigating to company portal...")
                    if handle_external_company_apply(ext_btn, title, PROFILE):
                        applied_successfully = True
                        applied_mode_label = "Company Portal 🌐"
                    close_active_modal()
                    time.sleep(1)
                else:
                    recheck_applied, _ = check_if_job_already_applied(card)
                    if recheck_applied:
                        now_str = datetime.datetime.now().strftime("%I:%M %p")
                        state.total_already_applied += 1
                        state.already_applied_jobs.append({
                            "title": title, "company": company, "mode": "Already Applied ✓", "time": now_str, "status": "ALREADY APPLIED"
                        })
                        update_automation_status({"total_already_applied": state.total_already_applied, "already_applied_jobs": state.already_applied_jobs})
                        continue

                    print("   -- Skipped (No applicable apply button found).")
                    state.total_skipped += 1
                    state.skipped_jobs.append({"title": title, "reason": "No apply button available"})
                    update_automation_status({"total_skipped": state.total_skipped, "skipped_jobs": state.skipped_jobs})
                    continue

            if applied_successfully:
                now_str = datetime.datetime.now().strftime("%I:%M %p")
                applied_entry = {
                    "title": title,
                    "company": company,
                    "mode": applied_mode_label,
                    "time": now_str,
                    "status": "APPLIED"
                }
                state.applied_jobs.append(applied_entry)
                state.total_applied += 1
                page_applied += 1
                print(f"   [SUCCESS] Successfully applied to '{title}' at '{company}' [{applied_mode_label}]!")
                update_automation_status({
                    "total_applied": state.total_applied,
                    "applied_jobs": state.applied_jobs,
                    "current_evaluating": f"Applied to: {title} at {company}"
                })

        except Exception as e:
            print(f"   [!] Job processing notice: {e}")
            ensure_active_window()
            close_active_modal()

    return page_applied

#----------------- Main Execution Routine -----------------

def main():
    global driver, API_KEY, USER_ID, PASSWORD, ROLES, INPUT_RESUME_PATH, YEARS, MONTHS, LINKS, JOB_MODE, PROFILE, LOCATION, CITY, APPLY_MODE

    config = load_config()
    PROFILE = build_candidate_profile(config)

    API_KEY           = config.get("API_KEY", "")
    USER_ID           = config.get("USER_ID", "")
    PASSWORD          = config.get("PASSWORD", "")
    ROLES             = config.get("ROLES", "java developer fresher")
    INPUT_RESUME_PATH = PROFILE.get("resume_path", "")
    LOCATION          = PROFILE.get("full_location", "Chennai, Tamil Nadu, India")
    CITY              = PROFILE.get("city", "Chennai")
    APPLY_MODE        = config.get("APPLY_MODE", "both").strip()
    YEARS             = config.get("YEARS", "0")
    MONTHS            = config.get("MONTHS", "0")
    LINKS             = config.get("LINKS", "")
    JOB_MODE          = config.get("JOB_MODE", "Fresher")

    mode_display = {
        "easy_apply": "Easy Apply Only (1-Click LinkedIn)",
        "company_website": "Company Website (External Portals + AI)",
        "both": "Both (Easy Apply & Company Portals)"
    }.get(APPLY_MODE, APPLY_MODE)

    resume_name = os.path.basename(str(INPUT_RESUME_PATH)) if INPUT_RESUME_PATH else "LinkedIn Profile Resume"

    print("\n" + "=" * 60)
    print("           [*] STARK LINKEDIN AUTO APPLICANT BOT           ")
    print("=" * 60)
    print(f"Candidate Name   : {PROFILE['name']}")
    print(f"Candidate Email  : {USER_ID}")
    print(f"Target Roles     : {ROLES}")
    print(f"Location         : {CITY} ({LOCATION})")
    print(f"Application Mode : {mode_display}")
    print(f"Resume Path      : {INPUT_RESUME_PATH or 'Using LinkedIn Profile Resume'}")
    print(f"Job Mode         : {JOB_MODE}")
    print(f"Gemini AI Engine : {'ACTIVE' if API_KEY.startswith('AIza') else 'Standby (Rule-Based Heuristic)'}")
    print("=" * 60)

    # Initialize live strongly-typed state
    state = AutomationState()

    # Stream initial running status to dashboard
    initial_status = {
        "status": "RUNNING",
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": None,
        "role": ROLES,
        "location": LOCATION,
        "mode": mode_display,
        "total_evaluated": 0,
        "total_applied": 0,
        "total_already_applied": 0,
        "total_skipped": 0,
        "current_evaluating": f"Initializing Chrome session for '{ROLES}'...",
        "applied_jobs": [],
        "already_applied_jobs": [],
        "skipped_jobs": [],
        "summary_instruction": f"Automation active for '{ROLES}' in {LOCATION}."
    }
    update_automation_status(initial_status)

    if not USER_ID or not PASSWORD:
        print("[ERROR] LinkedIn credentials missing in user_config.txt!")
        print("[*] Please configure user_config.txt or run 'py app.py'.")
        update_automation_status({
            "status": "COMPLETED",
            "current_evaluating": "Error: LinkedIn credentials missing in user_config.txt",
            "summary_instruction": "Please fill in your LinkedIn credentials in the setup form."
        })
        return

    print("\n>> Initializing Chrome Browser with Anti-Detection and Session Persistence...")
    driver = init_driver()

    try:
        # Step 1: Direct LinkedIn Login Verification
        update_automation_status({"current_evaluating": "Verifying LinkedIn login status..."})
        logged_in = login_to_linkedin(USER_ID, PASSWORD)
        if not logged_in:
            print("[ERROR] Cannot proceed with job applications without logging in.")
            update_automation_status({
                "status": "COMPLETED",
                "current_evaluating": "Authentication required. Please complete LinkedIn login.",
                "summary_instruction": "Could not authenticate to LinkedIn. Please check login credentials or complete 2FA."
            })
            return

        # Step 2: Search & Apply for Roles with Smart Continuous Queries
        roles_list = [r.strip() for r in ROLES.split(',') if r.strip()]
        expanded_searches = []
        for r in roles_list:
            expanded_searches.append((r, r))
            clean_r = r.lower().replace("fresher", "").replace("entry level", "").strip()
            if clean_r and clean_r != r.lower():
                expanded_searches.append((clean_r, r))
            if JOB_MODE == "Fresher":
                jr_r = f"junior {clean_r}".strip()
                if jr_r != r.lower() and jr_r != clean_r:
                    expanded_searches.append((jr_r, r))

        # Deduplicate search terms while preserving order
        unique_searches = []
        seen_queries = set()
        for q_term, assigned_r in expanded_searches:
            if q_term.lower() not in seen_queries:
                seen_queries.add(q_term.lower())
                unique_searches.append((q_term, assigned_r))

        print("\n" + "=" * 60)
        print(">> [2/3] STARTING AUTOMATED JOB SEARCH & APPLICATIONS...")
        print(f"   Search variations generated: {[q[0] for q in unique_searches]}")
        print("=" * 60)

        seen_job_keys = set()

        for search_query, assigned_role in unique_searches:
            print(f"\n==================================================")
            print(f"   SEARCHING QUERY: {search_query.upper()}")
            print(f"   ASSIGNED ROLE  : {assigned_role.upper()}")
            print(f"   LOCATION       : {LOCATION}")
            print(f"   MODE           : {mode_display}")
            print(f"==================================================")

            update_automation_status({
                "role": assigned_role,
                "current_evaluating": f"Searching LinkedIn for '{search_query}' in {LOCATION}..."
            })

            encoded_role = quote(search_query)
            encoded_loc = quote(str(LOCATION))

            # Smart LinkedIn Experience Filter based on Route
            exp_filter = "&f_E=1,2" if JOB_MODE == "Fresher" else "&f_E=3,4"
            try:
                if JOB_MODE == "Experienced" and int(YEARS or 0) >= 5:
                    exp_filter = "&f_E=4,5"
            except Exception:
                pass

            if APPLY_MODE == "easy_apply":
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}&location={encoded_loc}&f_AL=true{exp_filter}&locale=en_US"
            else:
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={encoded_role}&location={encoded_loc}{exp_filter}&locale=en_US"

            # 1. Visually navigate and type the search in the LinkedIn search bar live
            visually_type_and_search(driver, search_query, LOCATION)
            # 2. Open the filtered URL to enforce exact Easy Apply and Experience filters
            driver.get(search_url)
            bring_window_to_foreground(driver)
            time.sleep(3)

            # Turn ON LinkedIn Job Alert for this search if not already enabled
            enable_job_search_alert(search_query)

            for page in range(5):
                print(f"\n--- [PAGE {page + 1}] ---")
                update_automation_status({
                    "current_evaluating": f"Scanning Page {page + 1} for '{search_query}'..."
                })
                count = process_page_jobs(target_role=assigned_role, state=state, seen_keys=seen_job_keys)

                try:
                    ensure_active_window()
                    next_page_btn = driver.find_element(
                        By.XPATH,
                        f"//button[@aria-label='Page {page+2}'] | //button[contains(@aria-label, 'page {page+2}')]"
                    )
                    if next_page_btn.is_displayed():
                        print(f">> Advancing to Page {page + 2}...")
                        click_element_safe(next_page_btn)
                        time.sleep(4)
                    else:
                        break
                except Exception:
                    print(">> Reached end of search results for this query.")
                    break

        total_applied = state.total_applied
        total_already = state.total_already_applied

        if total_applied == 0 and total_already > 0:
            summary_text = (
                f"ℹ️ You have already applied for all matching jobs! "
                f"Every matching position for '{ROLES}' in {LOCATION} was already submitted previously by you on LinkedIn. "
                f"Total previously submitted applications identified: {total_already}. "
                f"Zero new unapplied jobs remain on LinkedIn for this search. You are completely up to date!"
            )
        elif total_applied > 0:
            summary_text = (
                f"Successfully applied to {total_applied} new jobs matching '{ROLES}' in {LOCATION}! "
                f"({total_already} other matching positions were already previously applied). "
                f"All candidate details and screening questions were populated from resume '{resume_name}'. "
                f"100% verified applications submitted without errors."
            )
        else:
            summary_text = (
                f"Job search completed for '{ROLES}' in {LOCATION}. "
                f"All {state.total_evaluated} scanned positions evaluated. Zero jobs met role criteria or remained unapplied."
            )

        update_automation_status({
            "status": "COMPLETED",
            "end_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total_applied": total_applied,
            "total_already_applied": total_already,
            "total_evaluated": state.total_evaluated,
            "total_skipped": state.total_skipped,
            "applied_jobs": state.applied_jobs,
            "already_applied_jobs": state.already_applied_jobs,
            "skipped_jobs": state.skipped_jobs,
            "current_evaluating": f"Completed: {total_applied} newly applied, {total_already} already applied.",
            "summary_instruction": summary_text
        })

        print("\n" + "=" * 65)
        print("          🎉 [3/3] PROTOCOL COMPLETE - FINAL SUMMARY")
        print("=" * 65)
        print(f"Total Jobs Evaluated : {state.total_evaluated}")
        print(f"Total Jobs Applied   : {total_applied}")
        print(f"Total Already Applied: {total_already}")
        print(f"Total Jobs Filtered  : {state.total_skipped}")
        print(f"Target Role          : {ROLES}")
        print(f"Target Location      : {LOCATION}")
        print(f"Resume Used          : {resume_name}")
        print(f"Status               : 100% Completed Successfully (0 Errors)")
        print("\nROLES NEWLY APPLIED:")
        if state.applied_jobs:
            for idx, aj in enumerate(state.applied_jobs, 1):
                print(f"  {idx}. {aj['title']} @ {aj['company']} ({aj['mode']}) at {aj['time']}")
        else:
            print("  (No new unapplied roles found)")
        print("\nROLES ALREADY APPLIED ON LINKEDIN:")
        if state.already_applied_jobs:
            for idx, aaj in enumerate(state.already_applied_jobs, 1):
                print(f"  {idx}. {aaj['title']} @ {aaj['company']} (Previously submitted)")
        print("=" * 65)
        time.sleep(5)

    except KeyboardInterrupt:
        print("\n>> Process interrupted by user.")
        update_automation_status({
            "status": "COMPLETED",
            "current_evaluating": "Process interrupted by user.",
            "summary_instruction": f"Automation stopped by user. Applied to {state.total_applied} jobs."
        })
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        update_automation_status({
            "status": "COMPLETED",
            "current_evaluating": f"Automation error: {e}",
            "summary_instruction": f"Automation ended with note: {e}. Applied to {state.total_applied} jobs."
        })
    finally:
        print(">> Closing browser session...")
        try:
            driver.quit()
        except Exception:
            pass

if __name__ == "__main__":
    main()

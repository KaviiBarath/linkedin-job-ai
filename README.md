# linkedin-job-ai

### STARK-on-AI LinkedIn Job Automation Bot

An automated LinkedIn job application platform featuring a real-time web interface, live status monitoring dashboard, intelligent candidate profile parser, resume screening question solver, and support for both 1-Click **Easy Apply** and **Company Website** career portals.

---

### Key Features
- **Modern Web Dashboard**: Real-time status reporting, live application counter, and evaluation logs.
- **Continuous Job Search & Application**: Scans LinkedIn search pages, scrolls virtualized job cards, and processes open positions continuously.
- **Smart Already-Applied Detection**: Automatically detects jobs already submitted on LinkedIn and displays status banners in clear English.
- **Dual Application Modes**:
  - `Easy Apply`: Automated 1-click LinkedIn multi-step application wizards.
  - `Company Website`: Automates external career portals and ATS forms (Greenhouse, Lever, Workday, etc.).
  - `Both`: Seamlessly handles both native and external job listings.
- **AI-Powered Screening Question Solver**: Analyzes candidate resume and auto-answers complex job application screening questions.
- **Strict Role & Experience Filtering**: Matches jobs precisely to target tech stacks while filtering out irrelevant roles and senior positions.

---

### Prerequisites
- Python 3.10+
- Google Chrome installed

---

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/KaviiBarath/linkedin-job-ai.git
   cd linkedin-job-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Settings:**
   Copy `user_config.example.txt` to `user_config.txt` and fill in your details:
   ```bash
   cp user_config.example.txt user_config.txt
   ```
   Or simply launch the web setup interface.

4. **Launch Web Application:**
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:5001` to configure your roles, location, and start the automation bot!

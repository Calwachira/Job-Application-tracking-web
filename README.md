# 🎯 1000 Days Job Application Tracker

A simple web app to track your job applications over a 1000-day job-search challenge. Built with **Streamlit** and **SQLite**, no external services or accounts needed. Your data stays on your machine.

## Features

- **Dashboard**: totals, status counts, success rate (interviews + offers ÷ total), and a 1000-day progress bar
- **Applications**: add, edit, delete (with confirmation), and filter by status
- **Search**: find applications by company or position
- **Status tracking**: `applied`, `interview`, `offer`, `rejected`
- **Local storage**: everything is saved in a SQLite file (`job_applications.db`), created automatically on first run

## Project Structure

```
job-tracker/
├── job_tracker_web.py     # Main Streamlit app
├── requirements.txt       # Python dependencies
├── .streamlit/
│   └── config.toml        # Streamlit theme/settings
├── data/                  # (optional) place for your local database
├── .gitignore             # Keeps your database and IDE files out of Git
├── LICENSE
└── README.md
```

## Getting Started

### Prerequisites

- Python 3.9 or newer

### Installation

```bash
git clone https://github.com/<your-username>/job-tracker.git
cd job-tracker

# (recommended) create a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### Run

```bash
streamlit run job_tracker_web.py
```

The app opens at <http://localhost:8501>. On first launch it creates `job_applications.db` and records today as **Day 0** of your 1000-day challenge.

## Usage

1. Open **Applications** → **Add application** and fill in company, position, status, and optional notes.
2. Use ✏️ to edit or 🗑️ to delete an entry.
3. Check the **Dashboard** to see your progress and success rate.
4. Use **Search** to look up a specific company or role.

## Data & Privacy

Your database is listed in `.gitignore`, so your personal application history will **not** be pushed to GitHub. To back up or move your data, copy `job_applications.db` yourself.

## Configuration

Edit the constants at the top of `job_tracker_web.py`:

| Setting | Default | Description |
|---|---|---|
| `DB_FILE` | `job_applications.db` | SQLite database path |
| `TARGET_DAYS` | `1000` | Length of the challenge |
| `VALID_STATUSES` | applied, interview, offer, rejected | Allowed statuses |

## Roadmap Ideas

- Export to CSV
- Charts over time
- Follow-up reminders
- Edit the start date from the UI

## License

MIT, see [LICENSE](LICENSE).

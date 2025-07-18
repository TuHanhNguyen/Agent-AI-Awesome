# Agent AI Awesome

This repository provides a small Flask application that demonstrates an AI-driven spare parts quoting workflow. The app analyses a customer's photo, checks a SQLite inventory and emails a price estimate.

## Database Setup

Create and seed the database using the helper functions in `CSDL.py`:

```bash
python - <<'PY'
import CSDL
CSDL.setup_database()
CSDL.insert_sample_data()
PY
```

This will produce `inventory.db` in the project directory.

## Running the Application

Install the required packages and start the Flask server:

```bash
pip install flask ag2
python ChuongTrinhChinh.py
```

Access the application at `http://localhost:5000`.

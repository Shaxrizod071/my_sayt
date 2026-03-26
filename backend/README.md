# Backend for Student Management System

This project implements the server-side logic for managing students, calculating GPA, determining grant/contract status, ratings, and notifications. It also includes an admin panel.

## Features

- Add students to database
- GPA calculation algorithm
- Grant/contract determination
- Ranking calculation
- Notification logic (stubbed)
- Admin endpoints

Built with FastAPI and SQLAlchemy.

## Getting Started 

1. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/Scripts/activate  # Windows
   pip install -r requirements.txt
   ```
2. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
3. Open http://127.0.0.1:8000/docs for the interactive API docs.

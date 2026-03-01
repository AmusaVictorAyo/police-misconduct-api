# Police Misconduct Complaint Tracking API

## Setup
## ✅ Reviewer Run & Test Guide

### Run the server

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
POST /api/complaints/{id}/route/

Examples for filters/search/ordering



Police Misconduct Complaint Tracking API
📌 Project Overview

A backend REST API built with Django and Django REST Framework that allows citizens to submit and track police misconduct complaints. Oversight authorities can review, update status, and route complaints.

🚀 Features (MVP)

User authentication (Token-based)

Complaint CRUD (Create, Read, Update, Delete)

Role-based access (Citizen / Oversight / Admin)

Status workflow (SUBMITTED → RECEIVED → PENDING → CLOSED)

Evidence attachment (metadata links)

Complaint routing to oversight authorities

Filtering, searching, ordering

Swagger API documentation

🛠 Tech Stack

Python 3

Django

Django REST Framework

django-filter

DRF Token Authentication

⚙️ Setup Instructions
git clone <your-repo-url>
cd police_misconduct_api

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env  # if applicable

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

Server runs at:

http://127.0.0.1:8000/
🔐 Authentication

Get a token:

POST /api/auth/login/

Example:

curl -X POST http://127.0.0.1:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{"username":"user","password":"password"}'

Use token:

-H "Authorization: Token YOUR_TOKEN"
📌 Core Endpoints
Create Complaint
POST /api/complaints/
Update Status (Oversight Only)
POST /api/complaints/{id}/status/
Route Complaint
POST /api/complaints/{id}/route/
Add Evidence
POST /api/complaints/{id}/evidence/
🔎 Filtering, Searching & Ordering

Examples:

Filter by status:

GET /api/complaints/?status=PENDING

Search:

GET /api/complaints/?search=Lagos

Order:

GET /api/complaints/?ordering=created_at
📄 API Documentation

Swagger UI:

http://127.0.0.1:8000/api/docs/

OpenAPI schema:

http://127.0.0.1:8000/api/schema/

🧪 Running Tests
python manage.py test
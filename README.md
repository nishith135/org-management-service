🚀 Multi-Tenant Organization Management API

A backend service built with FastAPI for managing organizations in a multi-tenant architecture.
Each organization gets an isolated MongoDB collection, along with secure admin authentication using JWT.

This project was built as part of a backend engineering assignment and follows clean, modular, and scalable design principles.

🌟 Features
🔐 Admin Authentication

Secure admin login using JWT

Password hashing with bcrypt

OAuth2 Bearer Token support (Swagger-compatible)

🏢 Organization Management

Create, read, update, and delete organizations

Per-organization dynamic MongoDB collections

Master database stores metadata + admin reference

🧱 Architecture

Multi-tenant isolation

Modular folder structure (services, models, routes, DB, auth)

Standardized API response envelope with trace IDs

📘 Documentation

Auto-generated Swagger UI

Typed models using Pydantic

🛠 Tech Stack
Component	Technology
Framework	FastAPI
Language	Python 3.10+
Database	MongoDB
Driver	Motor (async)
Auth	JWT (OAuth2)
Hashing	bcrypt
📦 Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/nishith135/org-management-service.git
cd org-management-service

2️⃣ Create Virtual Environment
Windows:
python -m venv venv
.\venv\Scripts\Activate.ps1

macOS / Linux:
python3 -m venv venv
source venv/bin/activate

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Configure Environment Variables

Copy the example file:

cp .env.example .env


Edit .env:

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=org_master_db
JWT_SECRET_KEY=change-this-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

5️⃣ Start MongoDB

Using local installation (MongoDB Compass / mongod) is enough.

Make sure MongoDB is running at:

mongodb://localhost:27017

6️⃣ Start FastAPI Server
uvicorn app.main:app --reload


Visit Swagger UI:

👉 http://localhost:8000/docs

📚 API Endpoints
🔐 Admin Authentication
POST /admin/login

Request:

{
  "email": "admin@example.com",
  "password": "StrongPass123!"
}


Response:

{
  "success": true,
  "data": {
    "access_token": "...",
    "token_type": "bearer"
  },
  "error": {},
  "trace_id": "uuid-string"
}

🏢 Organization Management
POST /org/create

Creates a new organization + dynamic collection + admin user.

Request:

{
  "organization_name": "Acme Corp",
  "admin_email": "admin@acme.com",
  "admin_password": "StrongPass123!"
}

GET /org/get

Retrieve organization metadata.

Example:

GET /org/get?organization_name=Acme%20Corp

PUT /org/update

Update organization name (and migrate collection).

Request:

{
  "current_organization_name": "Acme Corp",
  "new_organization_name": "Acme Global",
  "admin_email": "admin@acme.com",
  "admin_password": "StrongPass123!"
}

DELETE /org/delete

Requires JWT authentication.

Headers:

Authorization: Bearer <token>


Example:

DELETE /org/delete?organization_name=Acme%20Global

🎯 Response Format (Standard Across API)
{
  "success": true,
  "data": {},
  "error": {},
  "trace_id": "uuid"
}


Error example:

{
  "success": false,
  "data": null,
  "error": {
    "code": "ORG_NOT_FOUND",
    "message": "Organization not found",
    "details": null
  },
  "trace_id": "uuid"
}

🏗 Project Structure (Important for review)
app/
├── api/
│   └── v1/
│       ├── admin_routes.py
│       └── org_routes.py
├── auth/
│   └── dependencies.py
├── db/
│   └── client.py
├── models/
│   ├── admin.py
│   ├── org.py
│   ├── response.py
│   └── organization.py
├── services/
│   ├── auth_service.py
│   └── org_service.py
├── utils/
│   ├── jwt.py
│   └── responses.py
└── main.py

🧱 High-Level Architecture (for the assignment)

A detailed diagram is included in:

📄 ARCHITECTURE.md

Covers:

Master DB design

Per-tenant collections

Auth flow

Request → Service → Database flow

💡 Design Notes (Brief Summary)

Chose FastAPI for speed, typing, and clean architecture

Used Motor for non-blocking MongoDB I/O

Multi-tenant isolation achieved through dynamic collections

Standardized responses improve debugging with trace_id

JWT authentication ensures admin-only access to protected routes

Follows modular service-based architecture for scalability

A deeper explanation is inside:

📄 DESIGN.md

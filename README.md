# Multi-Tenant Organization Management API

A FastAPI backend for managing multi-tenant organizations with JWT authentication. This API provides organization CRUD operations with secure admin authentication and multi-tenant data isolation.

## Features

- **Admin Authentication**: JWT-based authentication with secure password hashing
- **Organization Management**: Full CRUD operations for organizations
- **Multi-Tenant Architecture**: Isolated data collections per organization
- **MongoDB Integration**: Async Motor driver for high-performance database operations
- **Standardized API Responses**: Consistent response format with trace IDs
- **OpenAPI Documentation**: Auto-generated Swagger UI and ReDoc documentation
- **OAuth2 Security**: Bearer token authentication with Swagger integration

## Tech Stack

- **FastAPI** 0.104.1 - Modern, fast web framework
- **Python** 3.10+ - Programming language
- **MongoDB** - NoSQL database
- **Motor** - Async MongoDB driver
- **Pydantic** - Data validation
- **JWT** - Token-based authentication
- **Bcrypt** - Password hashing

## Prerequisites

- Python 3.10 or higher
- MongoDB (local or remote instance)
- pip (Python package manager)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd "og multitenant api"
```

### 2. Create Virtual Environment

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file and update with your values:

```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` file with your configuration:

```env
MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=org_master_db
JWT_SECRET_KEY=your-super-secret-key-change-this
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 5. Start MongoDB

**Using Docker:**

```bash
docker run -d --name mongo-local -p 27017:27017 mongo:latest
```

**Or use a local MongoDB installation:**

```bash
# Ensure MongoDB service is running
mongod
```

### 6. Run the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once the server is running, access the interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Using Swagger UI

1. Open http://localhost:8000/docs
2. Click the **Authorize** 🔒 button to authenticate
3. Enter your JWT token (obtained from `/admin/login`)
4. All protected endpoints will automatically include the Bearer token

## API Endpoints

### Admin Authentication

#### `POST /admin/login`

Authenticate admin and receive JWT token.

**Request Body:**

```json
{
  "email": "admin@example.com",
  "password": "your-password"
}
```

**Response:**

```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  },
  "error": {},
  "trace_id": "uuid"
}
```

### Organization Management

#### `POST /org/create`

Create a new organization with an admin account.

**Request Body:**

```json
{
  "organization_name": "Acme Corp",
  "admin_email": "admin@acme.com",
  "admin_password": "StrongPass123!"
}
```

#### `GET /org/get`

Get organization by name (public endpoint, no authentication required).

**Query Parameters:**

- `organization_name` (required): Name of the organization

**Example:**

```
GET /org/get?organization_name=Acme%20Corp
```

#### `PUT /org/update`

Update an existing organization.

**Request Body:**

```json
{
  "current_organization_name": "Acme Corp",
  "new_organization_name": "Acme Global",
  "admin_email": "admin@acme.com",
  "admin_password": "StrongPass123!"
}
```

#### `DELETE /org/delete`

Delete an organization (requires authentication).

**Query Parameters:**

- `organization_name` (required): Name of the organization to delete

**Headers:**

- `Authorization: Bearer <JWT_TOKEN>`

**Example:**

```
DELETE /org/delete?organization_name=Acme%20Global
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## Response Format

All endpoints return a standardized response format:

```json
{
  "success": true,
  "data": {
    // Response data here
  },
  "error": {},
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Error Response:**

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error message",
    "details": {}
  },
  "trace_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

## Testing

### Using cURL

**Create Organization:**

```bash
curl -X POST "http://localhost:8000/org/create" \
  -H "Content-Type: application/json" \
  -d '{
    "organization_name": "Acme Corp",
    "admin_email": "admin@acme.com",
    "admin_password": "StrongPass123!"
  }'
```

**Admin Login:**

```bash
curl -X POST "http://localhost:8000/admin/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@acme.com",
    "password": "StrongPass123!"
  }'
```

**Get Organization:**

```bash
curl "http://localhost:8000/org/get?organization_name=Acme%20Corp"
```

**Delete Organization (with token):**

```bash
curl -X DELETE "http://localhost:8000/org/delete?organization_name=Acme%20Corp" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

### Using PowerShell

**Create Organization:**

```powershell
$body = @{
    organization_name = "Acme Corp"
    admin_email = "admin@acme.com"
    admin_password = "StrongPass123!"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:8000/org/create" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

**Admin Login:**

```powershell
$body = @{
    email = "admin@acme.com"
    password = "StrongPass123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/admin/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body

$token = $response.data.access_token
Write-Host "Token: $token"
```

**Delete Organization:**

```powershell
$headers = @{
    Authorization = "Bearer $token"
}

Invoke-RestMethod -Uri "http://localhost:8000/org/delete?organization_name=Acme%20Corp" `
    -Method DELETE `
    -Headers $headers
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_smoke.py
```

**Note:** Tests require MongoDB to be running. Tests use a separate test database (`org_master_db_test`) to avoid clobbering production data.

## Docker Deployment

### Using Docker Compose

```bash
docker-compose up -d
```

This will start both MongoDB and the FastAPI application.

### Manual Docker Setup

**Build the image:**

```bash
docker build -t org-api .
```

**Run the container:**

```bash
docker run -d \
  --name org-api \
  -p 8000:8000 \
  --env-file .env \
  --link mongo-local:mongo \
  org-api
```

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── api/
│   │   └── v1/
│   │       ├── admin_routes.py # Admin authentication routes
│   │       └── org_routes.py   # Organization CRUD routes
│   ├── auth/
│   │   └── dependencies.py    # OAuth2 authentication dependencies
│   ├── db/
│   │   └── client.py          # MongoDB connection management
│   ├── models/
│   │   ├── admin.py           # Admin Pydantic models
│   │   ├── org.py             # Organization request models
│   │   ├── organization.py    # Organization domain models
│   │   └── response.py        # API response models
│   ├── services/
│   │   ├── auth_service.py    # Authentication business logic
│   │   └── org_service.py     # Organization business logic
│   └── utils/
│       ├── jwt.py             # JWT token utilities
│       └── responses.py       # Standardized response helpers
├── tests/
│   └── test_smoke.py          # Smoke tests
├── .env.example               # Environment variables template
├── .gitignore                  # Git ignore rules
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker image definition
├── docker-compose.yml          # Docker Compose configuration
├── README.md                   # This file
├── ARCHITECTURE.md             # Architecture documentation
└── DESIGN.md                   # Design decisions

```

## Development

### Code Style

This project uses:

- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting

**Format code:**

```bash
black app/ tests/
isort app/ tests/
```

**Lint code:**

```bash
flake8 app/ tests/
```

## Security Considerations

- **JWT Secret Key**: Always use a strong, randomly generated secret key in production
- **Password Hashing**: Passwords are hashed using bcrypt
- **Environment Variables**: Never commit `.env` file to version control
- **CORS**: Currently allows all origins (`*`). Restrict in production
- **Token Expiration**: Configure `ACCESS_TOKEN_EXPIRE_MINUTES` appropriately

## License

MIT License - see LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## Support

For issues and questions, please open an issue on the GitHub repository.


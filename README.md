# CareDesk Healthcare API

CareDesk is a healthcare records backend and browser dashboard built with Django, Django REST Framework, JWT authentication, and PostgreSQL hosted by Supabase.

The system supports:

- Email/password user registration and JWT login
- Patient records owned by the authenticated user
- Doctor directory management
- Patient-doctor assignments with duplicate protection
- A responsive dashboard at `/`
- Local development with SQLite fallback
- Production database configuration through Supabase PostgreSQL

## Technology

- Python 3.13+
- Django 5.2
- Django REST Framework
- `djangorestframework-simplejwt` for access and refresh tokens
- PostgreSQL through `psycopg`
- Supabase PostgreSQL for hosted data
- `dj-database-url` for database URL parsing
- WhiteNoise for static files
- Vanilla HTML, CSS, and JavaScript dashboard served by Django

## Project Structure

```text
.
├── accounts/                Custom email-based user model and registration API
├── healthcare/              Patient, doctor, mapping models and API endpoints
├── dashboard/               Browser dashboard template and static assets
├── config/                  Django settings, URL routing, WSGI, and ASGI
├── manage.py                Django command-line entry point
├── requirements.txt         Python dependencies
├── .env.example             Environment variable template
└── README.md                Project documentation
```

### Application responsibilities

`accounts` provides the custom `User` model. Email is the login identifier and passwords are stored using Django's password hashing system.

`healthcare` provides:

- `Patient`, linked to the user who created it
- `Doctor`, linked to the user who created it
- `PatientDoctorMapping`, linking patients and doctors with a unique patient-doctor constraint

`dashboard` serves the frontend at `/`. The frontend calls the same-origin `/api/` endpoints and stores JWT tokens in browser local storage.

## Supabase Setup

1. Create a project at [supabase.com](https://supabase.com).
2. Open **Project Settings > Database > Connection string**.
3. Copy a PostgreSQL connection string. The transaction pooler connection is usually the best choice for serverless deployments.
4. Create a local `.env` file from `.env.example`.
5. Set `DATABASE_URL` to the Supabase connection string.

Example format:

```env
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres?sslmode=require
```

For a pooler connection, Supabase may provide a URL similar to:

```env
DATABASE_URL=postgresql://postgres.[project-ref]:[password]@[region].pooler.supabase.com:6543/postgres?sslmode=require
```

Do not commit `.env` or expose the database password in documentation. If a database password has been exposed, rotate it in Supabase before continuing.

## Local Installation

From PowerShell:

```powershell
git clone <repository-url>
cd whatbyte-assignment

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can use the virtual environment executable directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Create `.env`:

```powershell
Copy-Item .env.example .env
```

Then edit `.env` and set the values described below.

## Environment Variables

| Variable | Required | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes in production | Long random secret used by Django and JWT signing |
| `DJANGO_DEBUG` | No | `True` for local development, `False` in production |
| `DJANGO_ALLOWED_HOSTS` | Yes in production | Comma-separated hostnames accepted by Django |
| `DATABASE_URL` | Yes for Supabase | PostgreSQL connection URL from Supabase |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Required when deployed behind HTTPS | Comma-separated origins including `https://` |

Safe local example:

```env
DJANGO_SECRET_KEY=replace-with-a-long-random-secret
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://postgres:[password]@db.[project-ref].supabase.co:5432/postgres?sslmode=require
```

When `DATABASE_URL` is not set, the project falls back to `db.sqlite3` for local development. To use Supabase, `DATABASE_URL` must be present before running migrations.

## Database Migrations

Apply all migrations:

```powershell
python manage.py migrate
```

Create migrations after model changes:

```powershell
python manage.py makemigrations
python manage.py migrate
```

Check for model changes that have not been migrated:

```powershell
python manage.py makemigrations --check --dry-run
```

## Run the Application

Start the development server:

```powershell
python manage.py runserver
```

Open the dashboard at:

```text
http://127.0.0.1:8000/
```

The API base URL is:

```text
http://127.0.0.1:8000/api/
```

The dashboard provides login, registration, patient management, doctor management, assignment management, search, logout, and a developer-focused **Test API** tab. The Test API tab can send `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` requests, include the current JWT automatically, edit JSON request bodies, copy the access token, copy equivalent cURL commands, and inspect formatted responses with status and timing. All data operations use the REST API and require a valid JWT after login.

## Authentication API

### Register

```http
POST /api/auth/register/
Content-Type: application/json
```

```json
{
   "name": "Jane Smith",
   "email": "jane@example.com",
   "password": "strong-password-123"
}
```

Passwords must contain at least eight characters. A successful response returns HTTP `201 Created` with the new user's public fields.

### Login

```http
POST /api/auth/login/
Content-Type: application/json
```

```json
{
   "email": "jane@example.com",
   "password": "strong-password-123"
}
```

The response contains `access` and `refresh` tokens:

```json
{
   "refresh": "<refresh-token>",
   "access": "<access-token>"
}
```

Use the access token on protected requests:

```http
Authorization: Bearer <access-token>
```

### Refresh

```http
POST /api/auth/refresh/
Content-Type: application/json
```

```json
{
   "refresh": "<refresh-token>"
}
```

## Patient API

All patient endpoints require authentication. Patients are scoped to the user who created them.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/patients/` | Create a patient owned by the current user |
| `GET` | `/api/patients/` | List the current user's patients |
| `GET` | `/api/patients/<id>/` | Retrieve one owned patient |
| `PUT` | `/api/patients/<id>/` | Replace an owned patient |
| `PATCH` | `/api/patients/<id>/` | Partially update an owned patient |
| `DELETE` | `/api/patients/<id>/` | Delete an owned patient |

Create request:

```json
{
   "name": "Alex Johnson",
   "date_of_birth": "1990-04-12",
   "gender": "female",
   "contact": "555-0100",
   "address": "1 Main Street"
}
```

## Doctor API

All doctor endpoints require authentication. All authenticated users can view the doctor directory, but only the user who created a doctor can update or delete it.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/doctors/` | Create a doctor |
| `GET` | `/api/doctors/` | List all doctors |
| `GET` | `/api/doctors/<id>/` | Retrieve a doctor |
| `PUT` | `/api/doctors/<id>/` | Update a doctor created by the current user |
| `PATCH` | `/api/doctors/<id>/` | Partially update an owned doctor |
| `DELETE` | `/api/doctors/<id>/` | Delete a doctor created by the current user |

Create request:

```json
{
   "name": "Dr. Sam Lee",
   "specialization": "Cardiology",
   "contact": "555-0120"
}
```

## Patient-Doctor Mapping API

Mappings require authentication and are limited to patients owned by the current user.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/mappings/` | Assign a doctor to one of your patients |
| `GET` | `/api/mappings/` | List your patient-doctor assignments |
| `GET` | `/api/mappings/<patient_id>/` | Get assignments for a patient ID |
| `GET` | `/api/mappings/patient/<patient_id>/` | Get assignments for a patient ID |
| `DELETE` | `/api/mappings/<mapping_id>/` | Remove an assignment |

Create request:

```json
{
   "patient": 1,
   "doctor": 2
}
```

The same patient-doctor pair cannot be assigned twice. The API returns a validation error for duplicate assignments.

## Example PowerShell API Flow

Register and log in:

```powershell
$body = @{
      name = "Jane Smith"
      email = "jane@example.com"
      password = "strong-password-123"
} | ConvertTo-Json

Invoke-RestMethod http://127.0.0.1:8000/api/auth/register/ -Method Post -ContentType "application/json" -Body $body

$loginBody = @{
      email = "jane@example.com"
      password = "strong-password-123"
} | ConvertTo-Json

$tokens = Invoke-RestMethod http://127.0.0.1:8000/api/auth/login/ -Method Post -ContentType "application/json" -Body $loginBody
$headers = @{ Authorization = "Bearer $($tokens.access)" }
```

Create and list patients:

```powershell
$patientBody = @{
      name = "Alex Johnson"
      date_of_birth = "1990-04-12"
      gender = "female"
      contact = "555-0100"
      address = "1 Main Street"
} | ConvertTo-Json

Invoke-RestMethod http://127.0.0.1:8000/api/patients/ -Method Post -Headers $headers -ContentType "application/json" -Body $patientBody
Invoke-RestMethod http://127.0.0.1:8000/api/patients/ -Method Get -Headers $headers
```

## Testing and Checks

Run Django's system checks:

```powershell
python manage.py check
```

Run the test suite:

```powershell
python manage.py test
```

The included tests cover registration, JWT login, authenticated patient creation, and patient listing. The test database uses Django's configured database backend; do not point tests at a production database.

## Static Files

WhiteNoise serves the dashboard CSS and JavaScript through Django. For a deployment build, collect static files with:

```powershell
python manage.py collectstatic --noinput
```

The generated `staticfiles/` directory is ignored by Git.

## Deployment to Vercel

This project can run as a Vercel Python function when the repository includes the Vercel entrypoint and configuration files.

1. Push the project to GitHub and import it into Vercel.
2. Keep the project root at the repository root and use the `Other` framework preset.
3. Add these Production environment variables:

    ```text
    DJANGO_SECRET_KEY=<long-random-secret>
    DJANGO_DEBUG=False
    DATABASE_URL=<Supabase-connection-string>
   DJANGO_ALLOWED_HOSTS=whatbytess.vercel.app
   DJANGO_CSRF_TRUSTED_ORIGINS=https://whatbytess.vercel.app
    ```

4. Add custom domains to both host/origin variables when applicable. Vercel's `VERCEL_URL` is also accepted automatically as an allowed host.
5. Deploy the project.
   The Vercel catch-all route invokes `api/index.py` without changing the original path, so the dashboard remains at `/` and API requests remain under `/api/`. Do not change the rewrite destination to `/`, because that sends every request back to the dashboard root.
6. Run migrations against Supabase from a local terminal using the production URL:

    ```powershell
    $env:DATABASE_URL = "<Supabase-connection-string>"
    python manage.py migrate
    ```

Do not rely on local SQLite for production data. Vercel's filesystem is ephemeral, while Supabase provides the persistent PostgreSQL database.

## Troubleshooting

### `ModuleNotFoundError: No module named 'whitenoise'`

Install dependencies into the same virtual environment used to run Django:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### The dashboard returns `404 Not Found`

Make sure the server is running and open the root URL, not an API route:

```text
http://127.0.0.1:8000/
```

### The API returns `401 Unauthorized`

Log in first and send the access token exactly as:

```http
Authorization: Bearer <access-token>
```

### The deployment returns `Forbidden (CSRF cookie not set)`

The API uses JWT authentication, not Django session authentication. API paths are configured to skip Django's browser-session CSRF cookie check while the admin and non-API dashboard paths retain normal CSRF protection. Redeploy after pulling the latest `config/middleware.py`, `config/settings.py`, and `vercel.json` changes.

### The app uses SQLite instead of Supabase

Check that `.env` exists in the project root and contains a valid `DATABASE_URL`. Restart Django after changing environment variables, then run `python manage.py migrate`.

### Supabase connection fails

Check the password, project reference, region, port, and `sslmode=require`. Use the exact connection string shown in Supabase's Database settings. Never commit the connection string.

## Security Notes

- Keep `.env` out of version control.
- Use a unique long `DJANGO_SECRET_KEY` in production.
- Set `DJANGO_DEBUG=False` in production.
- Use HTTPS for deployed dashboard and API traffic.
- Rotate Supabase credentials if they are exposed.
- Apply migrations against the intended database before using the API.

# Backend (Django) for BioData Maker

This folder contains a minimal Django REST backend that stores biodata as JSON and optionally an uploaded profile image.

Quick start (PowerShell):

```powershell
# create venv and activate
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# install dependencies
pip install -r requirements.txt

# run migrations and start server
cd backend
python manage.py migrate
python manage.py createsuperuser  # optional, for admin
python manage.py runserver
```

API endpoints:

- GET/POST /api/biodata/ -> list and create
- GET/PUT/PATCH/DELETE /api/biodata/{id}/ -> detail

Notes:

- `MEDIA_ROOT` is `backend/media/`. Uploaded images will be served by Django when DEBUG=True.
- Update `SECRET_KEY` in `biodata_project/settings.py` before deploying to production.

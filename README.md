# Pet Adoption & Rescue Platform

Django (templates) + Django REST Framework + PostgreSQL.

## Features
- Register / login / logout / profile
- Pet list with search, filters (name, type, breed, gender, location, status) and pagination
- Pet details page (adopt button hidden when adopted)
- Adoption form and "My Adoption Requests" dashboard
- Django Admin: manage pets (with image upload) and approve/reject requests
- REST API with search, filtering, pagination and token authentication

## Business rules
1. Only **Available** pets can receive applications (model `clean()` + view check).
2. A user cannot have more than one active (Pending/Approved) request for the same pet
   (model `clean()` + PostgreSQL partial unique constraint).
3. Approving a request sets the pet to **Adopted** and automatically rejects the other pending
   requests for that pet; no new applications are accepted afterwards.

## Setup
1. Requires Python 3.10+ and PostgreSQL 13+.
2. Create the database (in `psql`):
   ```sql
   CREATE DATABASE pet_adoption;
   CREATE USER pet_user WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE pet_adoption TO pet_user;
   ALTER DATABASE pet_adoption OWNER TO pet_user;
   ```
3. Install and configure:
   ```bash
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cp .env.example .env            # then edit DB credentials
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```
4. Open http://127.0.0.1:8000/ (site) and http://127.0.0.1:8000/admin/ (admin). Add some pets in the admin first.

## Web pages
| URL | Page |
|---|---|
| `/` | Home |
| `/pets/` | Pet list + search/filter |
| `/pets/<id>/` | Pet details |
| `/pets/<id>/adopt/` | Adoption form (login required) |
| `/my-requests/` | My adoption requests |
| `/profile/` | Profile |
| `/register/`, `/login/` | Auth |

## REST API
| Method | URL | Notes |
|---|---|---|
| GET | `/api/pets/` | Public, paginated (`?page=2`) |
| GET | `/api/pets/<id>/` | Public |
| POST / PUT / DELETE | `/api/pets/`, `/api/pets/<id>/` | Staff only |
| GET / POST | `/api/adoptions/` | Logged-in users, own requests only |
| GET / PUT | `/api/adoptions/<id>/` | Own pending requests only (status is admin-controlled) |
| POST | `/api/token/` | Get auth token (`username`, `password`) |

Search/filter examples:
```
/api/pets/?search=golden
/api/pets/?animal_type=Dog&gender=Male
/api/pets/?location=Dhaka&status=Available
```

Token authentication example:
```bash
curl -X POST http://127.0.0.1:8000/api/token/ -d "username=rahim&password=secret"
curl -X POST http://127.0.0.1:8000/api/adoptions/ \
  -H "Authorization: Token <token>" -H "Content-Type: application/json" \
  -d '{"pet": 1, "phone": "01700000000", "address": "Dhaka", "reason": "Love dogs", "previous_pet_experience": true}'
```
Creating a pet with an image (staff token): `curl -H "Authorization: Token <staff-token>" -F name=Max -F animal_type=Dog -F age=2 -F gender=Male -F location=Dhaka -F image=@max.jpg http://127.0.0.1:8000/api/pets/`

## Project structure
```
config/   settings, urls
pets/     models, admin, forms, views, urls, serializers, filters, api_views, api_urls, migrations
templates/  base + all pages
```

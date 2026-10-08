# Mostakim Jihad — Odoo/ERP Marketing Website

A Django + Tailwind (CDN) marketing site for freelancing Odoo/ERP services. Includes a full admin panel for managing case studies, projects, clients, certifications, blog posts, and contact inquiries.

## Tech Stack

- **Backend**: Django 5.x
- **Frontend**: Tailwind CSS via CDN (single `<script>` tag, no build step)
- **Database**: PostgreSQL 14+
- **Image handling**: Pillow

## Project Structure

```
odoo_marketing_website/
├── core/           # Site config, services, contact form, home/about views
├── portfolio/      # Case studies, projects, clients, certifications
├── blog/           # Blog posts
├── templates/      # All HTML templates
├── static/         # CSS, JS, image assets
├── media/          # User-uploaded files (admin uploads)
└── manage.py
```

## First-Time Setup

### 1. Create the PostgreSQL database and user

Run these as a user with `sudo` privileges (e.g. your normal user with sudo access):

```bash
sudo -u postgres psql -c "CREATE USER odoo_business WITH PASSWORD 'odoo_business';"
sudo -u postgres psql -c "CREATE DATABASE odoo_business OWNER odoo_business;"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE odoo_business TO odoo_business;"
```

If you'd rather use SQLite for local development, edit `core/settings.py` and replace the `DATABASES` block with:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

The defaults match the brief (`odoo_business` / `odoo_business` on `localhost`). Edit `.env` if your setup differs.

### 3. Install dependencies

```bash
# Option A — use a virtual environment (recommended)
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Option B — install globally (not recommended on shared systems)
pip install -r requirements.txt
```

### 4. Run migrations and create a superuser

```bash
python manage.py migrate
python manage.py createsuperuser
```

The migrations will seed:
- All 11 services
- Site-wide settings (with bio content from the CV)
- Two sample clients (replace via admin)
- Two placeholder Odoo certifications (edit via admin)

### 5. Run the dev server

```bash
python manage.py runserver
```

- Public site: http://localhost:8000/
- Admin panel: http://localhost:8000/admin/

## Admin Workflow

After logging into `/admin/`, use these sections to manage content:

| Section | What you can do |
|---------|-----------------|
| **Core › Site Settings** | Singleton page. Edit hero text, profile image, CV download, contact info, social links, Fiverr URL, stats counters. |
| **Core › Services** | Edit the 11 services, reorder them, change icons. |
| **Core › Contact inquiries** | View messages submitted through the contact form. Mark read/unread. |
| **Portfolio › Case studies** | Add detailed client case studies (problem/solution/results). |
| **Portfolio › Success projects** | Add portfolio entries with cover images and links. |
| **Portfolio › Clients** | Add client logos, websites, and testimonials. Mark "featured" to show on home. |
| **Portfolio › Certifications** | Add Odoo / other certifications with credential URLs. |
| **Blog › Posts** | Write blog articles. Mark "is published" and set `published_at` to publish. |

## Pages

| URL | Purpose |
|-----|---------|
| `/` | Home — hero, stats, services preview, featured portfolio, clients, blog, CTA |
| `/about/` | Bio, education, experience, achievements, certifications |
| `/services/` | All 11 services |
| `/services/<slug>/` | Service detail page |
| `/portfolio/` | Case studies + projects |
| `/portfolio/case-studies/<slug>/` | Case study detail |
| `/portfolio/projects/<slug>/` | Project detail |
| `/clients/` | Client logos + testimonials |
| `/certifications/` | Certification grid |
| `/blog/` | Blog post list |
| `/blog/<slug>/` | Blog post detail |
| `/contact/` | Contact form + info |

## Customization

- **Colors**: Edit the `tailwind.config` block in `templates/base.html`. Primary purple `#714B67` and secondary teal `#017E84` are Odoo-inspired.
- **CV / profile image**: Upload via **Core › Site Settings** in admin.
- **Fiverr link**: Set `fiverr_url` in **Site Settings**.

## Deployment Notes

This README focuses on local development. For production, you'll want:
- `DJANGO_DEBUG=False` and a strong `DJANGO_SECRET_KEY`
- `DJANGO_ALLOWED_HOSTS` set to your domain
- Static files served via `python manage.py collectstatic` + nginx/white-noise
- Media files served from object storage (S3) or nginx
- HTTPS via Let's Encrypt
- Gunicorn or uWSGI behind nginx

## Troubleshooting

**`connection to server ... failed: FATAL: database "odoo_business" does not exist`** — The DB wasn't created. Run the SQL commands in step 1.

**`ModuleNotFoundError: No module named 'decouple'`** — Install dependencies: `pip install -r requirements.txt`.

**Tailwind styles don't load** — You need internet access for the CDN script. Check the browser network tab.
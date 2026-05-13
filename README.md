# PG Tutoring Hub

Lightweight Django tutoring platform with a small Node-based frontend workflow used for building Tailwind CSS assets.

Quick start (development):

1. Create and activate Python virtualenv

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Python deps

```bash
pip install -r requirements.txt
```

3. Install frontend tooling and build Tailwind

```bash
cd frontend
npm install
npm run build:css    # builds static/css/tailwind.css
```

4. Run Django dev server

```bash
cd ../
DEBUG=True USE_SQLITE=True python manage.py migrate
DEBUG=True USE_SQLITE=True python manage.py runserver
```

Notes:
- Compiled assets like `static/css/tailwind.css` are ignored by `.gitignore` and should be built in CI or locally when developing.
- See `docs/Tailwind_Pastel_Play.md` for design tokens and Tailwind usage.

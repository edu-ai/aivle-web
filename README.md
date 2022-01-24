# aiVLE: AI Virtual Learning Environment

> This repository is for aiVLE backend (a REST API server). For frontend, please refer to [aiVLE FE](https://github.com/le0tan/aivle-fe).

## Requirements

 * Python >= 3.7
 * Django
 * Additional requirements listed in `requirements.txt`

## Setup

1. Install the requirements
```
pip install -r requirements.txt
```

2. Create your [secret key](https://djecrety.ir/) and store it in ``.env`` as 
```dotenv
SECRET_KEY=<redacted>
BROKER_URI=<redacted>
FRONTEND_URL=<redacted>
EMAIL_HOST_USER=<redacted>
EMAIL_HOST_PASSWORD=<redacted>
DEFAULT_FROM_EMAIL=<redacted>
```

3. Create the `/logs` directory in the same level as `manage.py`/`/app`

4. Migrate and create the superuser
```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

5. Run server
```
python manage.py runserver
```

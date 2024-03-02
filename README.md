## This is a Django REST Framework (DRF) project that includes the implementation of user registration and authentication logic.
___

## Getting Started

### Make sure you have the following installed:
- Python (version 3.6 or higher)
- Django
- Django REST Framework

## Installation

1. ### Clone the repository:

```git clone git@github.com:raevul/Neobis_Auth_Project.git```

2. ### Set up the virtual environment

```python3 -m venv .venv```

3. ### Activate the virtual environment:
   - On Linux or macOS: </br>
   ```source venv/bin/activate```
    - On Windows: </br>
   ```venv\Scripts\activate```

4. ### Install dependencies:

```pip install -r requirements.txt```

### Database Setup

1. #### Apply migrations:
   ```python manage.py migrate```
2. #### Create a superuser:
   ```python manage.py createsuperuser```

### Then Run the Development Server
```python manage.py runserver```

### Run with gunicorn
```gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000```

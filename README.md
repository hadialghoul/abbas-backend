# Primefix Backend - Django API

This is the Django backend for handling contact form submissions from the Primefix website.

## Setup Instructions

1. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure email settings in `primefix_backend/settings.py`:**
   - Update `EMAIL_HOST` if not using Gmail
   - Set `EMAIL_HOST_USER` to your email address
   - Set `EMAIL_HOST_PASSWORD` to your email app password
   - For Gmail, you need to:
     - Enable 2-factor authentication
     - Generate an app-specific password at https://myaccount.google.com/apppasswords
     - Use that app password in `EMAIL_HOST_PASSWORD`

4. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

   The API will be available at `http://localhost:8000/api/contact/`

   **Note:** This app doesn't store form submissions in a database - it just sends emails directly. The SQLite database file (db.sqlite3) is only used by Django internally and can be ignored.

## API Endpoint

### POST /api/contact/

Submit a contact form.

**Request Body (JSON):**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "mobile": "123-456-7890",
    "service": "Electrical"
}
```

**Success Response (200):**
```json
{
    "success": true,
    "message": "Thank you for your submission! We will get back to you soon."
}
```

**Error Response (400/500):**
```json
{
    "success": false,
    "message": "Error message here"
}
```

## Production Deployment Notes

Before deploying to production:
1. Change `DEBUG = False` in settings.py
2. Update `SECRET_KEY` to a secure random value
3. Set `ALLOWED_HOSTS` to your domain
4. Configure proper email settings for your production environment
5. Set up proper CORS settings (restrict `CORS_ALLOW_ALL_ORIGINS`)
6. Use environment variables for sensitive settings (EMAIL_HOST_PASSWORD, SECRET_KEY, etc.)


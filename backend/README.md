# YubiKey Bitcoin Seed Storage Backend

This is the backend for the YubiKey Bitcoin Seed Storage application. It provides APIs for managing Bitcoin seed phrases securely using YubiKeys.

## Blueprint Organization

The application uses multiple Flask blueprints to organize its routes:

### API Blueprints

1. **Seed API Blueprint (`seed_blueprint` from `routes/seed_routes.py`)**
   - URL Prefix: `/api/v1`
   - Purpose: RESTful API for seed management (create, read, update, delete)
   - Authentication: JWT token-based authentication
   - Used by: Mobile apps, frontend SPA, and other API clients

2. **YubiKey API Blueprint (`yubikey_blueprint` from `routes/yubikey_routes.py`)**
   - URL Prefix: None (routes defined within the blueprint)
   - Purpose: YubiKey management and WebAuthn operations
   - Authentication: JWT token-based authentication
   - Used by: Mobile apps, frontend SPA, and other API clients

### Web Interface Blueprints

1. **Seeds Web Blueprint (`seeds_bp` from `api/seeds.py`)**
   - URL Prefix: `/api/seeds`
   - Purpose: Web interface for seed management
   - Authentication: Session-based authentication
   - Used by: Web browser users
   - Includes routes for rendering HTML pages and handling form submissions

2. **Auth Blueprint (`auth_bp` from `api/auth.py`)**
   - URL Prefix: None (routes defined within the blueprint)
   - Purpose: Authentication for the web interface
   - Authentication: Session-based authentication
   - Used by: Web browser users

## Authentication

The application supports two authentication methods:

1. **JWT Token Authentication**
   - Used by API routes
   - Token is passed in the `Authorization` header as `Bearer <token>`
   - Protected by the `@login_required` decorator from `services/auth_service.py`

2. **Session-based Authentication**
   - Used by web interface routes
   - Session is stored in a cookie
   - Protected by checking `session.get('authenticated')` in route handlers

## Testing

For testing purposes, the application supports bypassing authentication:

1. Set `app.config["TESTING_AUTH_BYPASS"] = True`
2. Set `app.config["TESTING_AUTH_USER_ID"] = "<user_id>"` to specify the test user ID

## Development

To run the application in development mode:

```bash
python app.py
```

## Production

For production deployment, use a WSGI server like Gunicorn:

```bash
gunicorn app:app
``` 
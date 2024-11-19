
# User Authentication and Registration System

## Project Overview
This project implements a user authentication and registration system.
This system allows users to:
1. Enter their phone number.
2. Authenticate using a password if already registered.
3. Generate a 6-digit OTP for new users to verify and complete registration.
4. Provide additional personal information (e.g., first name, last name, and email) after OTP verification.

### Special Features
- **Rate Limiting**: The system blocks users after 3 consecutive failed login attempts or incorrect OTP submissions. The blocking mechanism is based on both user attempts and IP address and lasts for 1 hour.
- **Secure Handling**: Secure token handling and password validation are incorporated for robust security.

## Local Configuration
The project includes a `local_settings.py` file (not included in the repository) with the following fields:

```python
DEBUG =  # Value should be True or False to set the debug mode
SECRET_KEY =  # Django secret key used for cryptographic signing
DB_NAME =  # Name of the database postgres
DB_PASSWORD =  # Password for the database postgres
DB_HOST =  # Database host (e.g., localhost or an IP address)
DB_USER =  # Username for the database postgres
DB_PORT =  # Port number for connecting to the database postgres

```

Make sure to create this file locally and add the above configurations for running the project.

## Installation Guide
1. Clone the repository.
2. Navigate to the project directory.
3. Install the required dependencies using:
    ```bash
    pip install -r requirements.txt
    ```
4. Create a `local_settings.py` file as described above.
5. Run the Django migrations:
    ```bash
    python manage.py migrate
    ```
6. Start the development server:
    ```bash
    python manage.py runserver
    ```

## Postman Collection
A Postman Collection is provided in the `postman` folder to facilitate API testing. Import it into Postman to test different endpoints.

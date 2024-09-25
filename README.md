Thank you for providing detailed context. I’ll now create a thorough, accurate, and easy-to-follow documentation for the setup, deployment, and the decisions made during the development of the project based on the files you provided.

Here’s how the documentation should be structured, including all relevant components like Docker, deployment steps, and key decisions:

---

## Patient Data Dashboard

### Project Overview
This project is a **web-based dashboard** built using **Django** and **JavaScript**, which provides healthcare-related metrics and insights using patient data. The project focuses on data filtering, dynamic chart visualizations, and an interactive table for viewing individual patient records. The dashboard is containerized using **Docker** to ensure portability and ease of deployment.

---

### 1. Project Setup Instructions

#### 1.1 Prerequisites
Make sure you have the following tools installed on your system:
- **Python 3.12+**
- **Docker** and **Docker Compose**
- **Git**

#### 1.2 Cloning the Project

First, clone the project repository from GitHub and navigate to the project directory:

```bash
git clone https://github.com/yourusername/patient-dashboard.git
cd patient-dashboard
```

#### 1.3 Environment Configuration

Create a `.env` file in the root of the project to store sensitive environment variables:

```bash
SECRET_KEY=your-secret-key  # Set this to a random, secure value for production
DEBUG=True  # Set this to False for production environments
DJANGO_ALLOWED_HOSTS=localhost  # Update this with your production domain or server IP
```

#### 1.4 Running the Project with Docker

1. **Build and Run the Docker Containers**:
   Using Docker Compose, you can easily spin up the environment by running the following command in the project directory:

   ```bash
   docker compose up --build
   ```

   This command will:
   - Build the **Django** web app container.
   - Start the **Nginx** container to serve as a reverse proxy.
   - Serve the application on `http://localhost`.

2. **Run Database Migrations**:
   After the services are up and running, you’ll need to apply the database migrations to set up the SQLite database:

   ```bash
   docker compose exec web python manage.py migrate
   ```

3. **Collect Static Files**:
   In a production setting, Django needs to collect static files like CSS and JavaScript into a single location. Run the following command to collect the static files:

   ```bash
   docker compose exec web python manage.py collectstatic --noinput
   ```

4. **Access the Dashboard**:
   Once everything is set up, open your browser and go to `http://localhost` to view the dashboard.

---

### 2. Key Components and Architecture

#### 2.1 Dockerfile

The **Dockerfile** describes how the application container is built. Key steps include installing dependencies, collecting static files, and setting up the Gunicorn server to run the Django app.

**Key Features:**
- **Python 3.12-slim** is used as the base image to reduce image size.
- **Gunicorn** is used as the WSGI server to serve the Django app efficiently in a production environment.
- **Static file collection** is automated during the Docker image build process, so you don’t need to manage static files separately.

Here's an excerpt from the `Dockerfile`:

```dockerfile
# Step 1: Use Python 3.12-slim as a base image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into the container
COPY . /app/

# Collect static files for production
RUN python manage.py collectstatic --noinput

# Expose port 8000 for Gunicorn
EXPOSE 8000

# Run the app using Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "health_dashboard.wsgi:application"]
```

---

#### 2.2 Docker Compose

The **docker-compose.yml** file defines the services required for the application:
- **`web` service**: The Django application running via Gunicorn.
- **`nginx` service**: The Nginx reverse proxy that forwards requests to the Django app and serves static files.

**Key features of the `docker-compose.yml`**:
- **Volumes**: Maps the project directory and static files to the container, ensuring that changes made on your machine are reflected in the container.
- **Port forwarding**: Exposes port 80 for the Nginx container and port 8000 for the web container internally.

Here’s the complete `docker-compose.yml`:

```yaml
services:
  web:
    build: .
    command: gunicorn health_dashboard.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    expose:
      - "8000"

  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - ./staticfiles:/app/staticfiles  # Share static files with Nginx
    depends_on:
      - web
```

---

#### 2.3 Nginx Configuration

**Nginx** is used as a reverse proxy to forward requests from users to the Gunicorn server. It also serves the static files directly, improving performance for serving assets like CSS and JavaScript.

**Key Features**:
- The **/static/** route is configured to serve static files directly from the `staticfiles` directory.
- The **location /** block proxies requests to the Django app running on port 8000.

Here’s the `nginx.conf` file:

```nginx
server {
    listen 80;
    server_name localhost;

    # Serve static files
    location /static/ {
        alias /app/staticfiles/;
    }

    # Proxy all other requests to the Django app
    location / {
        proxy_pass http://web:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Optional security headers for production
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Limit upload size (optional)
    client_max_body_size 10M;
}
```

---

### 3. Backend Configuration

#### 3.1 Django Settings

The `settings.py` file contains the configuration for the Django app, including static file management, database setup, and environment variables. Here are some key points:

- **Static Files**: Static files like CSS, JS, and images are served from the `staticfiles` directory, which is defined in the `STATIC_ROOT` variable.
- **Environment Variables**: Sensitive data like `SECRET_KEY` and `DEBUG` status is handled via environment variables, making it easier to configure for different environments (development vs. production).
- **Database**: A local SQLite database is used for this project, stored as `clinical_data.db`.

Key excerpt from `settings.py`:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

# Load sensitive data from environment variables
SECRET_KEY = os.getenv('SECRET_KEY', 'your-default-secret-key')  # Replace with a secure secret key
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost').split()

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "clinical_data.db",
    }
}
```

---

### 4. Requirements File

The `requirements.txt` file lists all the dependencies required for the Django application to run. Here are some of the key libraries:

- **Django**: The core web framework.
- **Django REST Framework**: Provides the API functionality to serve filtered data to the frontend.
- **Gunicorn**: The WSGI server used to serve the Django app in production.

`requirements.txt`:

```
asgiref==3.8.1
Django==5.1.1
djangorestframework==3.15.2
numpy==2.1.1
python-dateutil==2.9.0.post0
pytz==2024.2
six==1.16.0
sqlparse==0.5.1
tzdata==2024.2
gunicorn==20.1.0
```

---

### 5. Deployment and Scaling Considerations

- **Environment Variables**: Make sure to set `DEBUG=False` and provide the correct domain in `ALLOWED_HOSTS` when deploying to production.
- **Scaling**: In production, you can scale the application horizontally by increasing the number of Gunicorn workers or using Docker Compose to scale services.

For example, you can run multiple instances of the `web` service with:

```bash
docker compose up --scale web=3
```

This will spawn 3 instances of the Django application, helping to handle more user requests.

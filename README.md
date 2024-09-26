## Patient Data Dashboard

### Project Overview
This project is a **web-based dashboard** built using **Django** and **JavaScript**, which provides healthcare-related metrics and insights using patient data. The project focuses on data filtering, dynamic chart visualisations, and an interactive table for viewing individual patient records. The dashboard is containerised using **Docker** to ensure portability and ease of deployment.

---

## 1. Instructions on How to Set Up and Run the Application

### 1.1 Prerequisites
Ensure you have the following tools installed on your system:
- **Python 3.12+**
- **Docker** and **Docker Compose**
- **Git**

### 1.2 Cloning the Project

To begin, clone the project repository from GitHub and navigate to the project directory:

```bash
git clone https://github.com/MemonMustafa19/uq-test.git
cd uq-test
```

### 1.3 Move Your Database File

Place your `clinical_data.db` SQLite database file into the project directory to use the pre-existing data.

### 1.4 Running the Project with Docker

1. **Build and Run the Docker Containers**:
   To build and start the application using Docker Compose, run the following command in the project directory:

   ```bash
   docker compose up --build
   ```

   This command will:
   - Build the **Django** web application container.
   - Start the **Nginx** container to act as a reverse proxy.
   - Serve the application on `http://localhost`.

2. **Run Database Migrations**:
   After the services are up and running, you need to apply the database migrations to create the required core Django tables (e.g., `auth`, `admin`, `sessions`). However, if the `patient_data` table already exists in your database, you need to **fake the migration** for it to prevent Django from trying to recreate that table.

   - If your database already has the `patient_data` table, run the following command to **fake the migration** for that app:

     ```bash
     docker compose exec web python manage.py migrate --fake patient_data
     ```

     This will tell Django to skip creating the `patient_data` table, as it already exists.

   - After faking the migration (if applicable), or if the `patient_data` table doesn't exist, run the following command to apply the migrations for all the other core tables:

     ```bash
     docker compose exec web python manage.py migrate
     ```

   This will apply all the migrations for the core Django tables without affecting the `patient_data` table.

3. **Collect Static Files**:
   Django needs to collect static files (CSS, JavaScript) into a single directory in production. Run the following command to collect static files:

   ```bash
   docker compose exec web python manage.py collectstatic --noinput
   ```

4. **Access the Dashboard**:
   Once everything is configured and running, open your browser and navigate to `http://localhost` to view and use the dashboard.

---

## 2. Deploying the Dashboard to a Production Server Using Docker

### Dockerisation for Production

To deploy the dashboard to a production server using Docker, follow these steps:

### 2.1 Creating the Dockerfile

The **Dockerfile** describes the process of building the application container. This includes installing dependencies, setting up the Gunicorn server, and collecting static files.

Key steps in the Dockerfile:
- Use **Python 3.12-slim** to keep the image lightweight.
- Install dependencies from the `requirements.txt` file.
- Collect static files and use **Gunicorn** as the production server.

Here’s an example Dockerfile:

```dockerfile
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

### 2.2 Docker Compose Setup

Docker Compose simplifies the orchestration of multiple services like Django and Nginx.

The **docker-compose.yml** file defines two key services:
- **`web` service**: Runs the Django application using Gunicorn.
- **`nginx` service**: Acts as a reverse proxy to serve static files and forward user requests to the Django app.

Here’s the `docker-compose.yml`:

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
      - ./staticfiles:/app/staticfiles
    depends_on:
      - web
```

### 2.3 Nginx Configuration

Nginx is responsible for handling static files and forwarding requests to the Django app through Gunicorn. The configuration file (`nginx.conf`) defines how Nginx serves static files from the `staticfiles` directory and how it proxies all other requests to Gunicorn.

Here’s an example Nginx configuration:

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

    # Security headers
    add_header X-Frame-Options SAMEORIGIN;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Limit upload size
    client_max_body_size 10M;
}
```

### 2.4 Managing Environment Variables

To ensure the app runs correctly in both development and production, environment variables should be used to manage sensitive data like the secret key, debug status, and allowed hosts.

Example `.env` file:

```env
SECRET_KEY=your-production-secret-key
DEBUG=False  # Set to False in production
DJANGO_ALLOWED_HOSTS=your-production-domain.com
```

Make sure to set `DEBUG=False` and provide the correct domain name in `ALLOWED_HOSTS` for security reasons.

### 2.5 Scaling the Application

In production, you may need to scale the application to handle more traffic. Docker Compose allows you to run multiple instances of the `web` service:

```bash
docker compose up --scale web=3
```

This command will run 3 instances of the Django application to distribute the load and improve the app’s ability to handle multiple requests simultaneously.

### 2.6 Security Considerations

For production deployments, ensure:
- **HTTPS**: Use an SSL/TLS certificate (e.g., via Let's Encrypt) for secure communication.
- **Environment Variables**: Ensure sensitive data like `SECRET_KEY` is stored securely and never hard-coded.
- **Static Files**: Ensure Nginx serves static files efficiently to reduce the load on Django.

---

## 3. Explanations of Key Decisions Made During the Development Process

### 3.1 Models (Data Representation)

The **`Patient` model** is the core of the application, representing how patient data is stored and retrieved.

Key decisions:
- **Structured Data Storage**: 
  - Fields like `diagnosis`, `gender`, and `lab_results` allow for easy querying and filtering of patient records.
  - The `primary_key=True` on `patient_id` ensures that each patient is uniquely identifiable.

- **Optional Fields**: 
  - The `medication` field is optional (`null=True, blank=True`), allowing flexibility in cases where a patient may not have any prescribed medication.

- **Custom Table Name**: 
  - Using `Meta` to set a custom table name (`patient_data`) improves the clarity of the database schema.

### 3.2 API Design with Django REST Framework

The API endpoints serve patient data and filter options to the frontend via Django REST Framework.

Key decisions:
- **Efficient Serialization**: 
  - **`PatientSerializer`** is a `ModelSerializer`, which simplifies the process of serializing model data into JSON format for API responses.

- **Filter Options API**:
  - The **filter options** endpoint dynamically retrieves distinct values for diagnosis, gender, and visit type, making the frontend adaptable to changes in the dataset.

- **CSV Export**: 
  - The API endpoint for exporting patient data in CSV format is crucial for healthcare professionals who need to perform offline analysis.

### 3.3 Filtering Logic

Filtering patient data based on diagnosis, gender, visit type, and date range is a critical feature.

Key decisions:
- **Multiple Criteria Filtering**: 
  - The use of `getlist` allows users to filter by multiple values in each category, providing a flexible and powerful filtering mechanism.

- **Date Range Filtering**: 
  - Allowing both start and end dates (`from_date`, `to_date`) ensures that users can precisely filter records within specific timeframes.

### 3.4 Frontend (UI & UX)

The user interface provides a seamless experience for filtering data and viewing results in a dynamic and interactive way.

Key decisions:
- **Multi-Select Filters**: 
  - The **Select2** library is used for searchable, multi-select dropdowns, improving usability when there are many filter options.

- **Real-Time Data Loading**: 
  - Data is loaded dynamically into the DataTable and Chart.js visualisation based on the selected filters, providing an interactive experience without page reloads.

- **CSV Export**: 
  - Users can export filtered patient data to CSV format for further offline analysis, making the dashboard more versatile.

### 3.5 Testing

Comprehensive testing ensures the robustness of the filtering logic and API endpoints.

Key decisions:
- **Diverse Dataset**: 
  - The `setUp` method creates a diverse set of test patients to validate the filtering logic against various combinations of diagnoses, genders, visit types, and outcomes.

- **Comprehensive Filter Testing**: 
  - Tests cover filtering by individual criteria as well as combinations, ensuring that the filtering works as expected across different scenarios.

- **CSV Export Validation**: 
  - Tests verify that the CSV export functionality correctly generates and downloads the filtered patient data.

### 3.6 Dockerisation and Deployment

The use of Docker and Docker Compose ensures a smooth deployment process.

Key decisions:
- **Lightweight Container**: 
  - The **Python 3.12-slim** base image ensures a lightweight container, reducing build time and resource consumption.

- **Gunicorn for Production**: 
  - **Gunicorn** is chosen as the WSGI server to handle multiple requests concurrently, making it a production-ready solution.

- **Nginx Reverse Proxy**: 
  - Using **Nginx** to serve static files and forward requests to the Django app ensures that static assets are served efficiently, reducing the load on the application.

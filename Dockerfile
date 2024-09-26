# Step 1: Use Python 3.12-slim as a base image
FROM python:3.12-slim

# Step 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 3: Set the working directory in the container
WORKDIR /app

# Step 4: Copy the requirements file into the container
COPY requirements.txt /app/

# Step 5: Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the current directory into the container
COPY . /app/

# Step 7: Collect static files for production
RUN python manage.py collectstatic --noinput

# Step 8: Expose the port that the app runs on (8000 for Django)
EXPOSE 8000

# Step 9: Run Gunicorn to serve the Django app
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "health_dashboard.wsgi:application"]
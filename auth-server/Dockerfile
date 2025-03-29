# Use official Python image
FROM python:3.9

# Set working directory inside container
WORKDIR /app

# Copy requirements first (for efficient caching)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Start the Flask server
CMD [ "gunicorn", "--bind" , "0.0.0.0:5200" , "app:app"]

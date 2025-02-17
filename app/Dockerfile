FROM python:3.10-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy your application code
COPY . .

# Command to run the Python app
CMD ["python", "main.py"]
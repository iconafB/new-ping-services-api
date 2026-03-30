FROM python:3.12-slim

WORKDIR /app

# Prevent python from writing .pyc files and buffer logs
ENV PYTHONDONTWRITEBYTECODE=1

ENV PYTHONUNBUFFERED=1

#Install dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

#copy application
COPY . .

#expose the app port
EXPOSE 8000

# Start the fastapi app
CMD [ "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" ]

FROM python:3.10-slim-bullseye

# Copy source code and set working directory
COPY . /app
WORKDIR /app

# Install dependencies
RUN apt-get update -y \
    && apt-get install -y libpq-dev gcc \
    && pip install --upgrade pip \
    && pip install psycopg2 \
    && rm -rf /var/lib/apt/lists/*

# Install the requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install the testing requirements
COPY requirements_test.txt requirements_test.txt
RUN pip install -r requirements_test.txt

# Start app
ENV FLASK_APP=application.py
ENV FLASK_DEBUG=0
CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"]

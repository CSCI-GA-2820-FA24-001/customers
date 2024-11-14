##################################################
# Create production image
##################################################
FROM quay.io/rofrano/python:3.11-slim

# Set the working directory and install dependencies without dev dependencies
WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN python -m pip install --upgrade pip poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

# Copy the application code
COPY wsgi.py .
COPY service ./service

# Create a non-root user and set file ownership
RUN useradd --uid 1001 flask && \
    chown -R flask /app
USER flask

# Set environment variables for the application
ENV FLASK_APP=wsgi:app
ENV PORT=8080
EXPOSE $PORT

# Configure Gunicorn and set entry point
ENV GUNICORN_BIND=0.0.0.0:$PORT
ENTRYPOINT ["gunicorn"]
CMD ["--log-level=info", "wsgi:app"]
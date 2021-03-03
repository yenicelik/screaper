FROM python:3.8.5
MAINTAINER David Yenicelik "david@theaicompany.com"

RUN apt-get update -y
RUN apt-get install postgresql -y postgresql-contrib

# Copy all files into the docker dir
COPY . /app
ENV HOME=/app
WORKDIR /app

# Install Python web server and dependencies
RUN pip install -r ./screaper_backend/requirements.txt

# Expose port
EXPOSE 5000
EXPOSE 80
EXPOSE 8080

ENTRYPOINT ["gunicorn", "-k", "gevent", "-b", "0.0.0.0:8080", "--timeout", "500", "--workers", "1", "screaper_backend.application.application:application", "--log-level", "debug"]
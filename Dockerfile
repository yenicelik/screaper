FROM python:3.8.5
MAINTAINER David Yenicelik "david@theaicompany.com"

RUN apt-get update -y
RUN apt-get install postgresql -y postgresql-contrib

# Copy all files into the docker dir
COPY ./screaper_backend/ /app/screaper_backend/
ENV HOME=/app
WORKDIR /app

# Install Python web server and dependencies
RUN pwd
RUN ls
RUN pip install -r screaper_backend/requirements.txt
RUN pwd
RUN ls
RUN ls screaper_backend

# Expose port
EXPOSE 5000
EXPOSE 80
EXPOSE 8080

ENTRYPOINT ["gunicorn", "-k", "gevent", "-b", "0.0.0.0:8080", "--timeout", "500", "--workers", "1", "screaper_backend.run:application", "--log-level", "debug"]
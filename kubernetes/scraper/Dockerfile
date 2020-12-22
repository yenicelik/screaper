FROM python:3.7.9-slim

# Both items are required
RUN apt-get update -y
RUN apt-get install postgresql -y postgresql-contrib
RUN apt-get install python-psycopg2 -y
RUN apt-get install libpq-dev -y

# Copy all files into the docker dir
# Copy all core files into docker dir
COPY ./screaper /app/screaper
COPY ./kubernetes/scraper/requirements.txt /app/requirements.txt

# COPY . /app
ENV HOME=/app
WORKDIR /app

# Install Python web server and dependencies
RUN pip install -r ./requirements.txt

# Run a single python application

CMD ["python", "-m", "screaper.run"]

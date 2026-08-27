# Use python 3.12 on Debian 12 bookworm
FROM python:3.12-bookworm
LABEL maintainer="Bounpunh, LOYSURYYA.PPunh@gmail.com"

ENV PYTHONUNBUFFERED=1

# Copy requirement files to tmp directory
COPY ./requirements/production.txt /tmp/production.txt
COPY ./requirements/development.txt /tmp/development.txt

# Set working directory
WORKDIR /django-project

# Expose ports
EXPOSE 8000  
EXPOSE 8001  
EXPOSE 5050  

# Set noninteractive and timezone
ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Vientiane
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata

# Set variable to determine Development or Production
ARG DEV=false

# Update system + install dependencies
# libpq5, build-essential are dependencies for psycopg3
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    apt-utils libpq5 build-essential memcached openssl bpython \
    gettext \
    python3-pip python3-cffi python3-brotli libpango-1.0-0 \
    libharfbuzz0b libpangoft2-1.0-0 libpangocairo-1.0-0 \
    fontconfig fonts-thai-tlwg && \
    apt-get upgrade -y && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Create python virtual environment
RUN python3 -m venv /venv

# Set PATH early so subsequent RUN commands use the venv
ENV PATH="/venv/bin:$PATH"

# Upgrade pip and install requirements
RUN pip install --upgrade pip
RUN pip install -r /tmp/production.txt

# Install additional requirements for development if DEV=true
RUN if [ "$DEV" = "true" ]; then pip install -r /tmp/development.txt; fi

# Remove temporary files
RUN rm -rf /tmp

# Create user account to run django app
RUN adduser --disabled-password --no-create-home django-user

# Change ownership of django-project directory to django-user
RUN chown -R django-user:django-user /django-project

# Hide errors of fonts config
RUN mkdir -p /var/cache/fontconfig && chmod 777 /var/cache/fontconfig

# Set Entrypoint
# ENTRYPOINT ["/entrypoint.sh"]

# Default command — change to gunicorn in production
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8001"]
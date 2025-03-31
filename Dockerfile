FROM python:3.11

WORKDIR /app

RUN <<EOF
apt update
apt install -y netcat-openbsd
apt-get clean
rm -rf /var/lib/apt/lists/*
EOF

RUN pip install poetry

COPY pyproject.toml /app

RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-root --only main

COPY job_manager ./job_manager
COPY manager ./manager
COPY dispatcher ./dispatcher
COPY executor ./executor
COPY launcher ./launcher
COPY templates ./templates
COPY static ./static

COPY manage.py .
COPY entrypoint.sh .
COPY clear_sessions.py .

ENV DJANGO_SETTINGS_MODULE=job_manager.settings.production

RUN python manage.py collectstatic --noinput

ENTRYPOINT ["bash", "entrypoint.sh"]
CMD ["gunicorn", "--workers", "2", "--bind", ":8000", "job_manager.wsgi"]

# job-manager

## Need

- [Orthanc](https://orthanc.uclouvain.be/)
- [Kheops](https://kheops.online/)
- [RabbitMQ](https://www.rabbitmq.com/)
- [SLURM](https://slurm.schedmd.com/documentation.html)
- Microsoft EntraID configuration


## Installation

```bash
python3.12 -m venv .venv
source .venv/bin/activate
poetry install
```

## Configuration

```bash
cp dev.env .env
```

Complete .env values.
For now, job-manager works with Microsoft EntraID only. 

## Server

To run server locally:
```bash
gunicorn --workers 2 --bind :8000 job_manager.wsgi
```


## With Docker

```bash
docker compose pull
docker compose build
docker compose up -d
```

### At each release
For each release that change how the session data is store,
we need to clear it for all users. To do so run this in the container
```shell
python manage.py shell < clear_sessions.py
```

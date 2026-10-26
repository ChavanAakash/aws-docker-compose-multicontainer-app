# AWS Docker Compose Multi-Container App

A practical next step after Docker basics: run a small web application and Redis using Docker Compose on Ubuntu EC2.

## What this project demonstrates

- Docker Compose service orchestration
- Multi-container networking using service names
- Environment variables and configuration
- Health checks and restart policies
- Persistent named volumes for Redis data
- Basic troubleshooting and validation
- Safe deployment guidance for an EC2 instance

> This is a learning lab, not a production-ready application. Do not store real secrets in the repository. Run on your own AWS account and check costs.

## Architecture

```text
Browser
  |
  | HTTP :8080 (restrict inbound access to your IP)
  v
EC2 Ubuntu host
  |
  | Docker Compose
  +---- web (Python Flask, host 8080 -> container 5000)
  |       |
  |       | Docker Compose service DNS: redis:6379
  |       v
  +---- redis (Redis server, internal only)
          |
          +---- named volume: redis-data
```

## Repository structure

```text
aws-docker-compose-multicontainer-app/
├── app/
│   ├── app.py
│   └── requirements.txt
├── screenshots/
│   └── README.md
├── .dockerignore
├── .env.example
├── .gitignore
├── compose.yaml
├── Dockerfile
└── README.md
```

## Prerequisites

- Ubuntu 22.04 or 24.04 EC2 instance
- Docker Engine and Docker Compose plugin installed
- Git
- Security group: SSH TCP 22 restricted to your IP; app TCP 8080 restricted to your IP for testing

See the Docker installation instructions in your previous `aws-ec2-docker-hands-on-lab` repository or Docker's official documentation.

## Run locally on EC2

Clone your public repository:

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/aws-docker-compose-multicontainer-app.git
cd aws-docker-compose-multicontainer-app
```

Create a local environment file from the example:

```bash
cp .env.example .env
```

The sample app does not require secrets. `.env` is ignored by Git; `.env.example` contains non-secret defaults.

Build and start the app:

```bash
sudo docker compose up --build -d
sudo docker compose ps
sudo docker compose logs --tail=50
```

Test from the EC2 instance:

```bash
curl http://localhost:8080
curl http://localhost:8080/health
```

Open `http://EC2_PUBLIC_IP:8080` in your browser. Replace `EC2_PUBLIC_IP` with your instance's public IPv4 address. The EC2 security group must allow TCP 8080 from your current IP. Do not expose Redis port 6379 publicly.

## Useful endpoints

- `/` — app status and Redis visit counter
- `/health` — simple application health response

Refreshing `/` increments the Redis counter. Redis data is stored in the named volume `redis-data`.

## Explore Compose

```bash
sudo docker compose config
sudo docker compose ps
sudo docker compose logs web
sudo docker compose logs redis
sudo docker compose exec web sh
sudo docker compose exec redis redis-cli ping
```

Expected Redis response: `PONG`.

## Persistence test

1. Open `/` and note the visit counter.
2. Restart the Compose services:

```bash
sudo docker compose restart
```

3. Refresh the page. The Redis counter should continue from its previous value because the named volume persists Redis data.

To test a full container recreation:

```bash
sudo docker compose down
sudo docker compose up --build -d
```

The named volume remains by default, so Redis data should persist.

**Warning:** This command removes the named volume and its data. Use only when you intentionally want a clean lab:

```bash
sudo docker compose down -v
```

## Troubleshooting

- **Port 8080 is already allocated:** change the host side of `8080:5000` in `compose.yaml` to `8081:5000`, then run `sudo docker compose up -d`.
- **Web app cannot reach Redis:** check `sudo docker compose ps` and `sudo docker compose logs web redis`. Use hostname `redis`, not `localhost`, from the web container.
- **App not reachable from browser:** test `curl http://localhost:8080` on EC2, then check the security group TCP 8080 source rule.
- **Build errors:** check Dockerfile, `requirements.txt`, and `sudo docker compose logs`.
- **Redis data resets unexpectedly:** ensure the named volume is configured and you did not run `docker compose down -v`.

## Cleanup

Stop and remove containers and the Compose network:

```bash
sudo docker compose down
```

This keeps the named volume. To also delete the lab data intentionally:

```bash
sudo docker compose down -v
```

Stop or terminate your EC2 instance when finished and review AWS billing. EBS storage and some networking resources can continue to incur charges even when an instance is stopped.

## Author

Aakash Chavan

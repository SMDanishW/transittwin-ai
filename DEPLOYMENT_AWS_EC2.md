# Deploying TransitTwin AI on AWS EC2

Single-instance Docker Compose deployment targeting `eu-north-1` (Stockholm).
HSL GTFS-RT feeds require an EU IP — this region satisfies that constraint.

---

## Why EC2 Docker Compose instead of EKS?

EKS / ECS is the right target for production-scale multi-tenant deployments, but it
adds ~$150–300/month in control-plane and node costs even at minimum scale.  For a
portfolio or demo deployment this stack runs comfortably on a single `t3.medium`
(~$30/month) or `t4g.medium` (~$22/month ARM).  The same `docker-compose.prod.yml`
and application code work unchanged when migrating to ECS Compose or a managed
Kubernetes cluster later — no application changes required, only infrastructure.

---

## CI/CD with GitHub Actions (automated deploys)

On every push to `main`, GitHub Actions builds both Docker images, pushes them to Amazon ECR, then SSHs into the EC2 instance to pull and restart — no manual steps required.

### AWS setup (one-time)

**1. Create two ECR repositories** in `eu-north-1`:
```
transittwin-backend
transittwin-frontend
```
AWS Console → ECR → Create repository (private) → repeat for both.

**2. Create an IAM user for CI** with programmatic access only.  
Attach a single inline policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "ecr:GetAuthorizationToken",
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:PutImage"
    ],
    "Resource": "*"
  }]
}
```
Save the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` — you will need them as GitHub secrets.

**3. Attach an IAM role to the EC2 instance** so it can pull from ECR without storing credentials.  
Create a role with the `AmazonEC2ContainerRegistryReadOnly` managed policy and attach it to your instance:  
EC2 Console → select instance → Actions → Security → Modify IAM role.

**4. Install the AWS CLI on the EC2 instance:**
```bash
sudo apt-get install -y awscli
```

### GitHub secrets setup

Go to your repo → Settings → Secrets and variables → Actions → New repository secret.

| Secret | Value |
|---|---|
| `AWS_ACCESS_KEY_ID` | From the CI IAM user created above |
| `AWS_SECRET_ACCESS_KEY` | From the CI IAM user created above |
| `EC2_HOST` | EC2 public IP or DNS hostname |
| `EC2_SSH_KEY` | Full contents of your `.pem` private key file |
| `NEXT_PUBLIC_API_URL` | `https://your-domain.com` or `http://<EC2-IP>` |

### First deploy

Do the manual first deploy (section 5 below) once so that `.env.production` exists on the server and the stack is running. After that every push to `main` deploys automatically.

### How a deploy works

1. Actions builds `transittwin-backend` and `transittwin-frontend` images on the runner
2. Both images are tagged with the commit SHA and pushed to ECR
3. Actions SSHs into EC2 and runs:
   - `aws ecr get-login-password | docker login` (using the instance IAM role)
   - `docker pull` the two new images
   - `docker compose up -d --no-build` with `BACKEND_IMAGE` / `FRONTEND_IMAGE` set to the new ECR tags
   - `docker image prune -f` to remove the previous images

The workflow file is at [.github/workflows/deploy.yml](.github/workflows/deploy.yml).

---

## Prerequisites

- AWS account with EC2 access in `eu-north-1`
- A Groq API key (<https://console.groq.com>)
- (Optional) A domain name pointing to the instance's Elastic IP

---

## 1. Launch the EC2 Instance

1. Open the EC2 console and choose **eu-north-1 (Stockholm)**.
2. Launch an Ubuntu 24.04 LTS instance — `t3.medium` (2 vCPU, 4 GB RAM) is the
   minimum recommended size for running all five containers.
3. Allocate and associate an **Elastic IP** so the address does not change on reboot.
4. Configure the **Security Group** with these inbound rules:

   | Port | Protocol | Source    | Purpose           |
   |------|----------|-----------|-------------------|
   | 22   | TCP      | Your IP   | SSH               |
   | 80   | TCP      | 0.0.0.0/0 | HTTP              |
   | 443  | TCP      | 0.0.0.0/0 | HTTPS (optional)  |

   Do **not** open 3000, 8000, 5432, or 6379 — those are internal to Docker.

5. Use a key pair you own and save the `.pem` file.

---

## 2. Install Docker on the Instance

```bash
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu

# Install Docker Compose plugin
sudo apt-get install -y docker-compose-plugin

# Re-login for group membership to take effect
exit
ssh -i your-key.pem ubuntu@<EC2_PUBLIC_IP>

# Verify
docker compose version
```

---

## 3. Clone the Repository

```bash
git clone https://github.com/<your-username>/transit-twin-ai.git
cd transit-twin-ai
```

---

## 4. Configure the Environment

```bash
cp .env.production.example .env.production
nano .env.production
```

Required fields to update:

| Variable | What to set |
|---|---|
| `POSTGRES_PASSWORD` | A strong unique password |
| `DATABASE_URL` | Same password as above in the connection string |
| `GROQ_API_KEY` | Your Groq API key |
| `BACKEND_CORS_ORIGINS` | `https://your-domain.com` or `http://<EC2_IP>` |
| `NEXT_PUBLIC_API_URL` | `https://your-domain.com` or `http://<EC2_IP>` |
| `USE_MOCK_SEED` | `false` for live HSL data, `true` for demo mode |

---

## 5. Deploy

```bash
chmod +x scripts/deploy-ec2.sh
./scripts/deploy-ec2.sh
```

Or run directly:

```bash
docker compose -f docker-compose.prod.yml --env-file .env.production up -d --build
```

The first build takes 3–5 minutes. Subsequent builds are faster due to layer caching.

---

## 6. Verify the Deployment

```bash
# All containers should be Up (healthy)
docker compose -f docker-compose.prod.yml ps

# Test endpoints
curl http://<EC2_PUBLIC_IP>/health
curl http://<EC2_PUBLIC_IP>/api/vehicles
curl http://<EC2_PUBLIC_IP>/docs

# Stream SSE vehicles (Ctrl-C to stop)
curl -N http://<EC2_PUBLIC_IP>/api/sse/vehicles
```

The frontend loads at `http://<EC2_PUBLIC_IP>`.

---

## 7. Update the Deployment

```bash
chmod +x scripts/update-ec2.sh
./scripts/update-ec2.sh
```

This pulls the latest code, rebuilds changed images, and restarts affected containers
with zero manual steps.

---

## 8. Viewing Logs

```bash
# All main services
./scripts/logs.sh

# Single service
./scripts/logs.sh worker
./scripts/logs.sh backend
./scripts/logs.sh nginx
```

---

## 9. Common Management Commands

```bash
# Container status
docker compose -f docker-compose.prod.yml ps

# Restart a single service
docker compose -f docker-compose.prod.yml restart backend

# Open a psql shell
docker compose -f docker-compose.prod.yml exec db psql -U postgres -d transittwin

# Open a Redis CLI
docker compose -f docker-compose.prod.yml exec redis redis-cli

# Stop all services (data volumes preserved)
docker compose -f docker-compose.prod.yml down
```

---

## 10. Backing Up PostgreSQL

```bash
# Dump to a file on the host
docker compose -f docker-compose.prod.yml exec db \
  pg_dump -U postgres transittwin > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore from a dump
docker compose -f docker-compose.prod.yml exec -T db \
  psql -U postgres transittwin < backup.sql
```

---

## 11. Enable HTTPS with Certbot (Optional)

Requires a domain name pointing at the instance's Elastic IP.

```bash
sudo apt-get install -y certbot

# Stop nginx temporarily so Certbot can bind port 80
docker compose -f docker-compose.prod.yml stop nginx

sudo certbot certonly --standalone -d your-domain.com

# Mount the certs into nginx and uncomment the HTTPS block in deploy/nginx/nginx.conf
# Then restart
docker compose -f docker-compose.prod.yml up -d nginx
```

---

## 12. Auto-start on Reboot (systemd)

```bash
# Copy the repo to /opt/transittwin (or adjust paths in the service file)
sudo cp -r . /opt/transittwin
sudo cp deploy/systemd/transittwin.service /etc/systemd/system/

sudo systemctl daemon-reload
sudo systemctl enable transittwin
sudo systemctl start transittwin
```

---

## 13. Troubleshooting

**Backend fails to start / seeding errors**

The backend logs a warning and continues if Digitransit seeding fails (e.g. API key
missing or rate-limited).  Set `USE_MOCK_SEED=true` to skip live seeding entirely.

```bash
docker compose -f docker-compose.prod.yml logs backend
```

**Worker not polling**

```bash
docker compose -f docker-compose.prod.yml logs worker
```

ARQ workers connect to Redis on startup.  If Redis is not healthy the worker will
exit with a connection error.  Check `docker compose ps` to confirm Redis is healthy.

**Frontend shows blank / cannot connect to API**

`NEXT_PUBLIC_API_URL` is baked into the Next.js bundle at build time.  If you change
it you must rebuild the frontend container:

```bash
docker compose -f docker-compose.prod.yml up -d --build frontend
```

**SSE stream disconnects immediately through Nginx**

Confirm `proxy_buffering off` is present in the SSE location block in
`deploy/nginx/nginx.conf`.  Restart nginx after any config change:

```bash
docker compose -f docker-compose.prod.yml restart nginx
```

**Database volume already exists with wrong credentials**

If you change `POSTGRES_PASSWORD` after the volume was first created, PostgreSQL will
reject logins because the password is stored inside the volume.  To reset:

```bash
# WARNING: destroys all data
docker compose -f docker-compose.prod.yml down -v
docker compose -f docker-compose.prod.yml up -d --build
```

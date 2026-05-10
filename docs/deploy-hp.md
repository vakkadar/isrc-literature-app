# HP Home Server Deployment Runbook

Stack: Django + Wagtail API, Next.js web, Postgres on host, Cloudflare Tunnel + Access.

- HP user: `rvakkada`
- App path: `/opt/isrc-literature-app`
- Domains: `isrc-literature.sanatanadharma.cloud` (web), `isrc-api.sanatanadharma.cloud` (api/admin)
- OS: Fedora 44

---

## One-time HP setup

### 1. Install Docker + Compose

```bash
sudo dnf install -y dnf-plugins-core
sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
sudo dnf install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
sudo usermod -aG docker rvakkada
# log out and back in for group to take effect
```

### 2. Install Postgres 16 on host

```bash
sudo dnf install -y postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```

Edit `/var/lib/pgsql/data/pg_hba.conf` — add line so Docker bridge can connect:
```
host    isrc_literature   isrc_user   172.16.0.0/12   scram-sha-256
host    isrc_literature   isrc_user   127.0.0.1/32    scram-sha-256
```

Edit `/var/lib/pgsql/data/postgresql.conf`:
```
listen_addresses = '*'
```

Open firewall for Docker bridge:
```bash
sudo firewall-cmd --permanent --zone=trusted --add-source=172.16.0.0/12
sudo firewall-cmd --reload
sudo systemctl restart postgresql
```

Create DB + user:
```bash
sudo -u postgres psql <<EOF
CREATE USER isrc_user WITH PASSWORD 'CHANGE_ME_STRONG_PASSWORD';
CREATE DATABASE isrc_literature OWNER isrc_user;
GRANT ALL PRIVILEGES ON DATABASE isrc_literature TO isrc_user;
EOF
```

### 3. Clone repo

```bash
sudo mkdir -p /opt/isrc-literature-app
sudo chown rvakkada:rvakkada /opt/isrc-literature-app
cd /opt
git clone https://github.com/<youruser>/isrc-literature-app.git
cd /opt/isrc-literature-app
```

### 4. Create `.env.hp`

```bash
cp .env.hp.example .env.hp
# Edit secrets:
#   DJANGO_SECRET_KEY  → python -c 'import secrets; print(secrets.token_urlsafe(50))'
#   POSTGRES_PASSWORD  → match the one set in Postgres above
#   EMAIL_HOST_PASSWORD → Gmail App Password (myaccount.google.com → Security → App passwords)
#   DJANGO_SUPERUSER_PASSWORD → admin login pw
nano .env.hp
chmod 600 .env.hp
```

### 5. Install Cloudflare Tunnel

```bash
sudo dnf install -y https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-x86_64.rpm
cloudflared tunnel login              # browser auth → select sanatanadharma.cloud
cloudflared tunnel create isrc-literature
# Note the tunnel UUID printed
```

Copy template:
```bash
mkdir -p ~/.cloudflared
cp /opt/isrc-literature-app/cloudflared-config.example.yml ~/.cloudflared/config.yml
nano ~/.cloudflared/config.yml      # replace <TUNNEL_UUID> with real UUID
```

Add DNS in Cloudflare dashboard (or via CLI):
```bash
cloudflared tunnel route dns isrc-literature isrc-literature.sanatanadharma.cloud
cloudflared tunnel route dns isrc-literature isrc-api.sanatanadharma.cloud
```

Install as systemd service:
```bash
sudo cloudflared service install
sudo systemctl status cloudflared
```

### 6. Cloudflare Access (Zero Trust)

Cloudflare dashboard → Zero Trust → Access → Applications → Add application:

- Type: **Self-hosted**
- App name: `isrc-literature-web`
- Subdomain: `isrc-literature`, domain `sanatanadharma.cloud`
- Identity providers: Google + One-Time PIN
- Policy "Owner only": Action Allow, Include → Emails: `rajkumar.vakkada@gmail.com`

Repeat for `isrc-api.sanatanadharma.cloud` (or skip if you want public API).

### 7. First deploy

```bash
cd /opt/isrc-literature-app
docker compose -f docker-compose.hp.yml up -d --build
docker compose -f docker-compose.hp.yml logs -f api      # watch migrations
```

Verify:
- Web: https://isrc-literature.sanatanadharma.cloud
- Admin: https://isrc-api.sanatanadharma.cloud/admin/

---

## Updates

```bash
ssh rvakkada@<hp-ip>
cd /opt/isrc-literature-app
./scripts/deploy-hp.sh
```

## Backups (weekly to USB)

```bash
# On HP, plug USB, mount at /mnt/usb, then:
pg_dump -U isrc_user -h 127.0.0.1 isrc_literature | gzip > /mnt/usb/isrc_$(date +%F).sql.gz
docker compose -f docker-compose.hp.yml exec -T api tar czf - /app/media > /mnt/usb/media_$(date +%F).tar.gz
```

Cron weekly Sunday 02:00:
```cron
0 2 * * 0 /opt/isrc-literature-app/scripts/backup-hp.sh
```

(write `scripts/backup-hp.sh` separately when USB mount path confirmed)

## Logs

```bash
docker compose -f docker-compose.hp.yml logs -f api
docker compose -f docker-compose.hp.yml logs -f web
sudo journalctl -u cloudflared -f
sudo journalctl -u postgresql -f
```

## Rollback

```bash
cd /opt/isrc-literature-app
git log --oneline -10
git checkout <good-sha>
docker compose -f docker-compose.hp.yml up -d --build
```

## Troubleshooting

- **api can't reach Postgres** → check `host.docker.internal:host-gateway` worked: `docker compose -f docker-compose.hp.yml exec api getent hosts host.docker.internal`. Verify `pg_hba.conf` allows `172.16.0.0/12`.
- **Cloudflare Tunnel red** → `sudo systemctl status cloudflared`; check `~/.cloudflared/config.yml` UUID matches credentials file.
- **Cloudflare Access loop** → ensure SECURE_SSL_REDIRECT=False (tunnel handles TLS).
- **Wagtail admin static missing** → `docker compose ... exec api python manage.py collectstatic --noinput`.

# Deploy — Arsip Dokumen Kampus (arsip.unisan-g.id)

Runbook for this specific VPS (`unisan-g.id`, Rocky Linux, user `amiruddin`), which already hosts several other apps (`sister_dashboard`, `kiakurma-pb`, etc.) behind a shared **host-level nginx**. This app follows the same convention: a Dockerized Django app bound to `127.0.0.1:8002`, reverse-proxied by the host nginx — it does **not** run its own nginx container.

DNS for `arsip.unisan-g.id` already points at this VPS's public IP (confirmed during setup), so DNS is not a step here.

## 1. Get the code onto the VPS

Apps on this server live under `/opt/<app-name>/`, owned by `amiruddin` (matching `/opt/sister_dashboard`, `/opt/kiakurma-pb`). The `amiruddin` user is already in the `docker` group, so no `sudo` is needed for any `docker`/`docker compose` command below.

```bash
cd /opt
git clone https://github.com/unisan-gtlo/arsip-kampus.git
cd arsip-kampus/webapp
```

(To update later: `cd /opt/arsip-kampus && git pull`.)

## 2. Configure environment

```bash
cp .env.example .env
nano .env   # or vi
```

Fill in every value:
- `SECRET_KEY` — generate with `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `ALLOWED_HOSTS=arsip.unisan-g.id`
- `DB_PASSWORD` — pick a strong password
- `GCP_*` fields — copy from the old Streamlit app's `service_account.json` / `.streamlit/secrets.toml`. **`GCP_PRIVATE_KEY` must keep its `\n` as literal two-character sequences**, not real newlines.
- `DRIVE_FOLDER_ID`, `SPREADSHEET_ID` — same as the old app.

⚠️ **`DRIVE_FOLDER_ID` must point to a folder inside a Google Shared Drive, not a personal "My Drive" folder.** Confirmed during testing: service accounts get a `storageQuotaExceeded` error uploading to regular My Drive storage. A Google Workspace admin needs to create a Shared Drive, add the service account's `client_email` as a member (Content Manager/Editor), and put `DRIVE_FOLDER_ID` inside it. Until this is done, document uploads will fail with a friendly error message (the app won't crash, but uploads won't work).

## 3. Build and start (no sudo needed — amiruddin is in the docker group)

```bash
docker compose -f docker-compose.prod.yml up -d --build
```

`migrate` and `collectstatic` run automatically on container start (see the `web` service's `command`). The app listens on `127.0.0.1:8002` only — not reachable from outside until nginx is wired up in step 5.

Check it's actually up:

```bash
curl -I http://127.0.0.1:8002/publik/
docker compose -f docker-compose.prod.yml logs -f web   # Ctrl+C to stop tailing
```

## 4. Create the first admin account

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker compose -f docker-compose.prod.yml exec web python manage.py shell -c \
  "from accounts.models import User; u = User.objects.get(username='YOUR_USERNAME'); u.role = 'admin'; u.nama = 'Nama Admin'; u.save()"
```

## 5. Wire up nginx (requires sudo — run these yourself)

Copy the prepared config into place and reload:

```bash
sudo cp /opt/arsip-kampus/webapp/deploy/arsip.unisan-g.id.conf /etc/nginx/conf.d/arsip.unisan-g.id.conf
sudo nginx -t && sudo systemctl reload nginx
```

At this point `http://arsip.unisan-g.id/` should work (no HTTPS yet).

## 6. Get a TLS certificate (requires sudo)

This server already uses certbot's nginx plugin for every other domain (see the `# managed by Certbot` blocks in `/etc/nginx/conf.d/*.conf`) — same pattern here:

```bash
sudo certbot --nginx -d arsip.unisan-g.id
```

Certbot will edit the conf file in place to add the SSL block and an HTTP→HTTPS redirect (identical to `sister.conf`/`sso.conf`). Renewal is already handled by whatever cron/systemd timer certbot set up for the other domains on this box — no extra step needed.

## 7. (Optional, one-time) Import legacy data from Google Sheets

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py import_legacy_sheets
```

⚠️ Imported users get an **unusable password** — bcrypt hashes from the old app cannot be converted to Django's hasher. The command prints the list of usernames that need a reset:

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py changepassword <username>
```

## 8. Post-launch checklist

- [ ] `https://arsip.unisan-g.id/publik/` loads without login and shows only `Umum` documents.
- [ ] `https://arsip.unisan-g.id/admin/` (Django admin) is reachable and requires login.
- [ ] Login as the admin account created in step 4 works.
- [ ] Uploading a document via `/dokumen/upload/` lands the PDF in the correct Google Drive Shared Drive folder.
- [ ] Every imported legacy user (if step 7 was run) has had their password reset before being told to log in.

## Updating the app later

```bash
cd /opt/arsip-kampus && git pull
cd webapp && docker compose -f docker-compose.prod.yml up -d --build
```

(migrate/collectstatic re-run automatically on container start.)

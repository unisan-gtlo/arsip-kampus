"""
One-time import of the legacy Streamlit app's Google Sheets data
(dokumen / users / kategori) into Postgres.

IMPORTANT: user passwords cannot be migrated. The old app hashed passwords
with bcrypt; Django's default hasher is PBKDF2, and bcrypt hashes cannot be
converted into that scheme. Imported users are created with an unusable
password and MUST have their password reset before they can log in.
"""

from datetime import datetime

import gspread
from django.conf import settings
from django.core.management.base import BaseCommand
from google.oauth2.service_account import Credentials

from accounts.models import User
from arsip.models import Dokumen, Kategori

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class Command(BaseCommand):
    help = "Import dokumen/users/kategori from the legacy Google Sheet into Postgres."

    def add_arguments(self, parser):
        parser.add_argument("--spreadsheet-id", default=None)
        parser.add_argument("--dry-run", action="store_true")

    def _get_client(self):
        creds = Credentials.from_service_account_info(settings.GCP_SERVICE_ACCOUNT, scopes=SCOPES)
        return gspread.authorize(creds)

    def _parse_tgl(self, value):
        for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(str(value).strip(), fmt)
            except (ValueError, TypeError):
                continue
        return None

    def handle(self, *args, **options):
        spreadsheet_id = options["spreadsheet_id"] or settings.SPREADSHEET_ID
        if not spreadsheet_id:
            self.stderr.write(self.style.ERROR("No SPREADSHEET_ID configured or provided."))
            return
        dry_run = options["dry_run"]

        client = self._get_client()
        spreadsheet = client.open_by_key(spreadsheet_id)

        kategori_count = self._import_kategori(spreadsheet, dry_run)
        dokumen_count = self._import_dokumen(spreadsheet, dry_run)
        user_count, imported_usernames = self._import_users(spreadsheet, dry_run)

        self.stdout.write(
            self.style.SUCCESS(
                f"{kategori_count} kategori imported, {dokumen_count} dokumen imported, "
                f"{user_count} users imported (passwords require reset)"
            )
        )
        if imported_usernames:
            self.stdout.write(self.style.WARNING("Users needing a password reset before they can log in:"))
            for username in imported_usernames:
                self.stdout.write(f"  - {username}  ->  python manage.py changepassword {username}")

    def _import_kategori(self, spreadsheet, dry_run):
        rows = spreadsheet.worksheet("kategori").get_all_records()
        count = 0
        for row in rows:
            nama = str(row.get("nama_kategori", "")).strip()
            if not nama:
                continue
            if not dry_run:
                _, created = Kategori.objects.get_or_create(nama_kategori=nama)
                if created:
                    count += 1
            else:
                count += 1
        return count

    def _import_dokumen(self, spreadsheet, dry_run):
        rows = spreadsheet.worksheet("dokumen").get_all_records()
        count = 0
        for row in rows:
            judul = str(row.get("judul", "")).strip()
            if not judul:
                continue
            kategori_nama = str(row.get("kategori", "")).strip()
            kategori = None
            if kategori_nama and not dry_run:
                kategori, _ = Kategori.objects.get_or_create(nama_kategori=kategori_nama)
            if not kategori and not dry_run:
                self.stdout.write(self.style.WARNING(f"Skipping '{judul}': no kategori"))
                continue

            defaults = {
                "kategori": kategori,
                "deskripsi": row.get("deskripsi", ""),
                "file_id": row.get("file_id", ""),
                "link_view": row.get("link_view", ""),
                "sifat": row.get("sifat") or Dokumen.Sifat.UMUM,
            }
            tgl = self._parse_tgl(row.get("tgl_upload"))

            if not dry_run:
                doc, created = Dokumen.objects.get_or_create(
                    nomor_dokumen=str(row.get("nomor_dokumen", "")).strip(),
                    judul=judul,
                    defaults=defaults,
                )
                if created:
                    if tgl:
                        Dokumen.objects.filter(pk=doc.pk).update(tgl_upload=tgl)
                    count += 1
            else:
                count += 1
        return count

    def _import_users(self, spreadsheet, dry_run):
        rows = spreadsheet.worksheet("users").get_all_records()
        count = 0
        imported = []
        for row in rows:
            username = str(row.get("username", "")).strip()
            if not username:
                continue
            if not dry_run:
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "nama": row.get("nama", ""),
                        "role": row.get("role") or User.Role.USER,
                    },
                )
                if created:
                    user.set_unusable_password()
                    user.save()
                    count += 1
                    imported.append(username)
            else:
                count += 1
                imported.append(username)
        return count, imported

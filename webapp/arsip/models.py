from django.conf import settings
from django.db import models
from django.urls import reverse


class Kategori(models.Model):
    nama_kategori = models.CharField(max_length=150, unique=True)

    # Editable setting shown as a hint on the upload form ("nomor terakhir
    # untuk kategori ini"). Auto-updated whenever a document is saved with a
    # non-empty nomor_dokumen for this kategori, but admins can also edit it
    # directly here - e.g. to seed a starting number for a new kategori.
    nomor_terakhir = models.CharField(
        max_length=255, blank=True, verbose_name="Nomor Dokumen Terakhir"
    )

    class Meta:
        ordering = ["nama_kategori"]
        verbose_name = "Kategori"
        verbose_name_plural = "Kategori"

    def __str__(self):
        return self.nama_kategori


class Dokumen(models.Model):
    class Sifat(models.TextChoices):
        UMUM = "Umum", "Umum"
        RAHASIA = "Rahasia", "Rahasia"

    class Status(models.TextChoices):
        DRAF = "Draf", "Draf"
        BERLAKU = "Berlaku", "Berlaku"
        TIDAK_BERLAKU = "Tidak Berlaku", "Tidak Berlaku"

    # Not unique: the old app only shows the last nomor per kategori as a hint
    # to the uploader, it never enforced or validated uniqueness.
    nomor_dokumen = models.CharField(max_length=255, blank=True)
    judul = models.CharField(max_length=500)
    kategori = models.ForeignKey(
        Kategori, on_delete=models.PROTECT, related_name="dokumen"
    )
    deskripsi = models.TextField(blank=True)

    # A document is stored EITHER as a local upload (file) OR as a pasted
    # Google Drive link (file_id/link_view) - never both. Local upload is
    # the default path; the Drive-link path exists because the campus
    # Drive account is a personal Gmail account with no Shared Drive
    # access, so some staff prefer linking a file they already uploaded
    # to their own Drive rather than re-uploading it to the server.
    file = models.FileField(upload_to="dokumen/%Y/%m/", blank=True, null=True)
    file_id = models.CharField(max_length=255, blank=True)
    link_view = models.URLField(max_length=500, blank=True)

    # Optional editable-master version alongside the PDF. Always local
    # upload only (no Drive-link option) and always login-gated regardless
    # of sifat - anonymous visitors may only ever access the PDF.
    file_docx = models.FileField(
        upload_to="dokumen_docx/%Y/%m/", blank=True, null=True, verbose_name="File Word (DOCX)"
    )

    sifat = models.CharField(max_length=10, choices=Sifat.choices, default=Sifat.UMUM)
    status = models.CharField(
        max_length=15, choices=Status.choices, default=Status.BERLAKU
    )
    tgl_upload = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dokumen_diunggah",
    )

    class Meta:
        ordering = ["-tgl_upload"]
        indexes = [
            models.Index(fields=["kategori"]),
            models.Index(fields=["sifat"]),
            models.Index(fields=["status"]),
            models.Index(fields=["nomor_dokumen"]),
        ]
        verbose_name = "Dokumen"
        verbose_name_plural = "Dokumen"

    @property
    def is_local(self):
        return bool(self.file)

    @property
    def preview_url(self):
        """URL that serves/redirects to the file, access-gated by sifat."""
        return reverse("arsip:dokumen_file", args=[self.pk])

    @property
    def download_url(self):
        return reverse("arsip:dokumen_download", args=[self.pk])

    @property
    def has_docx(self):
        return bool(self.file_docx)

    @property
    def download_url_docx(self):
        return reverse("arsip:dokumen_download_docx", args=[self.pk])

    @property
    def is_rahasia(self):
        return self.sifat == self.Sifat.RAHASIA

    @property
    def is_berlaku(self):
        return self.status == self.Status.BERLAKU

    @property
    def is_draf(self):
        return self.status == self.Status.DRAF

    def __str__(self):
        return f"{self.nomor_dokumen} - {self.judul}" if self.nomor_dokumen else self.judul

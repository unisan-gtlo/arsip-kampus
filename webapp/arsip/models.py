from django.conf import settings
from django.db import models


class Kategori(models.Model):
    nama_kategori = models.CharField(max_length=150, unique=True)

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

    # Not unique: the old app only shows the last nomor per kategori as a hint
    # to the uploader, it never enforced or validated uniqueness.
    nomor_dokumen = models.CharField(max_length=255, blank=True)
    judul = models.CharField(max_length=500)
    kategori = models.ForeignKey(
        Kategori, on_delete=models.PROTECT, related_name="dokumen"
    )
    deskripsi = models.TextField(blank=True)
    file_id = models.CharField(max_length=255)
    link_view = models.URLField(max_length=500)
    sifat = models.CharField(max_length=10, choices=Sifat.choices, default=Sifat.UMUM)
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
            models.Index(fields=["nomor_dokumen"]),
        ]
        verbose_name = "Dokumen"
        verbose_name_plural = "Dokumen"

    @property
    def download_url(self):
        return f"https://drive.google.com/uc?export=download&id={self.file_id}"

    @property
    def is_rahasia(self):
        return self.sifat == self.Sifat.RAHASIA

    def __str__(self):
        return f"{self.nomor_dokumen} - {self.judul}" if self.nomor_dokumen else self.judul

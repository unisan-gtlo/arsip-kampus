from django.contrib import admin

from .models import Dokumen, Kategori


@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ("nama_kategori",)
    search_fields = ("nama_kategori",)


@admin.register(Dokumen)
class DokumenAdmin(admin.ModelAdmin):
    list_display = ("nomor_dokumen", "judul", "kategori", "sifat", "tgl_upload", "uploaded_by")
    list_filter = ("kategori", "sifat")
    search_fields = ("judul", "nomor_dokumen", "deskripsi")

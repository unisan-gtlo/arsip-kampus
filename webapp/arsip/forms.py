from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import Dokumen, Kategori


class DokumenForm(forms.ModelForm):
    file = forms.FileField(
        label="File PDF",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "application/pdf"}),
        help_text="Wajib diisi saat menambah dokumen baru. Kosongkan saat edit jika file tidak diganti.",
    )

    class Meta:
        model = Dokumen
        fields = ["nomor_dokumen", "judul", "kategori", "deskripsi", "sifat"]
        widgets = {
            "nomor_dokumen": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "contoh: 003/SK-UNISNA/V/2025"}
            ),
            "judul": forms.TextInput(attrs={"class": "form-control"}),
            "kategori": forms.Select(attrs={"class": "form-select"}),
            "deskripsi": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "sifat": forms.RadioSelect,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["kategori"].queryset = Kategori.objects.all().order_by("nama_kategori")
        self.fields["kategori"].empty_label = None

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if not file.name.lower().endswith(".pdf"):
                raise ValidationError("File harus berformat PDF.")
            max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
            if file.size > max_bytes:
                raise ValidationError(f"Ukuran file maksimal {settings.MAX_UPLOAD_SIZE_MB}MB.")
        elif not self.instance.pk:
            raise ValidationError("File PDF wajib diunggah untuk dokumen baru.")
        return file


class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = ["nama_kategori"]
        widgets = {
            "nama_kategori": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "contoh: Peraturan, MOU, Berita Acara"}
            ),
        }

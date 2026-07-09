from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError

from .drive import parse_drive_link
from .models import Dokumen, Kategori


class DokumenForm(forms.ModelForm):
    SUMBER_UPLOAD = "upload"
    SUMBER_LINK = "link"

    sumber = forms.ChoiceField(
        label="Sumber File",
        choices=[(SUMBER_UPLOAD, "Upload File PDF"), (SUMBER_LINK, "Link Google Drive")],
        widget=forms.RadioSelect,
        initial=SUMBER_UPLOAD,
    )
    upload_file = forms.FileField(
        label="File PDF",
        required=False,
        widget=forms.ClearableFileInput(attrs={"class": "form-control", "accept": "application/pdf"}),
        help_text="Kosongkan saat edit jika file tidak diganti.",
    )
    drive_link = forms.CharField(
        label="Link Google Drive",
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "https://drive.google.com/file/d/xxxx/view?usp=sharing",
            }
        ),
        help_text="Pastikan link sudah diset ke “Anyone with the link” agar bisa diakses.",
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
        if self.instance.pk:
            self.fields["sumber"].initial = (
                self.SUMBER_LINK if self.instance.link_view else self.SUMBER_UPLOAD
            )

    def clean(self):
        cleaned = super().clean()
        sumber = cleaned.get("sumber")
        file = cleaned.get("upload_file")
        drive_link = (cleaned.get("drive_link") or "").strip()
        is_new = not self.instance.pk

        if sumber == self.SUMBER_UPLOAD:
            if file:
                if not file.name.lower().endswith(".pdf"):
                    self.add_error("upload_file", "File harus berformat PDF.")
                max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
                if file.size > max_bytes:
                    self.add_error(
                        "upload_file", f"Ukuran file maksimal {settings.MAX_UPLOAD_SIZE_MB}MB."
                    )
            elif is_new:
                self.add_error("upload_file", "File PDF wajib diunggah untuk dokumen baru.")
        elif sumber == self.SUMBER_LINK:
            if drive_link:
                file_id, _ = parse_drive_link(drive_link)
                if not file_id:
                    self.add_error("drive_link", "Format link Google Drive tidak valid.")
            elif is_new:
                self.add_error("drive_link", "Link Google Drive wajib diisi untuk dokumen baru.")

        return cleaned


class KategoriForm(forms.ModelForm):
    class Meta:
        model = Kategori
        fields = ["nama_kategori"]
        widgets = {
            "nama_kategori": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "contoh: Peraturan, MOU, Berita Acara"}
            ),
        }

from django.db.models import Q

# Each value is a tuple of order_by() fields, applied in sequence.
# "urutan" is the default: kategori's own display order first, then each
# document's manual position within that kategori - the same pattern used to
# arrange Kelola Kategori (Universitas -> Fakultas -> Prodi -> ...).
SORT_MAP = {
    "urutan": ("kategori__urutan", "kategori__nama_kategori", "urutan", "-tgl_upload"),
    "terbaru": ("-tgl_upload",),
    "terlama": ("tgl_upload",),
    "nomor_az": ("nomor_dokumen",),
    "nomor_za": ("-nomor_dokumen",),
}

SORT_LABELS = {
    "urutan": "Urutan",
    "terbaru": "Terbaru",
    "terlama": "Terlama",
    "nomor_az": "Nomor A-Z",
    "nomor_za": "Nomor Z-A",
}

# "berlaku" is the default: listing pages only show active documents unless
# the user explicitly asks to see draft/inactive/all ones via the status
# filter. Draft documents (still being prepared by the university's
# document drafting team) are hidden by default the same way.
STATUS_LABELS = {
    "berlaku": "Berlaku",
    "draf": "Draf",
    "tidak_berlaku": "Tidak Berlaku",
    "semua": "Semua",
}
STATUS_FIELD_VALUE = {
    "berlaku": "Berlaku",
    "draf": "Draf",
    "tidak_berlaku": "Tidak Berlaku",
}

PER_PAGE_CHOICES = [5, 10, 25, 50]


def filter_dokumen(qs, q="", kategori_id=None, sort="urutan", status="berlaku", search_deskripsi=True):
    """Shared search/filter/sort logic for public, portal, and dashboard listings.

    search_deskripsi=False mirrors the old dashboard behaviour, which only
    matched judul + nomor_dokumen (not deskripsi).
    status defaults to "berlaku" (active-only); pass "tidak_berlaku" or
    "semua" to see inactive/all documents.
    """
    if status in STATUS_FIELD_VALUE:
        qs = qs.filter(status=STATUS_FIELD_VALUE[status])
    if kategori_id:
        qs = qs.filter(kategori_id=kategori_id)
    if q:
        conditions = Q(judul__icontains=q) | Q(nomor_dokumen__icontains=q)
        if search_deskripsi:
            conditions |= Q(deskripsi__icontains=q)
        qs = qs.filter(conditions)
    return qs.order_by(*SORT_MAP.get(sort, SORT_MAP["urutan"]))


def get_per_page(request):
    try:
        value = int(request.GET.get("per_halaman", 10))
    except (TypeError, ValueError):
        value = 10
    return value if value in PER_PAGE_CHOICES else 10


def querystring_without_page(request):
    params = request.GET.copy()
    params.pop("page", None)
    encoded = params.urlencode()
    return f"&{encoded}" if encoded else ""

from django.db.models import Q

SORT_MAP = {
    "terbaru": "-tgl_upload",
    "terlama": "tgl_upload",
    "nomor_az": "nomor_dokumen",
    "nomor_za": "-nomor_dokumen",
}

SORT_LABELS = {
    "terbaru": "Terbaru",
    "terlama": "Terlama",
    "nomor_az": "Nomor A-Z",
    "nomor_za": "Nomor Z-A",
}

PER_PAGE_CHOICES = [5, 10, 25, 50]


def filter_dokumen(qs, q="", kategori_id=None, sort="terbaru", search_deskripsi=True):
    """Shared search/filter/sort logic for public, portal, and dashboard listings.

    search_deskripsi=False mirrors the old dashboard behaviour, which only
    matched judul + nomor_dokumen (not deskripsi).
    """
    if kategori_id:
        qs = qs.filter(kategori_id=kategori_id)
    if q:
        conditions = Q(judul__icontains=q) | Q(nomor_dokumen__icontains=q)
        if search_deskripsi:
            conditions |= Q(deskripsi__icontains=q)
        qs = qs.filter(conditions)
    return qs.order_by(SORT_MAP.get(sort, "-tgl_upload"))


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

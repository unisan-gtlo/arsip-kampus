import json

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import role_required

from .drive import parse_drive_link
from .forms import DokumenForm, KategoriForm
from .models import Dokumen, Kategori
from .services import (
    PER_PAGE_CHOICES,
    SORT_LABELS,
    filter_dokumen,
    get_per_page,
    querystring_without_page,
)


def _search_context(request, qs, *, search_deskripsi=True):
    q = request.GET.get("q", "").strip()
    kategori_id = request.GET.get("kategori", "").strip()
    sort = request.GET.get("sort", "terbaru")
    per_page = get_per_page(request)

    filtered = filter_dokumen(
        qs, q=q, kategori_id=kategori_id or None, sort=sort, search_deskripsi=search_deskripsi
    )
    paginator = Paginator(filtered, per_page)
    page_obj = paginator.get_page(request.GET.get("page"))

    return {
        "page_obj": page_obj,
        "paginator": paginator,
        "kategori_list": Kategori.objects.all(),
        "q": q,
        "kategori_id": kategori_id,
        "sort": sort,
        "sort_labels": SORT_LABELS,
        "per_page": per_page,
        "per_page_choices": PER_PAGE_CHOICES,
        "querystring": querystring_without_page(request),
        "total_data": paginator.count,
    }


def public_search(request):
    qs = Dokumen.objects.exclude(sifat=Dokumen.Sifat.RAHASIA)
    context = _search_context(request, qs, search_deskripsi=True)
    return render(request, "arsip/public_search.html", context)


@login_required(login_url="accounts:login")
def portal_search(request):
    qs = Dokumen.objects.all()
    context = _search_context(request, qs, search_deskripsi=True)
    return render(request, "arsip/portal_search.html", context)


@login_required(login_url="accounts:login")
def home(request):
    return render(request, "arsip/home.html")


@role_required(User.Role.ADMIN, User.Role.OPERATOR)
def dashboard(request):
    qs = Dokumen.objects.all()
    context = _search_context(request, qs, search_deskripsi=False)

    total_dokumen = Dokumen.objects.count()
    kategori_terbanyak_row = (
        Dokumen.objects.values("kategori__nama_kategori")
        .annotate(n=Count("id"))
        .order_by("-n")
        .first()
    )
    kategori_terbanyak = (
        kategori_terbanyak_row["kategori__nama_kategori"] if kategori_terbanyak_row else "-"
    )
    jumlah_kategori = Dokumen.objects.values("kategori").distinct().count()

    context.update(
        {
            "total_dokumen": total_dokumen,
            "kategori_terbanyak": kategori_terbanyak,
            "jumlah_kategori": jumlah_kategori,
        }
    )
    return render(request, "arsip/dashboard.html", context)


@role_required(User.Role.ADMIN, User.Role.OPERATOR)
def dokumen_upload(request):
    kategori_qs = Kategori.objects.all()
    if not kategori_qs.exists():
        messages.warning(request, "Belum ada kategori. Minta admin menambahkan kategori terlebih dahulu.")
        return redirect("arsip:dashboard")

    nomor_per_kategori = {}
    for kat in kategori_qs:
        last_doc = (
            Dokumen.objects.filter(kategori=kat)
            .exclude(nomor_dokumen="")
            .order_by("tgl_upload")
            .last()
        )
        if last_doc:
            nomor_per_kategori[str(kat.id)] = last_doc.nomor_dokumen

    if request.method == "POST":
        form = DokumenForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            _apply_sumber(doc, form)
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, f"Dokumen '{doc.judul}' berhasil disimpan!")
            return redirect("arsip:dokumen_upload")
    else:
        form = DokumenForm()

    return render(
        request,
        "arsip/dokumen_form.html",
        {
            "form": form,
            "is_edit": False,
            "nomor_per_kategori_json": json.dumps(nomor_per_kategori),
        },
    )


@role_required(User.Role.ADMIN, User.Role.OPERATOR)
def dokumen_edit(request, pk):
    doc = get_object_or_404(Dokumen, pk=pk)

    if request.method == "POST":
        form = DokumenForm(request.POST, request.FILES, instance=doc)
        if form.is_valid():
            updated = form.save(commit=False)
            _apply_sumber(updated, form)
            updated.save()
            messages.success(request, "Dokumen berhasil diperbarui!")
            return redirect("arsip:dashboard")
    else:
        form = DokumenForm(instance=doc)

    return render(
        request,
        "arsip/dokumen_form.html",
        {"form": form, "is_edit": True, "dokumen": doc},
    )


def _apply_sumber(doc, form):
    """Set doc.file / file_id+link_view from whichever source the form picked,
    clearing out the other one so a document is never in a mixed state."""
    sumber = form.cleaned_data["sumber"]
    if sumber == DokumenForm.SUMBER_UPLOAD:
        file = form.cleaned_data.get("upload_file")
        if file:
            if doc.file:
                doc.file.delete(save=False)
            doc.file = file
            doc.file_id = ""
            doc.link_view = ""
    elif sumber == DokumenForm.SUMBER_LINK:
        drive_link = (form.cleaned_data.get("drive_link") or "").strip()
        if drive_link:
            file_id, link_view = parse_drive_link(drive_link)
            if doc.file:
                doc.file.delete(save=False)
            doc.file = None
            doc.file_id = file_id
            doc.link_view = link_view


@require_POST
@role_required(User.Role.ADMIN)
def dokumen_delete(request, pk):
    doc = get_object_or_404(Dokumen, pk=pk)
    if doc.file:
        doc.file.delete(save=False)
    judul = doc.judul
    doc.delete()
    messages.success(request, f"Dokumen '{judul}' berhasil dihapus.")
    return redirect("arsip:dashboard")


def _check_dokumen_access(request, doc):
    if doc.is_rahasia and not request.user.is_authenticated:
        raise PermissionDenied("Dokumen ini hanya dapat diakses oleh pengguna yang login.")


def dokumen_file(request, pk):
    """Serves the preview (inline). Access-gated the same way for both
    locally-stored files and Drive-link files, unlike the old Drive-API
    upload path which made every uploaded file public via "anyone with
    the link" regardless of sifat."""
    doc = get_object_or_404(Dokumen, pk=pk)
    _check_dokumen_access(request, doc)
    if doc.file:
        return FileResponse(doc.file.open("rb"), content_type="application/pdf")
    if doc.link_view:
        return redirect(doc.link_view)
    raise Http404


def dokumen_download(request, pk):
    doc = get_object_or_404(Dokumen, pk=pk)
    _check_dokumen_access(request, doc)
    if doc.file:
        return FileResponse(
            doc.file.open("rb"), as_attachment=True, filename=doc.file.name.rsplit("/", 1)[-1]
        )
    if doc.file_id:
        return redirect(f"https://drive.google.com/uc?export=download&id={doc.file_id}")
    raise Http404


@role_required(User.Role.ADMIN)
def kategori_list(request):
    kategori_qs = Kategori.objects.all()
    return render(
        request,
        "arsip/kategori_list.html",
        {"kategori_list": kategori_qs, "form": KategoriForm()},
    )


@role_required(User.Role.ADMIN)
def kategori_add(request):
    if request.method == "POST":
        form = KategoriForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Kategori '{form.instance.nama_kategori}' berhasil ditambahkan!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect("arsip:kategori_list")


@role_required(User.Role.ADMIN)
def kategori_edit(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    if request.method == "POST":
        form = KategoriForm(request.POST, instance=kategori)
        if form.is_valid():
            form.save()
            messages.success(request, f"Kategori berhasil diubah menjadi '{kategori.nama_kategori}'!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    return redirect("arsip:kategori_list")


@require_POST
@role_required(User.Role.ADMIN)
def kategori_delete(request, pk):
    kategori = get_object_or_404(Kategori, pk=pk)
    nama = kategori.nama_kategori
    if kategori.dokumen.exists():
        messages.error(
            request,
            f"Kategori '{nama}' tidak dapat dihapus karena masih dipakai oleh dokumen yang ada.",
        )
    else:
        kategori.delete()
        messages.success(request, f"Kategori '{nama}' berhasil dihapus.")
    return redirect("arsip:kategori_list")

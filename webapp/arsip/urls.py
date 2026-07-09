from django.urls import path

from . import views

app_name = "arsip"

urlpatterns = [
    path("", views.home, name="home"),
    path("publik/", views.public_search, name="public_search"),
    path("portal/", views.portal_search, name="portal_search"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dokumen/upload/", views.dokumen_upload, name="dokumen_upload"),
    path("dokumen/<int:pk>/edit/", views.dokumen_edit, name="dokumen_edit"),
    path("dokumen/<int:pk>/delete/", views.dokumen_delete, name="dokumen_delete"),
    path("dokumen/<int:pk>/file/", views.dokumen_file, name="dokumen_file"),
    path("dokumen/<int:pk>/download/", views.dokumen_download, name="dokumen_download"),
    path("kategori/", views.kategori_list, name="kategori_list"),
    path("kategori/add/", views.kategori_add, name="kategori_add"),
    path("kategori/<int:pk>/edit/", views.kategori_edit, name="kategori_edit"),
    path("kategori/<int:pk>/delete/", views.kategori_delete, name="kategori_delete"),
]

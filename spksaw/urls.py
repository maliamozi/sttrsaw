from django.contrib import admin
from django.urls import path
from . import views 
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path("home/", views.home, name="home"),  # Halaman utama untuk non-staff
    path("",views.home, name="home"),

    path("bidang/",views.bidang, name="bidang"),
    path("bidang/tambah-bidang/",views.tambah_bidang, name="tambah_bidang"), #name utk memanggil template, views.tambah_bidang diambil dari views.py setelah def
    path("bidang/edit-bidang/<int:id>/",views.edit_bidang, name="edit_bidang"),   
    path("bidang/hapus-bidang/<int:id>/",views.delete_bidang, name="delete_bidang"),

    path("pegawai/", views.pegawai, name="pegawai"),
    path("pegawai/tambah-pegawai/", views.tambah_pegawai, name="tambah_pegawai"),
    path('pegawai/edit/<int:id>/', views.edit_pegawai, name='edit_pegawai'),
    path('pegawai/hapus/<int:id>/', views.hapus_pegawai, name='hapus_pegawai'),
    
    path("kriteria/", views.kriteria, name="kriteria"),
    path("kriteria/tambah-kriteria/", views.tambah_kriteria, name="tambah_kriteria"),
    path('kriteria/edit/<int:id>/', views.edit_kriteria, name='edit_kriteria'),
    path('kriteria/hapus/<int:id>/', views.delete_kriteria, name='delete_kriteria'),
    path('kriteria/<int:kriteria_id>/input-bobot/', views.input_bobot, name='input_bobot'),

    path("penilaian/", views.penilaian, name="penilaian"),
    path("penilaian/input-nilai/<int:id>/", views.input_nilai, name="input_nilai"),
    path("penilaian/lihat-nilai/<int:penilaian_id>/", views.lihat_nilai, name="lihat_nilai"),
    path("penilaian/edit-nilai/<int:id>/", views.edit_nilai, name="edit_nilai"),

    path("penilaian/pegawai_terbaik/",views.pegawai_terbaik, name="pegawai_terbaik"),

    path("riwayat/", views.riwayat, name="riwayat"),
    path('unduh-pdf/', views.unduh_pdf, name='unduh_pdf'),

    path("user/",views.user, name="user"),
    path("user/tambah-user/",views.tambah_user, name="tambah_user"),
    path("user/edit/<int:id>/", views.edit_user, name="edit_user"),
    path("user/delete/<int:id>/", views.delete_user, name="delete_user"),

   
    path("login/", views.login, name="login"),
    path("logout/", LogoutView.as_view(next_page="login"), name="logout"),
]

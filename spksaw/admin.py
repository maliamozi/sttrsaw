from django.contrib import admin
from .models import Bidang, Pegawai, Kriteria, Penilaian, PegawaiTerbaik, RiwayatPenilaian

admin.site.register(Pegawai)
admin.site.register(Bidang)
admin.site.register(Kriteria)
admin.site.register(Penilaian)
admin.site.register(PegawaiTerbaik)
admin.site.register(RiwayatPenilaian)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Bidang, Pegawai, Kriteria, Penilaian, PegawaiTerbaik, RiwayatPenilaian
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models import Max, Min
from django.db.models import Q
import logging
import json
import ast  # Untuk parsing string dictionary

from django.http import HttpResponse
from reportlab.pdfgen import canvas
from io import BytesIO

logger = logging.getLogger(__name__)  # Logger untuk debugging

def home(request): 
    return render(request, 'home.html')

def bidang(request): 
    bidangs = Bidang.objects.all()
    return render(request, 'bidang.html',{'bidangs': bidangs})

def tambah_bidang(request):
    if request.method == "POST":
        # Ambil data dari input form
        nama = request.POST.get('nama_bidang')  # Ambil input dari field form
        if nama:  # Validasi: jika nama tidak kosong
            Bidang.objects.create(nama_bidang=nama)  # Simpan ke database
            messages.success(request, "Data bidang berhasil disimpan.")  # Pesan sukses
            return redirect('bidang')  # Redirect ke halaman daftar bidang
        else:
            messages.error(request, "Nama bidang tidak boleh kosong.")  # Pesan error
            # Tidak redirect agar tetap di halaman tambah bidang
    return render(request, 'tambahbidang.html')

#fungsi edit bidang
def edit_bidang(request, id):
    bidang = get_object_or_404(Bidang, id=id)
    if request.method == 'POST':
        bidang.nama_bidang = request.POST.get('nama', bidang.nama_bidang)
        bidang.save()
        messages.success(request, 'Bidang berhasil diubah')
        return redirect('bidang') # kembali ke halaman tabel
    return render(request, 'edit_bidang.html', {'bidang': bidang})

#fungsi Hapus Bidang
def delete_bidang(request, id):
    bidang = get_object_or_404(Bidang, id=id)
    if request.method == 'POST' :
        bidang.delete()
        messages.success(request, 'Bidang berhasil dihapus!')
        return redirect ('bidang') # kembali ke halaman tabel


def pegawai(request):
    # Ambil semua data Pegawai
    pegawai_list = Pegawai.objects.select_related('bidang').all()  # Optimalkan dengan select_related
    return render(request, 'pegawai.html', {'pegawai_list': pegawai_list})

# fungsi tambah pegawai
def tambah_pegawai(request):
    if request.method == "POST":
        nomor_induk = request.POST.get('nomor_induk')
        nama_pegawai = request.POST.get('nama_pegawai')
        alamat = request.POST.get('alamat')
        no_hp = request.POST.get('no_hp')
        bidang_id = request.POST.get('pilih_bidang')  # ID bidang dari dropdown

        try:
            # Validasi apakah bidang ada
            bidang = Bidang.objects.get(id=bidang_id)  # Cari bidang berdasarkan ID
            
            # Simpan data ke model Pegawai
            pegawai = Pegawai.objects.create(
                nomor_induk=nomor_induk,
                nama=nama_pegawai,
                alamat=alamat,
                no_telp=no_hp,
                bidang=bidang
            )
            
            # Simpan data ke model Penilaian
            Penilaian.objects.create(
                nama=pegawai,  # Relasi ke instance Pegawai yang baru dibuat
                bidang=bidang,  # Relasi ke instance Bidang yang sudah ada
                nilai=None  # Nilai default untuk kolom nilai
            )

            # Tampilkan pesan berhasil
            messages.success(request, "Pegawai berhasil ditambahkan.")
            return redirect('pegawai')  # Redirect ke halaman daftar pegawai

        except Bidang.DoesNotExist:
            # Jika bidang tidak ditemukan
            messages.error(request, "Bidang tidak ditemukan.")
        except Exception as e:
            # Jika terjadi error lainnya
            messages.error(request, f"Terjadi kesalahan: {str(e)}")

    # Ambil data bidang untuk dropdown pada form
    bidang_list = Bidang.objects.all()
    return render(request, 'tambah_pegawai.html', {'bidang_list': bidang_list})


def edit_pegawai(request, id):
    # Ambil data pegawai berdasarkan ID
    pegawai = get_object_or_404(Pegawai, id=id)
    
    if request.method == "POST":
        # Ambil data dari form
        nomor_induk = request.POST.get('nomor_induk')
        nama_pegawai = request.POST.get('nama_pegawai')
        alamat = request.POST.get('alamat')
        no_hp = request.POST.get('no_hp')
        bidang_id = request.POST.get('pilih_bidang')

        # Validasi input
        if not nomor_induk or not nama_pegawai or not alamat or not no_hp or not bidang_id:
            messages.error(request, "Semua field wajib diisi.")
            return redirect('edit_pegawai', id=id)

        try:
            # Ambil bidang berdasarkan ID
            bidang = Bidang.objects.get(id=bidang_id)

            # Perbarui data pegawai
            pegawai.nomor_induk = nomor_induk
            pegawai.nama = nama_pegawai
            pegawai.alamat = alamat
            pegawai.no_telp = no_hp
            pegawai.bidang = bidang
            pegawai.save()

            messages.success(request, "Data pegawai berhasil diperbarui.")
            return redirect('pegawai')  # Ganti dengan nama URL untuk daftar pegawai
        except Bidang.DoesNotExist:
            messages.error(request, "Bidang tidak ditemukan.")
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {e}")

    # Ambil daftar bidang untuk dropdown
    bidang_list = Bidang.objects.all()
    return render(request, 'edit_pegawai.html', {'pegawai': pegawai, 'bidang_list': bidang_list})

def hapus_pegawai(request, id):
    try:
        # Ambil data pegawai berdasarkan ID
        pegawai = get_object_or_404(Pegawai, id=id)
        
        # Hapus data pegawai
        pegawai.delete()
        
        # Berikan pesan sukses
        messages.success(request, "Data pegawai berhasil dihapus.")
    except Exception as e:
        # Berikan pesan error jika terjadi masalah
        messages.error(request, f"Terjadi kesalahan: {e}")

    # Redirect ke halaman daftar pegawai
    return redirect('pegawai')  # Ganti dengan nama URL untuk daftar pegawai

def kriteria(request):
    # Mengambil semua data kriteria dari database
    daftar_kriteria = Kriteria.objects.all()
    # Mengirimkan data ke template
    return render(request, 'kriteria.html', {'daftar_kriteria': daftar_kriteria})

def tambah_kriteria(request):
    if request.method == "POST":
        nama = request.POST.get('kriteria')  # Mengambil data nama kriteria dari form
        tipe_kriteria = request.POST.get('tipe_kriteria')  # Mengambil tipe kriteria dari form

        # Validasi input jika diperlukan (optional)
        if nama and tipe_kriteria:
            # Simpan data ke database
            Kriteria.objects.create(
                nama=nama,
                tipe_kriteria=tipe_kriteria,
                bobot=0  # Default bobot tetap 0
            )
            messages.success(request, "Data kriteria berhasil ditambahkan.")
            return redirect('kriteria')  # Redirect setelah berhasil menambahkan data

    return render(request, 'tambahkriteria.html')

def edit_kriteria(request, id):
    # Ambil data kriteria berdasarkan ID
    kriteria = get_object_or_404(Kriteria, id=id)

    if request.method == "POST":
        # Ambil data dari formulir
        nama = request.POST.get('nama')
        tipe_kriteria = request.POST.get('tipe_kriteria')

        # Perbarui data kriteria
        kriteria.nama = nama
        kriteria.tipe_kriteria = tipe_kriteria
        kriteria.save()  # Simpan perubahan ke database
        messages.success(request, "Data kriteria berhasil diperbarui.")

        # Redirect ke halaman lain (misalnya daftar kriteria)
        return redirect('kriteria')  # Ganti 'kriteria' dengan nama URL daftar kriteria Anda

    # Kirim data kriteria ke template
    return render(request, 'edit_kriteria.html', {'kriteria': kriteria})
def delete_kriteria(request, id):
    kriteria = get_object_or_404(Kriteria, id=id)
    if request.method == 'POST' :
        kriteria.delete()
        messages.success(request, 'kriteria berhasil dihapus!')
        return redirect ('kriteria') # kembali ke halaman tabel

# fungsi input bobot
def input_bobot(request, kriteria_id):
    # Ambil kriteria berdasarkan ID
    kriteria = get_object_or_404(Kriteria, id=kriteria_id)

    if request.method == "POST":
        try:
            bobot_baru = float(request.POST.get('bobot', 0))  # Ambil bobot baru dari form
            total_bobot_sekarang = Kriteria.objects.exclude(id=kriteria.id).aggregate(total=Sum('bobot'))['total'] or 0

            # Hitung total bobot jika bobot baru ditambahkan
            total_bobot_setelah_input = total_bobot_sekarang + bobot_baru

            if total_bobot_setelah_input > 100:
                # Jika total bobot melebihi 100, tampilkan pesan error
                messages.error(
                    request, 
                    f"Bobot yang Anda masukkan melebihi batas. Maksimal yang bisa ditambahkan adalah {100 - total_bobot_sekarang:.2f}%."
                )
            else:
                # Simpan bobot baru ke kriteria yang sudah ada
                kriteria.bobot = bobot_baru
                kriteria.save()

                messages.success(request, f"Bobot untuk {kriteria.nama} berhasil diperbarui.")
                return redirect('kriteria')  # Ganti dengan URL yang sesuai
        except ValueError:
            messages.error(request, "Bobot harus berupa angka yang valid.")
    
    # Data untuk ditampilkan di template
    total_bobot_sekarang = Kriteria.objects.exclude(id=kriteria.id).aggregate(total=Sum('bobot'))['total'] or 0
    context = {
        'kriteria': kriteria,
        'total_bobot_sekarang': total_bobot_sekarang,
        'bobot_maksimal': 100 - total_bobot_sekarang,
    }
    return render(request, 'bobot_kriteria.html', context)

# mengarahkan ke halaman kelola penilaian
def penilaian(request): 
    # ambil semua data dari model penilaian
    penilaian_list = Penilaian.objects.all()
    return render(request, 'penilaian.html', {'penilaian_list' : penilaian_list})

def input_nilai(request, id):
    penilaian = get_object_or_404(Penilaian, id=id)  # Ambil data Penilaian berdasarkan ID
    kriteria_list = Kriteria.objects.all()          # Ambil semua kriteria
    
    if request.method == 'POST':
        # Ambil nilai dari form input
        nilai_dict = {}
        for kriteria in kriteria_list:
            nilai = request.POST.get(kriteria.nama)
            if nilai:
                nilai_dict[kriteria.nama] = int(nilai)  # Pastikan nilai berupa integer
        
        # Simpan data ke kolom nilai dalam format JSON
        penilaian.nilai = json.dumps(nilai_dict)
        penilaian.save()

        # Redirect setelah berhasil menyimpan
        return redirect('penilaian')  # Ganti dengan nama URL untuk halaman daftar penilaian

    context = {
        'penilaian': penilaian,
        'kriteria_list': kriteria_list,
    }
    messages.success(request, "Nilai berhasil diinput.")
    return render(request, 'input_nilai.html', context)

def lihat_nilai(request, penilaian_id):
    # Ambil data penilaian berdasarkan ID
    penilaian = get_object_or_404(Penilaian, id=penilaian_id)

    # Parsing kolom nilai dari string ke dictionary
    try:
        nilai_dict = ast.literal_eval(penilaian.nilai) if penilaian.nilai else {}
    except Exception:
        nilai_dict = {}

    context = {
        'penilaian': penilaian,
        'nilai_dict': nilai_dict,
    }
    return render(request, 'lihat_nilai.html', context)

def tambah_kriteria(request):
    if request.method == "POST":
        # Ambil data dari input form
        nama_kriteria = request.POST.get('nama_kriteria')
        tipe_kriteria = request.POST.get('tipe_kriteria')  # Ambil tipe kriteria dari form

        if nama_kriteria and tipe_kriteria:  # Validasi jika nama_kriteria dan tipe_kriteria tidak kosong
            # Buat objek Kriteria dan simpan ke database
            kriteria = Kriteria.objects.create(nama=nama_kriteria, tipe=tipe_kriteria)
            
            # Update kolom nilai di semua Penilaian
            penilaian_list = Penilaian.objects.all()
            for penilaian in penilaian_list:
                if penilaian.nilai:  # Cek jika kolom nilai tidak kosong
                    # Load nilai dari JSON
                    nilai_dict = json.loads(penilaian.nilai)
                    # Tambahkan kriteria baru dengan nilai default 0
                    nilai_dict[kriteria.nama] = 0
                    # Simpan kembali ke database
                    penilaian.nilai = json.dumps(nilai_dict)
                    penilaian.save()

            # Tambahkan pesan sukses
            messages.success(request, "Kriteria berhasil ditambahkan!")
            # Redirect ke halaman daftar kriteria
            return redirect('kriteria')

        else:
            # Tambahkan pesan error jika input kosong
            messages.error(request, "Nama kriteria dan tipe kriteria tidak boleh kosong.")
            return redirect('tambah_kriteria')

    return render(request, 'tambahkriteria.html')

def edit_kriteria(request, id):
    kriteria = get_object_or_404(Kriteria, id=id)
    if request.method == 'POST':
        # Ambil data dari form
        nama_kriteria_baru = request.POST.get('nama', kriteria.nama)
        tipe_kriteria = request.POST.get('tipe', kriteria.tipe)

        # Validasi tipe kriteria
        if tipe_kriteria not in ['benefit', 'cost']:
            messages.error(request, "Tipe kriteria tidak valid.")
            return redirect('edit_kriteria', id=id)

        # Jika nama kriteria diubah, update kolom nilai pada Penilaian
        if nama_kriteria_baru != kriteria.nama:
            penilaian_list = Penilaian.objects.all()
            for penilaian in penilaian_list:
                if penilaian.nilai:  # Pastikan kolom nilai tidak kosong
                    nilai_dict = json.loads(penilaian.nilai)  # Parse JSON ke dictionary
                    if kriteria.nama in nilai_dict:  # Cek apakah kriteria ada di nilai
                        nilai_dict[nama_kriteria_baru] = nilai_dict.pop(kriteria.nama)  # Ganti nama kriteria
                        penilaian.nilai = json.dumps(nilai_dict)  # Simpan kembali dalam format JSON
                        penilaian.save()

        # Simpan perubahan pada model Kriteria
        kriteria.nama = nama_kriteria_baru
        kriteria.tipe = tipe_kriteria
        kriteria.save()
        
        messages.success(request, 'Kriteria berhasil diubah!')
        return redirect('kriteria')  # Kembali ke halaman tabel

    # Data untuk template
    return render(request, 'edit_kriteria.html', {'kriteria': kriteria})

def delete_kriteria(request, id):
    kriteria = get_object_or_404(Kriteria, id=id)
    if request.method == 'POST':
        penilaian_list = Penilaian.objects.all()

        # Hapus kriteria dari kolom nilai pada setiap Penilaian
        for penilaian in penilaian_list:
            if penilaian.nilai:  # Pastikan kolom nilai tidak kosong
                nilai_dict = json.loads(penilaian.nilai)  # Parse JSON ke dictionary
                if kriteria.nama in nilai_dict:  # Cek apakah kriteria ada di nilai
                    del nilai_dict[kriteria.nama]  # Hapus kriteria dari dictionary
                    penilaian.nilai = json.dumps(nilai_dict)  # Simpan kembali dalam format JSON
                    penilaian.save()

        # Hapus kriteria dari database
        kriteria.delete()
        messages.success(request, 'Kriteria berhasil dihapus!')
        return redirect('kriteria')  # Kembali ke halaman tabel

    # Data untuk konfirmasi penghapusan
    return render(request, 'delete_kriteria.html', {'kriteria': kriteria})

def edit_nilai(request, id):
    # Ambil data penilaian berdasarkan ID
    penilaian = get_object_or_404(Penilaian, id=id)

    # Ambil daftar kriteria
    kriteria_list = Kriteria.objects.all()

    # Muat nilai dari kolom nilai (format JSON) jika tidak kosong
    nilai_dict = json.loads(penilaian.nilai) if penilaian.nilai else {}

    # Buat pasangan (kriteria, nilai) untuk akses lebih mudah di template
    nilai_data = [(kriteria.nama, nilai_dict.get(kriteria.nama, '')) for kriteria in kriteria_list]

    if request.method == "POST":
        try:
            # Perbarui nilai berdasarkan input dari form
            for kriteria in kriteria_list:
                nilai_input = request.POST.get(kriteria.nama)
                if nilai_input:
                    nilai_dict[kriteria.nama] = int(nilai_input)  # Simpan nilai sebagai integer
            
            # Simpan kembali nilai ke database
            penilaian.nilai = json.dumps(nilai_dict)
            penilaian.save()

            messages.success(request, "Nilai berhasil diperbarui!")
            return redirect('lihat_nilai', penilaian.id)

        except Exception as e:
            messages.error(request, f"Terjadi kesalahan: {str(e)}")

    context = {
        'penilaian': penilaian,
        'nilai_data': nilai_data,  # Data (kriteria, nilai)
    }
    return render(request, 'editnilai.html', context)

def pegawai_terbaik(request):
    pegawai_terbaik_list = []
    error = None  # Untuk menampung pesan kesalahan
    if request.method == "POST":
        tahun_nilai = request.POST.get("tahun_nilai")

        # Validasi total bobot kriteria
        total_bobot = Kriteria.objects.aggregate(Sum('bobot'))['bobot__sum'] or 0
        if total_bobot != 100:
            error = "Bobot kriteria belum mencapai 100%. Harap lengkapi bobot kriteria."
        else:
            # Validasi penilaian
            penilaian_list = Penilaian.objects.all()
            if not penilaian_list.exists():
                error = "Penilaian belum diisi. Harap lengkapi penilaian."
            else:
                # Perhitungan normalisasi dan preferensi
                for penilaian in penilaian_list:
                    nilai_dict = json.loads(penilaian.nilai or "{}")  # Decode nilai JSON
                    normalisasi_dict = {}
                    nilai_preferensi = 0

                    # Normalisasi nilai berdasarkan tipe kriteria
                    for kriteria in Kriteria.objects.all():
                        nama_kriteria = kriteria.nama
                        tipe = kriteria.tipe
                        bobot = kriteria.bobot / 100  # Bobot dalam skala 0-1

                        # Ambil nilai dari dictionary
                        nilai = nilai_dict.get(nama_kriteria, 0)

                        # Normalisasi berdasarkan tipe kriteria
                        if tipe == 'benefit':
                            max_value = max(
                                float(json.loads(pen.nilai or "{}").get(nama_kriteria, 0))
                                for pen in penilaian_list
                            )
                            normalisasi = nilai / max_value if max_value else 0
                        elif tipe == 'cost':
                            min_value = min(
                                float(json.loads(pen.nilai or "{}").get(nama_kriteria, 0))
                                for pen in penilaian_list
                            )
                            normalisasi = min_value / nilai if nilai else 0

                        # Simpan hasil normalisasi
                        normalisasi_dict[nama_kriteria] = normalisasi

                        # Hitung nilai preferensi
                        nilai_preferensi += normalisasi * bobot

                    # Tambahkan ke daftar pegawai terbaik
                    pegawai_terbaik_list.append({
                        'nama': penilaian.nama.nama,
                        'bidang': penilaian.bidang.nama_bidang,
                        'normalisasi': normalisasi_dict,
                        'preferensi': nilai_preferensi
                    })

                    # **Simpan data ke RiwayatPenilaian sebelum mereset nilai**
                    RiwayatPenilaian.objects.create(
                        nama=penilaian.nama,
                        bidang=penilaian.bidang,
                        nilai=penilaian.nilai,  # Nilai disimpan dalam format JSON
                        tahun_penilaian=tahun_nilai
                    )

                    # Reset nilai ke default (kosongkan kolom nilai)
                    penilaian.nilai = ""
                    penilaian.save()

                # Urutkan berdasarkan nilai preferensi (descending) dan ambil 10 besar
                pegawai_terbaik_list.sort(key=lambda x: x['preferensi'], reverse=True)
                pegawai_terbaik_list = pegawai_terbaik_list[:10]

                # Simpan hasil ke database PegawaiTerbaik
                PegawaiTerbaik.objects.filter(tahun_penilaian=tahun_nilai).delete()  # Hapus data lama untuk tahun yang sama
                for pegawai in pegawai_terbaik_list:
                    PegawaiTerbaik.objects.create(
                        nama=pegawai['nama'],
                        bidang=pegawai['bidang'],
                        normalisasi_nilai=json.dumps(pegawai['normalisasi']),
                        nilai_preferensi=pegawai['preferensi'],
                        tahun_penilaian=tahun_nilai
                    )

    # Kirimkan data atau error ke template
    return render(request, 'pegawaiterbaik.html', {
        'pegawai_terbaik': pegawai_terbaik_list,
        'error': error
    })


def riwayat(request):
    tahun_penilaian_list = PegawaiTerbaik.objects.values_list('tahun_penilaian', flat=True).distinct().order_by('tahun_penilaian')
    data_tabel = None
    selected_riwayat = request.POST.get('riwayat')
    selected_tahun = request.POST.get('tahun_penilaian')

    if selected_riwayat and selected_tahun:
        if selected_riwayat == "riwayat_penilaian":
            # Ambil data dari model RiwayatPenilaian berdasarkan tahun
            data_tabel = RiwayatPenilaian.objects.filter(tahun_penilaian=selected_tahun)
        elif selected_riwayat == "pegawai_terbaik":
            # Ambil data dari model PegawaiTerbaik berdasarkan tahun
            data_tabel = PegawaiTerbaik.objects.filter(tahun_penilaian=selected_tahun)

    return render(request, 'riwayat.html', {
        'tahun_penilaian_list': tahun_penilaian_list,
        'data_tabel': data_tabel,
        'selected_riwayat': selected_riwayat,
        'selected_tahun': selected_tahun,
    })

def user(request): 
    pegawai_list = User.objects.all()  # Ambil semua data user
    context = {
        'pegawai_list': pegawai_list,  # Kirim data ke template
    }
    return render(request, 'user.html', context)

# fungsi tambah user
def tambah_user(request):
    if request.method == "POST":
        # Ambil data dari form
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        # Validasi input
        if password != password2:
            messages.error(
                request, "Password dan Konfirmasi Password tidak cocok.")
            return redirect('tambah_user')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username sudah digunakan.")
            return redirect('tambah_user')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email sudah terdaftar.")
            return redirect('tambah_user')

        # Simpan data user ke database
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=nama_depan,
            last_name=nama_belakang
        )
        user.save()
        messages.success(request, "User berhasil ditambahkan!")
        return redirect('user')  # Ubah sesuai kebutuhan

    # Jika request bukan POST, kembalikan halaman form
    return render(request, 'tambahuser.html')

def edit_user(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        user.first_name = request.POST.get('nama_depan')
        user.last_name = request.POST.get('nama_belakang')
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        if request.POST.get('password'):
            user.set_password(request.POST.get('password'))
        user.save()
        messages.success(request, "User berhasil diperbarui!")
        return redirect('user')
    
    context = {'user': user}
    return render(request, 'edituser.html', context)

def delete_user(request, id):
    user = User.objects.get(id=id)
    user.delete()
    messages.success(request, "User berhasil dihapus!")
    return redirect('user')


def login(request):  
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        #login berhasil 
        if user is not None:
            auth_login(request, user)
            return redirect ('home')
        else:
            # Login gagal
            messages.error(request, "Username atau password salah.")
            return redirect('login')
        
    return render(request, 'login.html')



def unduh_pdf(request):
    if request.method == 'POST':
        selected_riwayat = request.POST.get('riwayat')
        selected_tahun = request.POST.get('tahun_penilaian')

        if not (selected_riwayat and selected_tahun):
            return HttpResponse("Data tidak valid", status=400)

        # Ambil data sesuai riwayat yang dipilih
        if selected_riwayat == "riwayat_penilaian":
            data_tabel = RiwayatPenilaian.objects.filter(tahun_penilaian=selected_tahun)
        elif selected_riwayat == "pegawai_terbaik":
            data_tabel = PegawaiTerbaik.objects.filter(tahun_penilaian=selected_tahun)
        else:
            return HttpResponse("Pilihan riwayat tidak valid", status=400)

        # Buat PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{selected_riwayat}_{selected_tahun}.pdf"'

        buffer = BytesIO()
        p = canvas.Canvas(buffer)

        # Judul
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, f"Data {selected_riwayat.replace('_', ' ').title()} Tahun {selected_tahun}")

        # Header tabel
        y_position = 760
        p.setFont("Helvetica-Bold", 12)
        headers = ["No", "Nama", "Bidang"]
        if selected_riwayat == "riwayat_penilaian":
            headers.append("Nilai")
        else:
            headers.append("Nilai Preferensi")
        headers.append("Tahun Penilaian")
        for i, header in enumerate(headers):
            p.drawString(50 + (150 * i), y_position, header)

        # Isi tabel
        y_position -= 20
        p.setFont("Helvetica", 10)
        for index, item in enumerate(data_tabel, start=1):
            p.drawString(50, y_position, str(index))
            if selected_riwayat == "riwayat_penilaian":
                p.drawString(200, y_position, item.nama.nama)
                p.drawString(350, y_position, item.bidang.nama_bidang)
                p.drawString(500, y_position, item.nilai)
            else:
                p.drawString(200, y_position, item.nama)
                p.drawString(350, y_position, item.bidang)
                p.drawString(500, y_position, f"{item.nilai_preferensi:.2f}")
            p.drawString(650, y_position, str(item.tahun_penilaian))
            y_position -= 20

        p.save()
        buffer.seek(0)
        response.write(buffer.getvalue())
        buffer.close()

        return response

    return HttpResponse("Metode tidak valid", status=405)




def laporan_view(request):
    # Data Anda
    data_tabel = [...]  # Ganti dengan data sebenarnya
    logo_url = request.build_absolute_uri('/static/images/logo.png')  # Ganti path logo sesuai lokasi Anda

    return render(request, 'laporan.html', {
        'riwayat': 'riwayat_penilaian',
        'tahun': 2023,
        'data_tabel': data_tabel,
        'logo_url': logo_url,
    })


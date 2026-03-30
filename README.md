# PayrollFace - Sistem Absensi & Payroll Berbasis Face Recognition

Sistem informasi absensi dan payroll yang mengintegrasikan verifikasi biometrik wajah untuk memastikan kehadiran karyawan yang akurat dan aman.

## Fitur Utama

- **Face Recognition**: Verifikasi wajah menggunakan library `face_recognition` dan OpenCV.
- **Manajemen Absensi**: Pencatatan jam masuk dan pulang secara real-time.
- **Rekap Kehadiran**: Riwayat kehadiran dengan keterangan otomatis (terlambat, lembur, pulang cepat). Jam kerja standar: 09:00 - 18:00.
- **Pengajuan Cuti**: Formulir digital untuk pengajuan cuti ke HRD (termasuk upload surat dokter untuk cuti sakit).
- **Panel Admin HRD**: Enrollment karyawan baru, edit/hapus data karyawan, dan persetujuan cuti.
- **Slip Gaji Terintegrasi**: Penghitungan gaji otomatis berdasarkan data karyawan.
- **Mode Tanpa Kamera**: Upload foto wajah sebagai fallback jika kamera tidak tersedia.

## Teknologi yang Digunakan

- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.x, Flask
- **Computer Vision**: OpenCV, face_recognition, dlib
- **Database**: SQLite (otomatis, tanpa instalasi tambahan)

## Struktur File

```
project_skripsi_testing/
├── app.py                  # Backend Flask (API server, 11 endpoint)
├── camera.js               # Modul kamera & fallback upload foto
├── style.css               # Stylesheet global
├── index.html              # Halaman beranda
├── login.html              # Halaman login (pilih role)
├── dashboard.html          # Halaman absensi karyawan (face verification)
├── rekap_kehadiran.html    # Riwayat kehadiran + keterangan telat/lembur
├── pengajuan_cuti.html     # Formulir & riwayat pengajuan cuti
├── slip_gaji.html          # Slip gaji karyawan
├── admin.html              # Panel admin HRD (kelola karyawan & cuti)
├── test_api.py             # Script testing API tanpa browser
├── test_images/            # Folder foto wajah untuk testing
│   ├── test_face.jpg
│   ├── face_test1.jpg
│   └── face_test2.jpg
├── .gitignore              # Ignore database & cache files
└── requirements.txt        # Daftar dependensi Python
```

## Cara Menjalankan Program

### 1. Prasyarat

- **Python 3.10+** sudah terinstal
- Koneksi internet (untuk instalasi library pertama kali)

### 2. Instalasi Dependensi

Buka terminal di folder proyek, lalu jalankan:

```bash
pip install flask flask-cors opencv-python numpy Pillow
pip install dlib-bin
pip install face_recognition --no-deps
pip install face-recognition-models
pip install "setuptools<81"
```

### 3. Jalankan Server Backend

```bash
python app.py
```

Server akan berjalan di **http://127.0.0.1:5000**. Database SQLite (`payrollface.db`) akan dibuat secara otomatis saat pertama kali dijalankan, lengkap dengan akun Admin HRD default.

### 4. Buka Frontend

Buka file `index.html` di browser (klik kanan > Open with browser, atau gunakan Live Server extension di VS Code).

## Panduan Penggunaan

### Alur Admin HRD

1. Buka `index.html` > klik **Mulai Simulasi Sekarang**
2. Di halaman login, pilih **Masuk sebagai Admin HRD**
3. Di panel admin terdapat dua menu:

**Kelola Karyawan:**
- **Enrollment Karyawan Baru**:
  - Isi NIK, Nama Lengkap, dan Gaji Pokok
  - Jika ada kamera: wajah otomatis terdeteksi dari video
  - Jika tidak ada kamera: klik area upload, pilih foto wajah karyawan
  - Klik **Ambil Sampel Wajah** untuk menyimpan data biometrik
- **Daftar Karyawan**:
  - Tabel berisi semua karyawan terdaftar (NIK, Nama, Gaji, Tgl Daftar)
  - Menampilkan total jumlah karyawan
  - Tombol **Edit**: ubah NIK, Nama, atau Gaji Pokok via modal dialog
  - Tombol **Hapus**: hapus karyawan beserta seluruh data absensi dan cutinya

**Persetujuan Cuti:**
- Lihat semua pengajuan cuti dari karyawan
- Tombol **Setujui** atau **Tolak** untuk pengajuan berstatus Pending
- Status terupdate secara real-time di halaman karyawan

### Alur Karyawan

1. Buka `index.html` > klik **Mulai Simulasi Sekarang**
2. Di halaman login, pilih **Masuk sebagai Karyawan**
3. **Absensi** (`dashboard.html`):
   - Pilih tipe absensi: **Masuk** atau **Pulang**
   - Jika ada kamera: arahkan wajah ke kamera
   - Jika tidak ada kamera: upload foto wajah yang sudah didaftarkan
   - Klik **Mulai Verifikasi Wajah**
   - Sistem mencocokkan wajah dengan database dan mencatat kehadiran
4. **Rekap Kehadiran** (`rekap_kehadiran.html`):
   - Menampilkan Nama dan NIK karyawan dari database
   - Tabel riwayat: Tanggal, Jam Masuk, Jam Keluar, Status, dan **Keterangan**
   - Keterangan dihitung otomatis berdasarkan jam kerja standar (09:00 - 18:00):
     - **Tepat waktu** (hijau) -- masuk sebelum/tepat 09:00
     - **Terlambat X jam Y menit** (merah) -- masuk setelah 09:00
     - **Lembur X jam Y menit** (biru) -- pulang setelah 18:00
     - **Pulang cepat X jam Y menit** (oranye) -- pulang sebelum 18:00
5. **Pengajuan Cuti** (`pengajuan_cuti.html`):
   - Menampilkan Nama dan NIK karyawan yang sedang login
   - Pilih jenis cuti (Tahunan / Sakit / Kepentingan Mendesak)
   - Jika Cuti Sakit: wajib upload surat dokter
   - Isi tanggal dan alasan, lalu klik **Kirim Pengajuan ke HRD**
   - Riwayat pengajuan menampilkan status terbaru dari database (Pending / Approved / Rejected / Cancelled)
   - Pengajuan berstatus Pending dapat dibatalkan
6. **Slip Gaji** (`slip_gaji.html`):
   - Menampilkan Nama, NIK, Gaji Pokok, Potongan, dan Total Diterima
   - Tombol **Cetak Slip Gaji** untuk print

## Testing API Tanpa Browser

Gunakan script `test_api.py` untuk menguji API backend secara langsung:

```bash
# Test semua endpoint (otomatis pakai test_images/test_face.jpg)
python test_api.py

# Test dengan foto tertentu
python test_api.py test_images/face_test1.jpg

# Test endpoint tertentu
python test_api.py test_images/test_face.jpg register    # Daftarkan karyawan baru
python test_api.py test_images/test_face.jpg masuk       # Absensi masuk
python test_api.py test_images/test_face.jpg pulang      # Absensi pulang
```

## Cek Isi Database

```bash
# Lihat semua user
python -m sqlite3 payrollface.db "SELECT id, nik, nama, role, gaji_pokok FROM users;"

# Lihat log kehadiran
python -m sqlite3 payrollface.db "SELECT * FROM attendance_logs;"

# Lihat pengajuan cuti
python -m sqlite3 payrollface.db "SELECT * FROM leaves;"

# Mode interaktif (ketik query SQL bebas, .quit untuk keluar)
python -m sqlite3 payrollface.db
```

## API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| POST | `/api/v1/face/register` | Enrollment wajah karyawan baru |
| POST | `/api/v1/verify-liveness` | Verifikasi wajah untuk absensi masuk/pulang |
| GET | `/api/v1/employee/data/<id>` | Ambil data & riwayat kehadiran karyawan |
| GET | `/api/v1/employees` | Daftar semua karyawan (admin) |
| PUT | `/api/v1/employee/update/<id>` | Edit data karyawan (admin) |
| DELETE | `/api/v1/employee/delete/<id>` | Hapus karyawan (admin) |
| POST | `/api/v1/leave/request` | Ajukan cuti |
| POST | `/api/v1/leave/cancel` | Batalkan pengajuan cuti |
| GET | `/api/v1/leave/my/<id>` | Riwayat cuti per karyawan |
| GET | `/api/v1/leave/list` | Daftar semua pengajuan cuti (admin) |
| POST | `/api/v1/leave/approve` | Setujui/tolak cuti (admin) |

## Database Schema

Tiga tabel utama (SQLite, auto-generated):

- **users** -- id, nik, nama, role (admin/karyawan), gaji_pokok, face_encoding, created_at
- **attendance_logs** -- id, user_id (FK), tanggal, jam_masuk, jam_keluar, status
- **leaves** -- id, user_id (FK), jenis_cuti, tanggal, alasan, attachment, status (Pending/Approved/Rejected/Cancelled)

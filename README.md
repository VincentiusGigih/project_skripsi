# PayrollFace - Sistem Absensi & Payroll Berbasis Face Recognition

Sistem informasi absensi dan payroll yang mengintegrasikan verifikasi biometrik wajah dan *Liveness Detection* (Deteksi Kedipan) untuk memastikan kehadiran karyawan yang akurat dan aman.

## 🚀 Fitur Utama
- **Face Recognition & Liveness Detection**: Verifikasi wajah asli (bukan foto statis) menggunakan OpenCV.
- **Manajemen Absensi**: Pencatatan jam masuk dan pulang secara real-time.
- **Pengajuan Cuti**: Formulir digital untuk pengajuan cuti ke HRD.
- **Panel Admin HRD**: Kelola enrollment karyawan baru dan persetujuan cuti.
- **Slip Gaji Terintegrasi**: Penghitungan gaji otomatis berdasarkan rekap kehadiran.

## 🛠️ Teknologi yang Digunakan
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Backend**: Python 3.x, Flask
- **Computer Vision**: OpenCV
- **Storage**: Browser LocalStorage (untuk simulasi frontend)

## 📋 Cara Menjalankan Program

### 1. Prasyarat
Pastikan sudah menginstal **Python 3.x** di perangkat.

### 2. Instalasi Library
Buka terminal/command prompt di folder proyek, lalu jalankan:
```bash
pip install -r requirements.txt

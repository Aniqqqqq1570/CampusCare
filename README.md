# Sistem Informasi Pelaporan Kerusakan Fasilitas Kampus

## Deskripsi Proyek

Sistem Informasi Pelaporan Kerusakan Fasilitas Kampus merupakan aplikasi berbasis website yang dirancang untuk mempermudah mahasiswa dalam melaporkan kerusakan fasilitas yang berada di lingkungan kampus.

Melalui sistem ini, mahasiswa dapat mengirimkan laporan kerusakan dengan menyertakan deskripsi, kategori, lokasi, dan foto sebagai bukti. Mahasiswa juga dapat melihat laporan yang dikirim oleh mahasiswa lain serta memantau perkembangan penanganan laporan.

Laporan yang masuk akan diterima dan ditindaklanjuti secara langsung oleh pihak kampus. Sementara itu, admin bertugas mengelola dan mengawasi sistem, termasuk data pengguna, kategori kerusakan, lokasi fasilitas, serta aktivitas pelaporan.

## Tujuan Proyek

1. Mempermudah mahasiswa dalam menyampaikan laporan kerusakan fasilitas kampus.
2. Membantu pihak kampus mengetahui kondisi fasilitas yang membutuhkan perbaikan.
3. Meningkatkan transparansi proses penanganan laporan.
4. Mempermudah pemantauan riwayat dan perkembangan laporan.
5. Menyediakan data laporan sebagai bahan evaluasi fasilitas kampus.

## Hak Akses Pengguna

### 1. Mahasiswa
- Login menggunakan akun akademik kampus.
- Membuat laporan kerusakan fasilitas.
- Mengunggah foto kerusakan.
- Melihat seluruh laporan yang telah dikirim.
- Melihat detail dan lokasi kerusakan.
- Memantau status laporan.
- Melihat riwayat laporan pribadi.
- Memberikan dukungan pada laporan kerusakan serupa.

### 2. Admin
- Mengelola akun pengguna.
- Mengelola kategori kerusakan.
- Mengelola data lokasi fasilitas.
- Melihat dan memantau seluruh laporan.
- Melihat statistik dan aktivitas sistem.
- Mengelola log aktivitas.
- Mengekspor data laporan.

### 3. Pihak Kampus
- Melihat laporan yang masuk.
- Melakukan verifikasi laporan.
- Menolak laporan dengan menyertakan alasan.
- Memberikan tanggapan kepada pelapor.
- Memperbarui status penanganan.
- Menambahkan catatan perkembangan.
- Mengunggah dokumentasi hasil perbaikan.

## Status Laporan

Sistem menggunakan beberapa status untuk menunjukkan perkembangan penanganan laporan:

1. **Menunggu Verifikasi** – Laporan telah dikirim dan menunggu pemeriksaan.
2. **Diverifikasi** – Laporan telah diperiksa dan dinyatakan valid.
3. **Sedang Diproses** – Laporan sedang ditangani oleh pihak kampus.
4. **Selesai** – Kerusakan telah selesai ditangani.
5. **Ditolak** – Laporan tidak dapat diproses dan harus disertai alasan penolakan.

## Fitur Utama

- Autentikasi dan pembagian hak akses pengguna.
- Pelaporan kerusakan fasilitas.
- Unggah foto bukti kerusakan.
- Kategori dan lokasi fasilitas.
- Daftar seluruh laporan.
- Detail dan riwayat laporan.
- Pelacakan status penanganan.
- Verifikasi dan tindak lanjut laporan.
- Dokumentasi sebelum dan sesudah perbaikan.
- Dashboard dan statistik laporan.

## Teknologi yang Digunakan

*Teknologi berikut merupakan rencana awal dan dapat disesuaikan selama proses pengembangan.*

- **Frontend:** HTML, CSS, JavaScript, Bootstrap
- **Backend:** Python Flask
- **Database:** MySQL
- **Tools:** Visual Studio Code, Git, GitHub/GitLab

## Alur Sistem

1. Mahasiswa login ke dalam sistem.
2. Mahasiswa membuat laporan kerusakan fasilitas.
3. Sistem menyimpan laporan dan menampilkannya pada daftar laporan.
4. Pihak kampus menerima dan memverifikasi laporan.
5. Pihak kampus memberikan tanggapan serta memperbarui status penanganan.
6. Mahasiswa dapat memantau perkembangan laporan.
7. Setelah perbaikan selesai, pihak kampus mengunggah dokumentasi penyelesaian.
8. Admin dapat memantau seluruh aktivitas dan data laporan.

## Keamanan dan Privasi

- Setiap pengguna memiliki hak akses sesuai perannya.
- Identitas pelapor tidak ditampilkan kepada mahasiswa lain.
- Hanya pihak kampus yang berwenang mengubah status penanganan.
- Admin bertugas mengawasi sistem dan tidak menjadi perantara laporan.
- Kata sandi akun akademik tidak disimpan di aplikasi.

## Status Pengembangan

**Tahap:** Perencanaan dan Perancangan Sistem

Proyek ini dikembangkan sebagai sistem informasi berbasis website untuk mendukung pengelolaan laporan kerusakan fasilitas di lingkungan kampus.

---

**Catatan:** Proyek ini masih dalam tahap perencanaan dan akan dikembangkan secara bertahap sesuai hasil analisis kebutuhan dan rancangan sistem.

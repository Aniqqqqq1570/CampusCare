-- Jalankan sekali pada database CampusCare yang sudah ada.
-- Menambahkan identitas akademik agar tampil pada kartu Laporan Publik.
ALTER TABLE users
    ADD COLUMN study_program VARCHAR(100) NULL,
    ADD COLUMN faculty VARCHAR(120) NULL;

-- Setelah kolom ditambahkan, isi data mahasiswa yang sudah terdaftar.
-- Contoh (ganti sesuai data asli):
-- UPDATE users
-- SET study_program = 'Informatika', faculty = 'Fakultas Sains dan Teknologi'
-- WHERE nim = 'NIM_MAHASISWA';

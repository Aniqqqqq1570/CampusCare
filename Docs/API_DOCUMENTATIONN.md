# CampusCare API Documentation

Dokumentasi API backend CampusCare.

## 1. Informasi Umum

**Nama aplikasi:** CampusCare  
**Backend:** Python Flask  
**Database:** TiDB Cloud  
**Frontend:** HTML, CSS, JavaScript  
**Authentication:** Flask-Login (Session Cookie)

### Base URL

Saat development:

```text
http://127.0.0.1:5000
```

### Format Response

Sebagian besar endpoint API mengembalikan JSON dengan format:

```json
{
  "message": "Pesan informasi",
  "data": {}
}
```

### Authentication

API menggunakan session cookie Flask.

Untuk JavaScript, gunakan:

```javascript
credentials: "include"
```

Akun harus login terlebih dahulu sebelum mengakses endpoint yang dilindungi.

### Role Pengguna

| Role | Hak akses |
|---|---|
| mahasiswa | Membuat dan mengelola laporan sendiri |
| kampus | Melihat laporan dan memperbarui status |
| admin | Mengelola pengguna, kategori, lokasi, dan melihat laporan |

---

## 2. Authentication

Base endpoint: `/`

### 2.1 Registrasi

**POST** `/register`

Membuat akun mahasiswa baru.

Form fields:

| Field | Tipe | Wajib |
|---|---|---|
| full_name | String | Ya |
| nim | String | Ya |
| email | String | Ya |
| password | String | Ya |

Ketentuan:
- Password minimal 8 karakter.
- Email harus unik.
- NIM harus unik.
- Role otomatis menjadi `mahasiswa`.

Format pengiriman: Form Data atau URL Encoded.

Response berupa redirect dan flash message, bukan JSON.

### 2.2 Login

**POST** `/login`

Form fields:

| Field | Tipe | Wajib |
|---|---|---|
| email | String | Ya |
| password | String | Ya |

Setelah login berhasil, pengguna diarahkan berdasarkan role:

- admin → `/api/admin/dashboard`
- kampus → `/api/campus/dashboard`
- mahasiswa → `/api/student/dashboard`

Login menyimpan session cookie.

### 2.3 Logout

**GET** `/logout`

Mengakhiri session pengguna.

### 2.4 Dashboard Redirect

**GET** `/dashboard`

Mengarahkan pengguna ke dashboard berdasarkan role.

---

## 3. API Mahasiswa

Base endpoint: `/api/student`

Semua endpoint memerlukan login dengan role `mahasiswa`.

### 3.1 Dashboard Mahasiswa

**GET** `/api/student/dashboard`

Response:

```json
{
  "message": "Selamat datang di dashboard mahasiswa",
  "user": "Nama Mahasiswa",
  "role": "mahasiswa"
}
```

### 3.2 Menampilkan Laporan

**GET** `/api/student/reports`

Menampilkan semua laporan milik mahasiswa yang sedang login.

Response:

```json
{
  "message": "Daftar laporan berhasil diambil",
  "data": [
    {
      "id": 1,
      "title": "AC Ruang Kelas Rusak",
      "description": "AC tidak menyala",
      "status": "menunggu_verifikasi",
      "image_path": "/static/uploads/reports/contoh.jpg",
      "category": {
        "id": 1,
        "name": "Kerusakan Elektronik"
      },
      "location": {
        "id": 1,
        "name": "Ruang Kelas",
        "building": "Gedung A",
        "floor": "1"
      },
      "created_at": "2026-11-08T10:00:00",
      "updated_at": "2026-11-08T10:00:00"
    }
  ]
}
```

### 3.3 Membuat Laporan

**POST** `/api/student/reports`

Membuat laporan baru.

Format: `multipart/form-data`

| Field | Tipe | Wajib |
|---|---|---|
| title | String | Ya |
| description | String | Ya |
| category_id | Integer | Ya |
| location_id | Integer | Ya |
| image | File | Tidak |

Ketentuan foto:
- JPG
- JPEG
- PNG
- WEBP
- Maksimal 5 MB

Contoh JavaScript:

```javascript
const formData = new FormData();

formData.append("title", "AC Ruang Kelas Rusak");
formData.append("description", "AC tidak menyala");
formData.append("category_id", 1);
formData.append("location_id", 1);
formData.append("image", imageInput.files[0]);

const response = await fetch(
  "http://127.0.0.1:5000/api/student/reports",
  {
    method: "POST",
    credentials: "include",
    body: formData
  }
);

const result = await response.json();
console.log(result);
```

Jangan mengatur header `Content-Type` secara manual saat menggunakan FormData.

Response sukses: HTTP 201.

### 3.4 Detail Laporan

**GET** `/api/student/reports/{report_id}`

Menampilkan detail laporan milik mahasiswa yang sedang login.

Response memiliki struktur data laporan yang sama dengan endpoint daftar laporan.

### 3.5 Mengubah Laporan

**PUT** `/api/student/reports/{report_id}`

Mengubah laporan yang masih berstatus `menunggu_verifikasi`.

Field yang dapat diubah:

- title
- description
- category_id
- location_id
- image

Foto bersifat opsional. Jika foto baru dikirim, foto lama akan diganti.

Format pengiriman dapat menggunakan JSON atau FormData.

### 3.6 Menghapus Laporan

**DELETE** `/api/student/reports/{report_id}`

Menghapus laporan milik mahasiswa.

Laporan hanya dapat dihapus ketika statusnya `menunggu_verifikasi`.

Response:

```json
{
  "message": "Laporan berhasil dihapus"
}
```

---

## 4. API Pihak Kampus

Base endpoint: `/api/campus`

Semua endpoint memerlukan login dengan role `kampus`.

### 4.1 Dashboard Kampus

**GET** `/api/campus/dashboard`

Response:

```json
{
  "message": "Selamat datang di dashboard pihak kampus",
  "user": "Nama Petugas",
  "role": "kampus"
}
```

### 4.2 Daftar Laporan

**GET** `/api/campus/reports`

Menampilkan seluruh laporan mahasiswa.

Data mencakup:
- ID laporan
- Judul
- Deskripsi
- Status
- Nama mahasiswa
- Kategori
- Lokasi
- Gedung
- Lantai
- Tanggal dibuat

### 4.3 Detail Laporan

**GET** `/api/campus/reports/{report_id}`

Menampilkan detail laporan dan riwayat tanggapan.

Response:

```json
{
  "message": "Detail laporan berhasil diambil",
  "data": {
    "id": 1,
    "title": "AC Ruang Kelas Rusak",
    "description": "AC tidak menyala",
    "status": "menunggu_verifikasi",
    "student": "Nama Mahasiswa",
    "category": "Kerusakan Elektronik",
    "location": "Ruang Kelas",
    "building": "Gedung A",
    "floor": "1",
    "created_at": "2026-11-08T10:00:00"
  },
  "responses": []
}
```

Catatan: Implementasi saat ini belum menyertakan URL foto pada response kampus.

### 4.4 Memperbarui Status Laporan

**PATCH** `/api/campus/reports/{report_id}/status`

Memperbarui status laporan sekaligus memberikan tanggapan.

Request JSON:

```json
{
  "status": "diverifikasi",
  "message": "Laporan telah diverifikasi oleh pihak kampus."
}
```

Status yang diperbolehkan:

| Status saat ini | Status berikutnya |
|---|---|
| menunggu_verifikasi | diverifikasi |
| menunggu_verifikasi | ditolak |
| diverifikasi | sedang_diproses |
| diverifikasi | ditolak |
| sedang_diproses | selesai |

Setiap perubahan status akan:
1. Memperbarui status laporan.
2. Menyimpan tanggapan ke tabel `responses`.
3. Mencatat aktivitas ke tabel `activity_logs`.

Response sukses:

```json
{
  "message": "Status laporan berhasil diperbarui",
  "data": {
    "report_id": 1,
    "old_status": "menunggu_verifikasi",
    "new_status": "diverifikasi",
    "response": "Laporan telah diverifikasi oleh pihak kampus."
  }
}
```

---

## 5. API Admin

Base endpoint: `/api/admin`

Semua endpoint memerlukan login dengan role `admin`.

### 5.1 Dashboard dan Statistik

**GET** `/api/admin/dashboard`

Mengambil statistik aplikasi.

Data:
- total_users
- total_students
- total_campus
- total_reports
- reports_by_status
- total_categories
- total_locations

### 5.2 Manajemen Pengguna

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/admin/users` | Daftar pengguna |
| GET | `/api/admin/users/{user_id}` | Detail pengguna |
| POST | `/api/admin/users` | Membuat pengguna |
| PUT | `/api/admin/users/{user_id}` | Mengubah pengguna |
| DELETE | `/api/admin/users/{user_id}` | Menonaktifkan pengguna |

#### Membuat pengguna

Request JSON:

```json
{
  "full_name": "Nama Pengguna",
  "nim": "123456789",
  "email": "pengguna@example.com",
  "password": "password123",
  "role": "mahasiswa"
}
```

Role yang tersedia:
- mahasiswa
- kampus
- admin

Password minimal 8 karakter.

#### Mengubah pengguna

**PUT** `/api/admin/users/{user_id}`

Field yang dapat diubah:
- full_name
- nim
- email
- role
- password (opsional)

#### Menonaktifkan pengguna

**DELETE** `/api/admin/users/{user_id}`

Penghapusan dilakukan dengan mengubah `is_active` menjadi `false`, bukan menghapus data secara permanen.

Admin tidak dapat menonaktifkan akunnya sendiri.

### 5.3 Manajemen Kategori

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/admin/categories` | Daftar kategori |
| POST | `/api/admin/categories` | Membuat kategori |
| PUT | `/api/admin/categories/{category_id}` | Mengubah kategori |
| DELETE | `/api/admin/categories/{category_id}` | Menonaktifkan kategori |

Request membuat kategori:

```json
{
  "name": "Kerusakan Elektronik",
  "description": "Kerusakan perangkat elektronik kampus"
}
```

DELETE kategori menggunakan soft delete dengan mengubah `is_active` menjadi `false`.

### 5.4 Manajemen Lokasi

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/admin/locations` | Daftar lokasi |
| POST | `/api/admin/locations` | Membuat lokasi |
| PUT | `/api/admin/locations/{location_id}` | Mengubah lokasi |
| DELETE | `/api/admin/locations/{location_id}` | Menonaktifkan lokasi |

Request membuat lokasi:

```json
{
  "name": "Ruang Kelas",
  "building": "Gedung A",
  "floor": "1",
  "description": "Ruang kelas lantai satu"
}
```

DELETE lokasi menggunakan soft delete dengan mengubah `is_active` menjadi `false`.

### 5.5 Manajemen Laporan

| Method | Endpoint | Fungsi |
|---|---|---|
| GET | `/api/admin/reports` | Daftar seluruh laporan |
| GET | `/api/admin/reports/{report_id}` | Detail laporan |

Filter berdasarkan status:

```text
GET /api/admin/reports?status=menunggu_verifikasi
```

Detail laporan juga menampilkan riwayat tanggapan.

### 5.6 Riwayat Aktivitas

**GET** `/api/admin/activity-logs`

Menampilkan maksimal 100 aktivitas terbaru.

Data mencakup:
- ID aktivitas
- Nama pengguna
- Jenis aktivitas
- Deskripsi aktivitas
- Waktu aktivitas

---

## 6. Daftar Status Laporan

| Status | Keterangan |
|---|---|
| menunggu_verifikasi | Laporan menunggu pemeriksaan |
| diverifikasi | Laporan telah diverifikasi |
| sedang_diproses | Laporan sedang ditangani |
| selesai | Penanganan laporan selesai |
| ditolak | Laporan ditolak |

---

## 7. HTTP Status Code

| Kode | Keterangan |
|---|---|
| 200 | Request berhasil |
| 201 | Data berhasil dibuat |
| 400 | Request tidak valid |
| 403 | Akses ditolak atau tindakan tidak diperbolehkan |
| 404 | Data tidak ditemukan |
| 409 | Data duplikat atau konflik |
| 413 | File melebihi batas ukuran upload |

Untuk endpoint yang dilindungi, pengguna harus login dan memiliki role yang sesuai.

---

## 8. Integrasi Frontend

Frontend menggunakan HTML, CSS, dan JavaScript.

Backend development:

```text
http://127.0.0.1:5000
```

Frontend Live Server:

```text
http://127.0.0.1:5500
```

Konfigurasi CORS backend mengizinkan kedua origin berikut:

```text
http://127.0.0.1:5500
http://localhost:5500
```

Contoh GET API:

```javascript
const response = await fetch(
  "http://127.0.0.1:5000/api/student/reports",
  {
    method: "GET",
    credentials: "include"
  }
);

const result = await response.json();
console.log(result);
```

Contoh POST JSON:

```javascript
const response = await fetch(
  "http://127.0.0.1:5000/api/admin/categories",
  {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      name: "Fasilitas Umum",
      description: "Kerusakan fasilitas umum kampus"
    })
  }
);
```

Catatan:
- Gunakan `credentials: "include"` untuk request yang membutuhkan session login.
- Jangan menggunakan JSON untuk upload foto. Gunakan FormData.
- Jangan mengakses database TiDB langsung dari frontend.
- Semua komunikasi data harus melalui Flask API.

---

## 9. Catatan Pengembangan

Beberapa hal yang perlu diselesaikan sebelum integrasi frontend dinyatakan lengkap:

1. Menambahkan endpoint mahasiswa untuk mengambil daftar kategori aktif.
2. Menambahkan endpoint mahasiswa untuk mengambil daftar lokasi aktif.
3. Menyediakan URL foto laporan pada response API pihak kampus.
4. Memastikan response admin mengembalikan URL foto yang dapat diakses frontend.
5. Melakukan pengujian seluruh endpoint melalui browser setelah frontend selesai.

Dokumentasi ini mengikuti implementasi backend CampusCare saat ini. Perubahan endpoint atau format response harus diikuti dengan pembaruan dokumentasi.
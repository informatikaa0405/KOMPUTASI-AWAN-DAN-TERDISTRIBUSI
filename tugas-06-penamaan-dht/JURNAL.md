# Jurnal Proses — Tugas 6

## Implementasi `find_successor`
- **Kesalahan pertama yang ditemui:** Logika pencarian successor perlu memperhatikan kondisi *wrap-around*. Jika nilai hash key lebih besar daripada seluruh ID node yang ada, pencarian tidak boleh menghasilkan nilai kosong atau error.
- **Cara memperbaikinya:** ID node diurutkan dari yang terkecil hingga terbesar. Program memilih node pertama yang memiliki ID lebih besar atau sama dengan hash key. Jika tidak ditemukan, program mengembalikan node dengan ID terkecil sebagai successor. Dengan demikian, pencarian tetap berjalan sesuai sifat ring Chord yang melingkar.

## Skenario join/leave
- **Hasil sebelum dan sesudah node baru bergabung:**
  - `node-medan-1` (id=123) bergabung: tidak ada key yang berpindah karena tidak terdapat key pada rentang (102, 123]. `kurir-001` tetap berada di `node-jakarta-2`.
  - `node-semarang-1` (id=77) bergabung: `kurir-001` (hash=50) berpindah dari `node-jakarta-2` (id=102) ke `node-semarang-1` (id=77), karena node baru menjadi successor untuk key tersebut.
- **Hasil sebelum dan sesudah node keluar:**
  - `node-jakarta-1` (id=177) keluar: `kurir-005` (hash=175) berpindah ke `node-bandung-1` (id=40) melalui mekanisme *wrap-around*.
  - `node-semarang-1` (id=77) keluar: `kurir-001` berpindah kembali ke `node-jakarta-2` (id=102), yang menjadi successor berikutnya.
  - **Bukti pengujian:** `bukti/output_simulasi.txt`.

## Kontribusi anggota
Berikut pembagian kontribusi yang disusun sebagai draf berdasarkan bagian pekerjaan dalam proyek. Pastikan pembagian ini sesuai dengan pekerjaan nyata masing-masing anggota sebelum dikumpulkan.

| Anggota | Kontribusi |
|---|---|
| Rui Juniarta | Mempelajari konsep Chord DHT dan membantu implementasi serta pemeriksaan fungsi pencarian successor (`find_successor`). |
| Mochammad Raditya | Membantu implementasi dan pemeriksaan proses penambahan node (`join`) serta pengeluaran node (`leave`), termasuk perpindahan tanggung jawab data. |
| Danendra Adi | Membantu menjalankan simulasi, memeriksa hasil lookup ID kurir, dan mencocokkan hasil pengujian dengan output simulasi. |
| Arya Bariq Irawan | Membantu menyusun dokumentasi proyek, analisis pada README, dan merapikan bukti hasil pengujian. |

## Log Penggunaan AI
| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah menjadi tulisan/kode sendiri |
|---|---|---|---|---|
| 2026-10-31 | ChatGPT | Meminta beberapa ide untuk memahami dan mengerjakan tugas Penamaan DHT (Chord), terutama implementasi, pengujian, dan analisis. | Memberikan ide mengenai mekanisme `find_successor`, proses `join` dan `leave`, lookup ID kurir, serta skenario pengujian perubahan alamat IP. | Ide digunakan sebagai referensi untuk memahami konsep Chord DHT, menentukan skenario pengujian, dan menyusun analisis. Selanjutnya, ide disesuaikan dengan kebutuhan tugas serta hasil implementasi dan simulasi proyek. |

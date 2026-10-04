# Tugas 1 — Analisis Pitfall FoodGo

**Kelompok:** [nama kelompok]

| Nama | NIM | Kontribusi |
|------|-----|------------|
| [Mochammad Raditya Ramadani Akbar] | [103072400039] | Pitfall 1: Network is reliable |
| [Danendra Adi Wicaksono] | [103072400076] | Pitfall 2: Tidak ada timeout (latency is zero) |
| [Arya Bariq Irawan] | [103072400132] | Pitfall 3: Single point of failure |
| [Rui Juniarta] | [103072400090] | Kesimpulan Kelompok, merapikan JURNAL.md, tabel kontribusi |
---

## Pitfall 1: Network is reliable 

**Bukti di skenario:** Di kode FoodGo ada komentar `# network is always reliable, no need for retry`. Jadi programmernya sengaja tidak membuat retry, dan di beberapa permintaan menjadi timeout waktu pesanan lagi banyak.

**Kenapa salah:** Programmer menganggap jaringan pasti lancar, kenyataannya paket data bisa hilang, koneksi bisa putus, apalagi kalau lagi padat. Gangguan kecil seperti ini biasa di sistem terdistribusi, jadi seharusnya sudah diantisipasi.

**Dampak ke FoodGo:** Karena tidak ada retry, gangguan jaringan yang cuma sebentar langsung bikin pesanan atau pembayaran gagal. User dapat error padahal kalau dicoba sekali lagi mungkin berhasil. Waktu jam makan siang atau promo besar, jaringan lebih padat, jadi kejadian makin sering.

**Solusi:** Pakai retry dengan backoff, yaitu jeda antar percobaan dibuat makin lama (misalnya 1 detik, lalu 2 detik, lalu 4 detik) dan jumlah percobaan dibatasi, misalnya maksimal 3 kali. Khusus pembayaran, tiap transaksi perlu ID unik supaya kalau di-retry, pelanggan tidak tertagih dua kali.

**Trade-off:** Retry menambah beban ke service tujuan. Kalau service itu memang sedang bermasalah, banyak retry yang masuk bersamaan malah bisa memperparah (cascading failure). Retry juga bikin user menunggu lebih lama, dan membuat ID unik untuk transaksi menambah pekerjaan buat programmer.

---

## Pitfall 2: Tidak ada timeout (latency is zero) 

**Bukti di skenario:** Waktu modul pesanan memanggil modul pembayaran, modulnya menunggu tanpa batas waktu. Tidak ada timeout sama sekali.

**Kenapa ini keliru:** Programmer menganggap pembayaran pasti langsung membalas. Padahal latensi jaringan tidak nol, dan service tujuan bisa saja lambat atau macet. Tanpa timeout, modul pesanan tidak punya batas kapan harus berhenti menunggu.

**Dampak ke FoodGo:** Kalau modul pembayaran lambat, setiap thread di modul pesanan yang memanggilnya ikut tertahan. Permintaan baru terus masuk, jadi thread yang tertahan makin banyak sampai resource server (thread dan memori) habis. Akibatnya modul pesanan tidak bisa melayani permintaan lain, aplikasi jadi sangat lambat, dan server akhirnya crash lalu harus di-restart manual. Jadi masalah di satu modul menjalar ke modul lain.

**Solusi desain awal:** Pasang timeout di setiap pemanggilan antar service, misalnya 3 detik untuk pembayaran. Tambahkan juga circuit breaker. Kalau pembayaran gagal atau lambat berkali-kali, pemanggilan ke sana dihentikan sementara dan langsung dibalas gagal (atau pesanan disimpan dulu dengan status menunggu pembayaran), lalu dicoba lagi setelah beberapa saat.

**Trade-off:** Kalau timeout terlalu pendek, permintaan yang sebenarnya bisa berhasil ikut dibatalkan. Kalau terlalu panjang, resource server tetap tidak terlindungi. Circuit breaker juga menambah kerumitan karena harus diatur dan dipantau, dan selama circuit terbuka sebagian user tetap gagal bayar, jadi harus ditentukan juga pesan error dan alur cadangannya.

---

## Pitfall 3: Single point of failure 

**Bukti di skenario:** Satu server menangani semua modul (pesanan, pembayaran, notifikasi kurir) karena semuanya jalan dalam satu proses monolitik. Waktu trafik naik, server ini kewalahan.

**Kenapa ini keliru:** Desain ini bergantung pada satu proses dan satu server untuk semua fungsi. Kalau salah satu modul bermasalah, tidak ada yang memisahkannya dari modul lain. Skalabilitasnya juga kurang karena semua modul harus ikut diperbesar bersama, padahal mungkin hanya satu modul yang butuh.

**Dampak ke FoodGo:** Kalau satu modul bermasalah, misalnya notifikasi kurir lambat atau kehabisan memori, seluruh proses ikut jatuh, sehingga pesanan dan pembayaran juga ikut mati. Saat ramai, satu server tidak kuat menampung beban, dan sekali crash seluruh layanan berhenti sampai di-restart manual.

**Solusi desain awal:** Pisahkan modul jadi service sendiri-sendiri (pesanan, pembayaran, notifikasi kurir) supaya bisa dijalankan dan diperbesar masing-masing. Tiap service dijalankan lebih dari satu instance dengan load balancer di depannya. Untuk hal yang tidak harus langsung selesai, seperti notifikasi kurir, bisa pakai message queue supaya service pesanan tidak perlu menunggu.

**Trade-off:** Memecah monolit membuat pengelolaan lebih rumit: ada lebih banyak service yang harus di-deploy, dipantau, dan di-debug. Selain itu muncul pemanggilan lewat jaringan antar service, sehingga masalah di Pitfall 1 dan 2 bisa muncul lagi. Untuk tim kecil, sebaiknya dipecah bertahap, mulai dari modul yang paling sering bermasalah seperti pembayaran.

---

## Kesimpulan Kelompok

Ketiga pitfall ini saling berhubungan. Asumsi jaringan pasti cepat (Pitfall 1 dan 2) jadi berbahaya karena semua modul ada dalam satu proses (Pitfall 3), sehingga masalah kecil bisa menjatuhkan seluruh sistem. Kalau FoodGo memperbaiki ketiganya, arsitektur yang disarankan secara garis besar adalah memecah sistem jadi beberapa service yang berdiri sendiri (pesanan, pembayaran, notifikasi kurir). Antar service dipanggil dengan timeout, retry berbackoff, dan circuit breaker, dan proses yang tidak perlu langsung dijawab memakai antrean pesan. Hal ini bisa dilanjutkan di Tugas 2:yaitu merancang arsitektur FoodGo dengan SOA

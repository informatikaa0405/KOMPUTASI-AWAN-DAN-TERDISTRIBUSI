# Jurnal Proses — Tugas 3

## Percobaan tanpa Lock
- Hasil `processed_count` yang didapat:
  - Lokal (Windows, Python 3.11.9): **90 dari 100 pesanan**.
  - Docker container: **89 dari 100 pesanan**.
- Kenapa bisa meleset (mekanisme *race condition*):
  `processed_count` dipakai bersama oleh beberapa thread. Tanpa lock, dua thread dapat membaca nilai counter yang sama sebelum salah satunya memperbaruinya. Keduanya kemudian menulis nilai hasil penambahan yang sama, sehingga salah satu pembaruan hilang (*lost update*). Akibatnya, jumlah yang tercatat lebih kecil daripada 100 pesanan yang diproses.

## Percobaan dengan Lock
- Hasil `processed_count` setelah perbaikan:
  - Lokal (Windows, Python 3.11.9): **100**, dengan waktu sekitar **0,070 detik**.
  - Docker container: **100**, dengan waktu sekitar **0,072 detik**.
- Perbaikan dilakukan menggunakan `threading.Lock()` untuk melindungi bagian kode yang membaca, menambah, dan menulis kembali counter. Dengan begitu, hanya satu thread pada satu waktu yang memperbarui counter, sehingga hasilnya tepat 100.

## Kendala Docker
- Error yang ditemui saat `docker build`/`docker run` dan cara memperbaikinya:
  **Tidak ada pesan error Docker yang dicantumkan pada catatan sumber.** Berdasarkan hasil percobaan yang tersedia, container berhasil dijalankan dan menghasilkan `processed_count` sebesar 100 dengan lock serta 89 tanpa lock. Jika ada error yang benar-benar muncul saat proses build atau run, tambahkan pesan error tersebut beserta langkah perbaikannya di bagian ini.

## Log Penggunaan AI (Level 2)

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 20 Oktober 2026 | ChatGPT | Meminta ide dan bantuan untuk memahami cara kerja kode. | Membantu memberikan ide serta menjelaskan alur kerja kode agar lebih mudah dipahami. | Menggunakan penjelasan tersebut untuk memahami kode, lalu mengolah pemahaman dengan kata-kata sendiri. |

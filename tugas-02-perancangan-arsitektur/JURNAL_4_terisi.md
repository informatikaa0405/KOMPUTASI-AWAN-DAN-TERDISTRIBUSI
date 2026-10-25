# Jurnal Proses — Tugas 2

## 22 Oktober 2026
- Opsi arsitektur yang dipertimbangkan: Kelompok mempertimbangkan Service-Oriented Architecture (SOA) dan Publish-Subscribe. SOA memiliki pembagian layanan yang jelas dan mendukung komunikasi request-response, tetapi layanan perlu mengelola komunikasi antarlayanan. Publish-Subscribe memungkinkan pengirim dan penerima pesan tidak saling bergantung secara langsung, tetapi alur proses dapat lebih sulit ditelusuri karena komunikasi berlangsung melalui pesan.
- Kenapa akhirnya pilih SOA: SOA dipilih karena domain sistem dapat dibagi dengan jelas ke dalam beberapa modul layanan. Banyak proses membutuhkan pola request-response, dan kontrak API memungkinkan tim kurir dan restoran mengembangkan atau melakukan deployment layanan secara terpisah.
- Revisi diagram (versi 1 → versi 2, apa yang berubah dan kenapa): Diagram awal dibuat menggunakan Mermaid, lalu dipindahkan ke draw.io. Pada diagram komponen, arah panah Order → Payment tidak sesuai dengan sequence diagram. Panah kemudian diubah menjadi Payment → Order untuk menunjukkan bahwa layanan Payment meminta total tagihan dari Order.

## Log Penggunaan AI (Level 2)

> Penggunaan AI dibatasi untuk membantu memahami materi dan mencari ide, bukan untuk membuat kode atau menghasilkan teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
| 22 Okt 2026 | ChatGPT | Meminta penjelasan agar tidak bingung memahami materi dan meminta ide untuk tugas. | ChatGPT membantu menjelaskan konsep dan alur agar lebih mudah dipahami serta memberikan ide awal sebagai bahan pertimbangan. | Penjelasan dan ide digunakan sebagai referensi untuk memahami materi. Kelompok menentukan pilihan dan menyusun isi jurnal dengan kata-kata sendiri serta menyesuaikannya dengan hasil diskusi dan diagram kelompok. |

# Jurnal Proses — Tugas 1

> Isi jurnal ini selama proses diskusi berlangsung, bukan ditulis ulang rapi di akhir. Tulis dengan gaya bebas — poin diskusi, kebuntuan, perubahan pikiran.

## [22 September 2026 - diskusi 1]
- Peserta: Mochammad Raditya Ramadani Akbar, Danendra Adi Wicaksono, Arya Bariq Irawan, Rui Juniarta (hadir semua, tatap muka)
- Poin diskusi:
  - Membaca bersama skenario FoodGo dan gejalanya (lambat, timeout, server crash).
  - Menentukan 3 pitfall: network is reliable, tidak ada timeout (latency is zero), dan single point of failure.
  - Membahas bukti dan dampak dari masing-masing pitfall pada sistem FoodGo.
  - Membagi tugas: Raditya Pitfall 1, Danendra Pitfall 2, Arya Pitfall 3, Rui kesimpulan dan merapikan JURNAL.md.
- Perbedaan pendapat (jika ada): Tidak ada.

## [29 September 2026 — Diskusi 2 ]
- Peserta: Mochammad Raditya Ramadani Akbar, Danendra Adi Wicaksono, Arya Bariq Irawan, Rui Juniarta (hadir semua, tatap muka)
- Poin diskusi:
  - Membahas solusi desain untuk masing-masing pitfall.
  - Membahas retry dengan backoff untuk mengatasi gangguan jaringan.
  - Membahas timeout dan circuit breaker untuk mencegah service menunggu tanpa batas.
  - Membahas pemisahan modul menjadi service, penggunaan load balancer, dan message queue untuk mengurangi dampak single point of failure.
  - Membahas trade-off dari setiap solusi.
  - Menyusun kesimpulan kelompok dan menghubungkan hasil analisis dengan rencana Tugas 2 tentang arsitektur FoodGo menggunakan SOA.
- Perbedaan pendapat (jika ada): Tidak ada.

## Review Silang
- Belum dilakukan.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
|29 September 2026 | GPT | Meminta ide dan struktur pembahasan untuk analisis pitfall pada skenario FoodGo. | Memberikan beberapa ide awal mengenai struktur pembahasan pitfall, solusi, dan trade-off yang dapat dipertimbangkan. | Ide digunakan sebagai bahan diskusi, kemudian isi analisis dan tulisan akhir disusun sendiri oleh anggota kelompok. |

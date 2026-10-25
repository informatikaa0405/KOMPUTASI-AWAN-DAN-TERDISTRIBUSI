# Jurnal Proses — Tugas 5

## Implementasi Bully
Kendala saat mengisi TODO 1–4: Hal yang perlu dipahami dalam implementasi Bully Algorithm adalah komunikasi antar-node, proses pemilihan leader, pengiriman pesan, dan pendeteksian leader yang tidak merespons. Pada bagian "on_message", perlu dipahami fungsi pesan "ELECTION", "OK", dan "COORDINATOR". Pada bagian "start_election", perlu diperhatikan proses pengiriman pesan ke node dengan ID lebih tinggi dan waktu tunggu balasan. Pada bagian "declare_leader", node yang terpilih harus memberitahukan statusnya kepada node lain. Sementara itu, "monitor_leader" digunakan untuk memantau leader dan memulai pemilihan ulang ketika leader tidak merespons.

## Skenario 1: Start normal
- Leader yang terpilih: Node 5.
- Log/observasi: Pada awal pengujian, node 4 sempat menyatakan dirinya sebagai leader karena node 5 belum aktif ketika proses pemilihan berlangsung. Setelah node 5 dijalankan, node-node lain kembali melakukan proses pemilihan leader. Node 5 kemudian terpilih sebagai leader akhir karena memiliki ID tertinggi. Selama proses tersebut, sempat terjadi kondisi ketika node 4 dan node 5 sama-sama menyatakan diri sebagai leader. Berdasarkan log pengujian, seluruh node akhirnya mencatat node 5 sebagai leader sekitar pukul 17:14:51. Waktu dari node pertama yang menyatakan diri sebagai leader hingga seluruh node mencapai kesepakatan sekitar 12 detik.

## Skenario 2: Leader dimatikan
- Leader baru yang terpilih: Node 4.
- Berapa lama waktu sampai leader baru terdeteksi: Node 4 mendeteksi node 5 tidak merespons sekitar pukul 17:15:52 dan menyatakan diri sebagai leader sekitar pukul 17:15:56. Dengan demikian, waktu yang dibutuhkan hingga node 4 menjadi leader sekitar 4 detik. Seluruh node kemudian mencatat node 4 sebagai leader sekitar pukul 17:15:59, atau sekitar 7 detik sejak deteksi pertama.
- Log/observasi: Pengujian dilakukan dengan menghentikan terminal node 5 menggunakan "Ctrl+C". Setelah node 5 tidak merespons, node-node lain mendeteksi kegagalan leader dan memulai proses pemilihan ulang. Node 4 menjadi leader baru karena tidak menerima balasan "OK" dari node dengan ID lebih tinggi. Setelah pemberitahuan "COORDINATOR" diterima, node-node lain mengikuti node 4 sebagai leader dan kembali mengirimkan "PING" untuk memantau keberadaannya.

## Log Penggunaan AI (Level 2)

> Wajib diisi sesuai kebijakan Level 2 di [`../RUBRIK-UMUM.md`](../RUBRIK-UMUM.md). Tulis "Tidak memakai AI" pada baris pertama jika memang tidak dipakai. Hanya untuk brainstorming ide/outline — bukan untuk kode/analisis/teks akhir.

| Tanggal | Tool AI | Prompt yang diberikan | Ringkasan saran/ide AI | Bagaimana diolah jadi tulisan/kode sendiri |
|---|---|---|---|---|
|20 Oktober 2026| ChatGPT| Meminta ide untuk memahami dan mengerjakan tugas simulasi Bully Algorithm.| Memberikan beberapa ide mengenai konsep pemilihan leader, komunikasi antar-node, dan hal-hal yang perlu diperhatikan saat pengujian.| Ide yang relevan dipelajari dan dipertimbangkan, kemudian dikembangkan berdasarkan pemahaman sendiri serta hasil pengujian program.|

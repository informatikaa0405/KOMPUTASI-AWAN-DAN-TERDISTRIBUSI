# Tugas 5 (Pekan 5) — Koordinasi & Konsensus

Simulasi Bully Algorithm untuk memilih leader di antara 5 node virtual (5 proses Python terpisah, komunikasi lewat TCP socket di `localhost`), dikaitkan dengan kasus konflik urutan pesanan pada FoodGo.

## Cara Menjalankan

Buka 5 terminal, masuk ke folder `tugas-05-koordinasi-konsensus`, lalu jalankan satu perintah per terminal. Pengujian dilakukan di Windows, jadi memakai `py` (bukan `python3`).

```
py src/node.py --id 1 --port 5001 --peers 5002,5003,5004,5005
py src/node.py --id 2 --port 5002 --peers 5001,5003,5004,5005
py src/node.py --id 3 --port 5003 --peers 5001,5002,5004,5005
py src/node.py --id 4 --port 5004 --peers 5001,5002,5003,5005
py src/node.py --id 5 --port 5005 --peers 5001,5002,5003,5004
```

## Catatan Implementasi

Bagian infrastruktur jaringan di `src/node.py` (socket server, `handle_connection`, `send_message`) tidak diubah. Yang dilengkapi adalah empat bagian `# TODO`:

- `on_message`: menangani tiga pesan. `ELECTION` dibalas `OK` jika ID node ini lebih besar dari pengirim, lalu node ini memulai election sendiri. `OK` menandai ada node lebih tinggi yang hidup. `COORDINATOR` menyimpan pengirim sebagai leader.
- `start_election`: mengirim `ELECTION` ke semua peer ber-ID lebih besar, lalu menunggu `OK` selama `ELECTION_TIMEOUT` (2 detik). Kalau tidak ada `OK`, node menjadi leader. Kalau ada `OK`, node berhenti mencalonkan diri dan menunggu `COORDINATOR`; bila `COORDINATOR` tidak datang, election diulang.
- `declare_leader`: mengisi `leader_id` dengan ID sendiri lalu mengirim `COORDINATOR` ke semua peer.
- `monitor_leader`: tiap 3 detik mengirim `PING` ke leader. Jika koneksi gagal, leader dianggap mati, `leader_id` dikosongkan, dan election dimulai.

Tambahan di luar TODO: fungsi `log()` yang memberi jam pada setiap baris log (supaya waktu deteksi dan election bisa dibaca), serta flag `electing` supaya satu node tidak menjalankan dua election sekaligus.

## Analisis

### 1. Kenapa perlu leader

Pada kasus FoodGo, dua server mencatat urutan pesanan yang berbeda karena jam keduanya tidak sinkron. Misalnya server 1 mencatat pesanan A pukul 10:00:01, sedangkan jam server 2 tertinggal sehingga pesanan B yang sebenarnya masuk belakangan tercatat pukul 10:00:00. Kalau tiap server memutuskan urutan sendiri, antrean di kedua server bisa berbeda dan satu pesanan bisa diproses dua kali. Dengan satu leader, hanya satu node yang menentukan urutan antrean dan node lain mengikutinya, sehingga urutan tidak lagi bergantung pada jam lokal masing-masing.

### 2. Kenapa Bully, dan perbandingannya dengan Raft

Bully dipilih karena sederhana. Node ber-ID tertinggi yang masih hidup selalu menang, dan hanya ada tiga jenis pesan (`ELECTION`, `OK`, `COORDINATOR`), sehingga alurnya mudah diikuti di log. Untuk simulasi 5 node di satu laptop tanpa gangguan jaringan, ini sudah cukup.

Kelemahannya terlihat langsung di hasil pengujian. Saat start, node 1, 2, dan 3 sama-sama mengirim `ELECTION` ke node 4, dan node 4 membalas `OK` satu per satu. Jumlah pesan membengkak ketika banyak node memulai election bersamaan. Selain itu Bully bergantung pada timeout, dan pada saat start sempat ada dua node yang sama-sama menyatakan diri leader (lihat skenario 1). Dalam jaringan yang terbelah (partisi), tiap sisi bisa memilih leader sendiri dan keduanya merasa sah.

Raft lebih rumit karena memakai term, voting, dan mayoritas suara (quorum). Leader hanya sah jika didukung mayoritas node, jadi tidak mungkin ada dua leader sah pada saat yang sama. Harga yang dibayar adalah implementasi yang lebih berat (termasuk replikasi log). Untuk FoodGo di lingkungan nyata, Raft lebih cocok karena antrean pesanan harus konsisten dan tidak boleh diproses ganda. Untuk tugas ini Bully lebih tepat karena tujuannya memahami alur pemilihan leader.

### 3. Hasil dua skenario

**Skenario 1: start normal.** Kelima node dibuka satu per satu secara manual, sehingga waktu start tersebar sekitar 8 detik: node 1 pukul 17:14:30, node 4 sekitar 17:14:34, node 3 sekitar 17:14:37, dan node 5 sekitar 17:14:38. Karena node 5 belum menyala saat node 4 melakukan election, node 4 tidak mendapat `OK` dan menyatakan diri leader pada 17:14:39. Satu detik kemudian, 17:14:40, node 5 yang baru menyala juga menyatakan diri leader karena tidak punya peer yang lebih tinggi. Selama beberapa detik ada dua node yang sama-sama mengaku leader: node 1 sempat mencatat leader = 4 (17:14:40), lalu leader = 5 (17:14:41), sedangkan node 5 sendiri sempat menerima `COORDINATOR` dari node 4 pada 17:14:43.

Node ber-ID lebih kecil kemudian memulai election lagi (misalnya node 2 dan 3 pada 17:14:42-17:14:44). Node 5 membalas `OK` ke node-node itu lalu menyatakan diri leader lagi pada 17:14:47 dan mengirim `COORDINATOR` ulang. Mulai 17:14:48 node 1 sampai node 4 berturut-turut mencatat leader = 5 (node 1 pukul 17:14:48, node 2 pukul 17:14:49, node 3 pukul 17:14:50, node 4 pukul 17:14:51). Hasil akhirnya sesuai harapan: node 5 menjadi leader. Dari kondisi dua leader pertama (17:14:39) sampai semua node sepakat (17:14:51) butuh sekitar 12 detik. Satu putaran election tambahan di node 2 pada 17:14:41 kemungkinan terjadi karena `COORDINATOR` tiba hampir bersamaan dengan habisnya waktu tunggu.

**Skenario 2: leader mati.** Terminal node 5 dihentikan dengan Ctrl+C. Setiap node mengecek leader tiap 3 detik, jadi kematian node 5 terdeteksi dalam beberapa detik:

| Waktu | Kejadian |
|-------|----------|
| 17:15:52 | Node 4 mendeteksi node 5 tidak merespons, memulai election ke node 5 |
| 17:15:53 | Node 2 mendeteksi node 5 mati |
| 17:15:55 | Node 3 mendeteksi node 5 mati |
| 17:15:56 | Node 1 mendeteksi node 5 mati. Node 4 tidak mendapat `OK` dari siapa pun, menyatakan diri leader, dan mengirim `COORDINATOR` |
| 17:15:57 | Node 1 menerima `COORDINATOR` dari node 4 |
| 17:15:58 | Node 2 menerima `COORDINATOR` dari node 4 |
| 17:15:59 | Node 3 menerima `COORDINATOR` dari node 4 |
| 17:16:02 dst. | Node 2, 3, dan 1 mulai mengirim `PING` ke node 4 secara berkala |

Node 4 menjadi leader sekitar 4 detik setelah deteksi pertama (17:15:52 ke 17:15:56), dan seluruh node sudah mencatat leader = 4 sekitar 7 detik setelah deteksi pertama. Waktu 4 detik itu terdiri dari upaya koneksi ke node 5 yang gagal, ditambah `ELECTION_TIMEOUT` 2 detik. Node 1, 2, dan 3 membalas `OK` ke node-node di bawahnya tetapi tidak menang, karena masih ada node 4 yang hidup di atas mereka. Munculnya `PING` ke node 4 dari node 1, 2, dan 3 membuktikan bahwa semua node sekarang memantau node 4 sebagai leader yang baru. Leader baru terpilih otomatis tanpa campur tangan manual.

### Kaitan ke FoodGo

Dua hasil di atas langsung berkaitan dengan masalah urutan pesanan. Skenario 2 menunjukkan bahwa antrean pesanan bisa dilanjutkan oleh leader baru (node 4) tanpa perlu menyamakan jam. Skenario 1 menunjukkan risikonya: selama beberapa detik ada dua node yang mengaku leader, dan kalau pada saat itu keduanya sama-sama memproses pesanan, pesanan yang sama bisa diproses ganda. Karena itu, pada sistem nyata pesanan baru sebaiknya ditahan selama masa pemilihan sampai `COORDINATOR` diterima, dan untuk keamanan yang lebih kuat dipakai algoritma berbasis quorum seperti Raft.

## Bukti

Screenshot terminal node 1 sampai 5 untuk kedua skenario disimpan di folder `bukti/`. Log node 1-5 mencakup start normal (17:14:30-17:14:54) dan leader mati lalu re-election (17:15:52-17:16:07).

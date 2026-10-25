# Tugas 2 (Pekan 2) — Perancangan Arsitektur untuk FoodGo

**Gaya arsitektur yang dipilih:** Service-Oriented Architecture (SOA)

---

## 1. Pemilihan Gaya Arsitektur & Justifikasi

Kami memilih **SOA** sebagai gaya utama. Setiap fungsi bisnis FoodGo dipecah menjadi *service* mandiri yang mengekspos **kontrak antarmuka** (REST/RPC) dan berkomunikasi lewat lapisan integrasi (**API Gateway** + **Service Bus**).

**Kenapa SOA, bukan Pub-Sub murni?**

| Alasan | Penjelasan |
|---|---|
| Domain jelas terbagi | Pesanan, Pembayaran, Kurir/Notifikasi, dan Katalog Resto adalah kapabilitas bisnis yang berbeda dan dimiliki tim berbeda. Ini cocok dengan konsep *service* di SOA. |
| Butuh request-response | Banyak langkah butuh jawaban langsung (cek harga menu, proses bayar). Pub-Sub murni kurang natural untuk ini. |
| Kontrak antarmuka eksplisit | Tim kurir dan tim resto bisa bekerja terpisah selama kontrak API tidak berubah. |
| Cocok untuk migrasi dari monolit | Modul monolit yang ada dapat dipisah menjadi service satu per satu (*strangler pattern*). |

**Kombinasi:** inti sistem memakai SOA (komunikasi **sinkron**). Untuk langkah yang tidak perlu ditunggu (notifikasi, penugasan kurir), **Service Bus** meneruskan pesan secara **asinkron** (event). Ini sejalan dengan konsep *Enterprise Service Bus* di SOA, sehingga tetap satu gaya utama dengan dukungan asinkron di lapisan integrasi. Alasan kombinasi: notifikasi tidak boleh memperlambat atau menggagalkan proses pembayaran, dan jika layanan kurir sedang down, pesan tetap tersimpan di bus dan diproses setelah pulih.

---

## 2. Diagram Komponen

![Diagram komponen SOA FoodGo](diagram/komponen-soa.png)

> Sumber diagram: [`diagram/komponen-soa.drawio`](diagram/komponen-soa.drawio) (dibuat dengan draw.io)

**Keterangan:** garis solid = komunikasi sinkron (request-response), garis putus-putus ungu = komunikasi asinkron (event lewat bus). Setiap service punya database sendiri (tidak berbagi tabel).

### Tanggung jawab komponen

| Komponen | Tanggung jawab |
|---|---|
| **API Gateway** | Pintu masuk tunggal: autentikasi, routing, rate limiting. |
| **Order Service** | Membuat pesanan, mengelola status (`PENDING_PAYMENT → PAID → ACCEPTED → ON_DELIVERY → DONE`). |
| **Payment Service** | Membuat tagihan, memproses pembayaran via payment gateway, menerbitkan hasil pembayaran. |
| **Restaurant Catalog Service** | Menyimpan menu, harga, ketersediaan, dan jam buka resto. |
| **Courier & Notification Service** | Menugaskan kurir terdekat dan mengirim notifikasi ke resto, kurir, dan pelanggan. |
| **Service Bus** | Meneruskan event antar service secara asinkron, menyimpan pesan sementara (*durable queue*), dan melakukan retry. |

---

## 3. Skenario End-to-End: Pelanggan Pesan → Bayar → Resto Notifikasi → Kurir Ditugaskan

![Sequence diagram skenario end-to-end](diagram/sequence-skenario.png)

> Sumber diagram: [`diagram/sequence-skenario.drawio`](diagram/sequence-skenario.drawio) (dibuat dengan draw.io)

### Ringkasan jenis komunikasi

| # | Dari → Ke | Jenis | Alasan |
|---|---|---|---|
| 1 | Pelanggan → Gateway → Order | Sinkron, request-response | Pelanggan perlu `order_id` langsung. |
| 2 | Order → Catalog | Sinkron, request-response | Harga dan ketersediaan harus valid sebelum pesanan dibuat. |
| 3 | Pelanggan → Payment → Payment Gateway | Sinkron, request-response | Hasil bayar harus diketahui saat itu juga. |
| 4 | Payment → Order | Sinkron, request-response | Payment Service mengambil total tagihan yang valid dari Order Service, bukan dari klien. |
| 5 | Payment → Bus → Order | Asinkron, event | Order Service tidak perlu memblokir proses pembayaran. |
| 6 | Order → Bus → Courier/Notif | Asinkron, event | Notifikasi dan penugasan kurir boleh tertunda sebentar, tidak boleh menggagalkan transaksi. |
| 7 | Resto → Gateway → Order | Sinkron, request-response | Resto butuh konfirmasi bahwa penerimaan pesanan tercatat. |

---

## 4. Analisis Tertulis

### 4.1 Masalah pada Tugas 1 (monolit)

Seluruh modul (pesanan, pembayaran, notifikasi kurir, katalog) berjalan dalam **satu proses dan satu unit deploy**. Akibatnya:

- **Coupling tinggi pada waktu deploy:** perubahan kecil di modul kurir memaksa seluruh aplikasi restart, sehingga pesanan dan pembayaran ikut down.
- **Coupling pada kode & data:** modul saling memanggil langsung dan berbagi database yang sama, sehingga perubahan skema di satu modul bisa merusak modul lain.
- **Kegagalan menjalar:** bug atau memory leak di satu modul bisa menjatuhkan seluruh sistem.
- **Tidak bisa diskalakan sebagian:** saat jam makan siang, hanya Order dan Katalog yang padat, tetapi semua modul harus ikut diperbanyak.
- **Tim saling menghambat:** tim kurir dan tim resto harus berbagi jadwal rilis.

### 4.2 Bagaimana SOA mengatasinya

| Masalah monolit | Solusi dengan SOA |
|---|---|
| Deploy satu paket, downtime total | Setiap service di-deploy **independen**. Deploy ulang Courier Service tidak menyentuh Order/Payment. |
| Modul saling memanggil langsung | Interaksi hanya lewat **kontrak API** yang terdefinisi. Implementasi internal bebas berubah selama kontrak tetap. |
| Database bersama | **Database per service**. Data diakses lewat API, bukan lewat tabel. |
| Kegagalan menjalar | **Isolasi kegagalan.** Jika Courier Service mati, pesanan dan pembayaran tetap jalan; event menunggu di bus lalu diproses setelah pulih. |
| Skala menyeluruh | **Skala per service**, misalnya hanya Order dan Catalog saat jam sibuk. |
| Tim saling menghambat | Tim kurir dan tim resto memiliki service dan siklus rilis sendiri. |

Contoh konkret: tim kurir ingin merilis algoritma penugasan baru. Mereka hanya deploy Courier & Notification Service. Selama proses itu, event `OrderAccepted` tertahan di bus dan diproses begitu service naik kembali. Pelanggan tetap bisa memesan dan membayar tanpa gangguan.

### 4.3 Trade-off SOA

| Trade-off | Dampak | Mitigasi |
|---|---|---|
| **Service Bus / Gateway menjadi single point of failure dan potensi bottleneck** | Jika bus atau gateway down, seluruh komunikasi terganggu. | Jalankan secara **cluster / redundan**, health check, dan auto-scaling. |
| **Latensi bertambah** | Panggilan jaringan antar service lebih lambat dari pemanggilan fungsi lokal. | Cache data katalog, timeout yang jelas, dan minimalkan rantai panggilan sinkron. |
| **Konsistensi data terdistribusi** | Tidak ada satu transaksi database lintas service (misalnya pembayaran sukses tetapi status order belum berubah). | Pola **Saga** dengan kompensasi, status eksplisit, dan **idempotency key** agar event yang terkirim ganda tidak diproses dua kali. |
| **Debugging lebih sulit** | Satu skenario melewati banyak service, dan bagian asinkron tidak berurutan secara linear. | **Correlation ID / distributed tracing** (mis. OpenTelemetry), log terpusat, dan dead-letter queue. |
| **Kompleksitas operasional** | Banyak service berarti banyak deployment, monitoring, dan konfigurasi. | CI/CD per service, containerization, dan observability terpusat. |
| **Manajemen versi kontrak** | Perubahan API bisa merusak service lain. | **Versioning API** (`/v1`, `/v2`), backward compatibility, dan contract testing. |
| **Ketergantungan sinkron** | Order Service tergantung pada Catalog Service saat pemesanan. | **Circuit breaker**, retry dengan backoff, dan fallback (mis. data menu dari cache). |

### 4.4 Kesimpulan

SOA menjawab inti masalah Tugas 1: modul kurir dan resto tidak lagi saling menggangu saat deploy, karena masing-masing menjadi service independen dengan kontrak yang jelas. Komunikasi sinkron dipakai pada langkah yang butuh jawaban langsung, sedangkan Service Bus asinkron dipakai untuk notifikasi dan penugasan kurir agar proses inti tetap cepat dan tahan gangguan. Harga yang dibayar adalah kompleksitas operasional, konsistensi data terdistribusi, dan kebutuhan observability yang lebih baik, yang bisa diredam dengan pola Saga, idempotency, circuit breaker, dan distributed tracing.

---

## 5. Struktur Submission

```
tugas-02-perancangan-arsitektur/
├── README.md                    # Analisis tertulis (file ini)
├── JURNAL.md                    # Jurnal pengerjaan kelompok
└── diagram/                     # File diagram
    ├── komponen-soa.drawio
    ├── komponen-soa.png
    ├── sequence-skenario.drawio
    └── sequence-skenario.png
```

"""
Tugas 3 - Simulasi Pesanan Masuk dengan Multithreading

Mode dipilih lewat environment variable USE_LOCK:
  USE_LOCK=1 (default) -> increment dilindungi threading.Lock  (hasil selalu benar)
  USE_LOCK=0           -> tanpa lock, race condition sengaja dibiarkan (hasil meleset)
"""

import os
import threading
import random
import time

NUM_ORDERS = 100        # jumlah pesanan simulasi yang masuk
NUM_WORKERS = 10        # jumlah thread pekerja

USE_LOCK = os.environ.get("USE_LOCK", "1") != "0"

# Counter bersama untuk menghitung total pesanan yang berhasil diproses.
# Sengaja rawan race condition jika diakses tanpa proteksi.
processed_count = 0

# TODO 1 (selesai): Lock untuk melindungi `processed_count`.
lock = threading.Lock()


def process_order(order_id: int) -> None:
    """Proses satu pesanan. Dipanggil oleh tiap thread pekerja."""
    global processed_count

    # Simulasikan kerja nyata (mis. validasi, hitung total harga)
    time.sleep(random.uniform(0.001, 0.01))

    # TODO 2 (selesai): increment counter.
    # Operasi `+= 1` dipecah menjadi baca -> (jeda) -> tulis agar jendela
    # race condition cukup lebar untuk terlihat. time.sleep(0) melepas GIL
    # sehingga thread lain bisa menyela di antara baca dan tulis.
    if USE_LOCK:
        with lock:
            current = processed_count
            time.sleep(0)
            processed_count = current + 1
    else:
        current = processed_count      # baca nilai lama
        time.sleep(0)                  # thread lain bisa menyela di sini
        processed_count = current + 1  # tulis: bisa menimpa update thread lain


def worker(order_ids: list) -> None:
    """Satu thread pekerja memproses sekumpulan order_id."""
    for order_id in order_ids:
        process_order(order_id)


def main() -> None:
    order_ids = list(range(1, NUM_ORDERS + 1))

    print(f"Mode: {'DENGAN lock' if USE_LOCK else 'TANPA lock'} | "
          f"{NUM_ORDERS} pesanan, {NUM_WORKERS} thread")

    # TODO 3 (selesai): bagi order ke NUM_WORKERS bagian (round-robin),
    # satu Thread per bagian, start semua dulu, baru join (lihat loop di bawah).
    threads = []
    for i in range(NUM_WORKERS):
        bagian = order_ids[i::NUM_WORKERS]
        t = threading.Thread(target=worker, args=(bagian,), name=f"worker-{i + 1}")
        threads.append(t)

    start = time.perf_counter()
    for t in threads:       # start SEMUA dulu agar benar-benar konkuren
        t.start()

    for t in threads:
        t.join()
    durasi = time.perf_counter() - start

    print(f"Total pesanan diproses: {processed_count} (seharusnya {NUM_ORDERS})")
    print(f"Waktu: {durasi:.3f} detik")
    if processed_count != NUM_ORDERS:
        print("RACE CONDITION TERDETEKSI - lengkapi TODO 1 & TODO 2 dengan Lock!")


if __name__ == "__main__":
    main()

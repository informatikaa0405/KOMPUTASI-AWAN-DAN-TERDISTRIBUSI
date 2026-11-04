"""
Tugas 6 - Simulasi Chord DHT (single-process, tanpa jaringan sungguhan)

Fungsi hashing & struktur data ring sudah disediakan.
Lengkapi TODO untuk lookup(), join(), dan leave().
"""

import hashlib

M_BITS = 8               # ruang identifier 0..255 (disederhanakan dari Chord asli yang pakai 160-bit)
RING_SIZE = 2 ** M_BITS


def hash_id(key: str) -> int:
    """Hash string (ID node atau ID kurir) ke ruang identifier 0..RING_SIZE-1."""
    digest = hashlib.sha1(key.encode()).digest()
    return int.from_bytes(digest, "big") % RING_SIZE


class ChordRing:
    def __init__(self):
        # node_id (hasil hash) -> alamat IP node tersebut
        self.nodes: dict[int, str] = {}
        # key kurir (hasil hash) -> IP kurir yang disimpan node yang bertanggung jawab
        self.data: dict[int, tuple[str, str]] = {}  # hash -> (kurir_id, ip_kurir)
        # key kurir (hasil hash) -> node_id yang SAAT INI memegang key tersebut.
        # (Tambahan: dipakai supaya perpindahan tanggung jawab saat join/leave
        # benar-benar tercatat, bukan hanya dihitung ulang.)
        self.holder: dict[int, int] = {}
        # nama node -> node_id, hanya untuk memperindah log
        self._names: dict[int, str] = {}

    # ---------- util log ----------
    def _label(self, node_id: int) -> str:
        return f"{self._names.get(node_id, '?')}(id={node_id}, {self.nodes.get(node_id, '-')})"

    def _transfer(self, keys: list[int], dari: int | None, ke: int, alasan: str):
        """Pindahkan penanggung jawab `keys` ke node `ke` dan cetak lognya."""
        if not keys:
            print("    (tidak ada key yang berpindah tanggung jawab)")
            return
        for k in sorted(keys):
            kurir_id, ip = self.data[k]
            asal = self._label(dari) if dari is not None else "-"
            print(f"    {kurir_id} (hash={k}, ip={ip}): {asal} -> {self._label(ke)}  [{alasan}]")
            self.holder[k] = ke

    # ---------- operasi ring ----------
    def join(self, node_name: str, node_ip: str):
        """Tambahkan node baru ke ring. Pindahkan data yang seharusnya
        menjadi tanggung jawab node baru ini dari successor lamanya."""
        node_id = hash_id(node_name)
        print(f"[JOIN] Node '{node_name}' (id={node_id}) bergabung, alamat {node_ip}")

        if node_id in self.nodes:
            # Dua nama berbeda bisa bertabrakan hash-nya di ruang 0..255.
            raise ValueError(
                f"Tabrakan hash: id={node_id} sudah dipakai {self._label(node_id)}. "
                "Gunakan nama node lain."
            )

        # TODO 2: successor LAMA dicari SEBELUM node baru dimasukkan ke self.nodes
        # (sama artinya dengan mengecualikan node_id baru dari pencarian).
        successor_lama = self.find_successor(node_id) if self.nodes else None

        # TODO 1: masukkan node ke ring.
        self.nodes[node_id] = node_ip
        self._names[node_id] = node_name

        # TODO 3: key yang dulu dipegang successor lama, tapi sekarang successor-nya
        # adalah node baru, berpindah ke node baru. Memakai find_successor() (bukan
        # perbandingan "hash <= node_id") supaya kasus wrap-around ikut benar.
        if successor_lama is not None:
            pindah = [
                k for k, h in self.holder.items()
                if h == successor_lama and self.find_successor(k) == node_id
            ]
            self._transfer(pindah, successor_lama, node_id, "node baru menjadi successor key")
        else:
            print("    (ring sebelumnya kosong, tidak ada data untuk dipindah)")

    def leave(self, node_name: str):
        """Keluarkan sebuah node dari ring. Data yang dipegangnya harus
        berpindah ke successor-nya."""
        node_id = hash_id(node_name)
        print(f"[LEAVE] Node '{node_name}' (id={node_id}) keluar dari ring")

        if node_id not in self.nodes:
            raise ValueError(f"Node '{node_name}' (id={node_id}) tidak ada di ring")

        # Catat key yang dipegang node ini SEBELUM dihapus.
        dipegang = [k for k, h in self.holder.items() if h == node_id]
        label_lama = self._label(node_id)

        # TODO 4: hapus node dari ring.
        del self.nodes[node_id]

        if not self.nodes:
            print(f"    Ring kosong: {len(dipegang)} mapping hilang (tidak ada replika).")
            for k in dipegang:
                del self.holder[k]
            self._names.pop(node_id, None)
            return

        # TODO 5: successor baru untuk tiap key = find_successor() pada ring tanpa node ini.
        for k in sorted(dipegang):
            baru = self.find_successor(k)
            kurir_id, ip = self.data[k]
            print(f"    {kurir_id} (hash={k}, ip={ip}): {label_lama} -> {self._label(baru)}  [node keluar]")
            self.holder[k] = baru
        if not dipegang:
            print("    (node ini tidak memegang key apa pun)")
        self._names.pop(node_id, None)

    def find_successor(self, key_hash: int) -> int:
        """Cari node_id dengan nilai hash TERKECIL yang >= key_hash
        (successor menurut aturan Chord). Jika tidak ada, wrap-around
        ke node dengan hash terkecil di ring (karena ring melingkar)."""
        if not self.nodes:
            raise LookupError("Ring kosong, tidak ada node")
        urut = sorted(self.nodes.keys())
        for node_id in urut:
            if node_id >= key_hash:
                return node_id
        return urut[0]  # wrap-around: key lebih besar dari semua node

    def register_kurir(self, kurir_id: str, ip_kurir: str):
        """Simpan mapping ID Kurir -> IP di node yang bertanggung jawab.
        Memanggil lagi dengan IP baru = memperbarui IP (kasus kurir pindah jaringan)."""
        key_hash = hash_id(kurir_id)
        if key_hash in self.data and self.data[key_hash][0] != kurir_id:
            raise ValueError(
                f"Tabrakan hash kurir: '{kurir_id}' dan '{self.data[key_hash][0]}' sama-sama hash={key_hash}"
            )
        node_id = self.find_successor(key_hash)
        self.data[key_hash] = (kurir_id, ip_kurir)
        self.holder[key_hash] = node_id
        print(f"[REGISTER] {kurir_id} (hash={key_hash}) -> {ip_kurir}, disimpan di {self._label(node_id)}")

    def lookup(self, kurir_id: str) -> str | None:
        """Cari alamat IP terkini untuk sebuah ID Kurir."""
        key_hash = hash_id(kurir_id)
        node_id = self.find_successor(key_hash)
        entri = self.data.get(key_hash)
        if entri is None or entri[0] != kurir_id or self.holder.get(key_hash) != node_id:
            return None
        return entri[1]

    def lookup_verbose(self, kurir_id: str) -> str | None:
        """Sama seperti lookup(), tapi mencetak node penanggung jawabnya."""
        key_hash = hash_id(kurir_id)
        node_id = self.find_successor(key_hash)
        ip = self.lookup(kurir_id)
        print(f"  {kurir_id} (hash={key_hash}) -> {self._label(node_id)} -> {ip}")
        return ip

    def tampilkan_ring(self):
        print("  Ring (urut naik):")
        for node_id in sorted(self.nodes):
            isi = sorted(k for k, h in self.holder.items() if h == node_id)
            daftar = ", ".join(f"{self.data[k][0]}(h={k})" for k in isi) or "-"
            print(f"    {self._label(node_id)}  memegang: {daftar}")


def main():
    ring = ChordRing()

    print("=== Skenario awal: 4 node bergabung ===")
    ring.join("node-jakarta-1", "10.0.0.1")
    ring.join("node-jakarta-2", "10.0.0.2")
    ring.join("node-bandung-1", "10.0.0.3")
    ring.join("node-surabaya-1", "10.0.0.4")

    print("\n=== Daftarkan beberapa kurir ===")
    ring.register_kurir("kurir-001", "192.168.1.10")
    ring.register_kurir("kurir-002", "192.168.1.11")
    ring.register_kurir("kurir-003", "192.168.1.12")
    ring.register_kurir("kurir-005", "192.168.1.14")  # hash 175 -> node 177
    ring.register_kurir("kurir-006", "192.168.1.15")  # hash 217 > semua node -> wrap-around

    print("\n--- Lookup sebelum perubahan topologi ---")
    ring.lookup_verbose("kurir-001")
    ring.lookup_verbose("kurir-002")
    ring.lookup_verbose("kurir-006")
    ring.tampilkan_ring()

    print("\n=== Node baru bergabung (tidak mengambil key apa pun) ===")
    ring.join("node-medan-1", "10.0.0.5")
    ring.lookup_verbose("kurir-001")

    print("\n=== Node baru bergabung (mengambil alih kurir-001) ===")
    ring.join("node-semarang-1", "10.0.0.6")
    ring.lookup_verbose("kurir-001")
    ring.tampilkan_ring()

    print("\n=== Sebuah node keluar (wrap-around: kurir-005 pindah ke node terkecil) ===")
    ring.leave("node-jakarta-1")
    ring.lookup_verbose("kurir-001")
    ring.lookup_verbose("kurir-002")
    ring.lookup_verbose("kurir-005")
    ring.tampilkan_ring()

    print("\n=== Node pemegang kurir-001 keluar ===")
    ring.leave("node-semarang-1")
    ring.lookup_verbose("kurir-001")
    ring.tampilkan_ring()

    print("\n=== Kurir pindah jaringan: IP berubah, ID tetap ===")
    ring.register_kurir("kurir-001", "172.16.5.77")
    ring.lookup_verbose("kurir-001")

    print("\n=== Kurir tidak dikenal ===")
    ring.lookup_verbose("kurir-999")


if __name__ == "__main__":
    main()

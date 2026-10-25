"""
Tugas 5 - Simulasi Node untuk Bully Algorithm

Contoh menjalankan (5 terminal terpisah, Windows):
    py src/node.py --id 1 --port 5001 --peers 5002,5003,5004,5005
    py src/node.py --id 2 --port 5002 --peers 5001,5003,5004,5005
    ... dst untuk id 3, 4, 5
"""

import argparse
import socket
import threading
import time

ELECTION_TIMEOUT = 2.0  # detik menunggu balasan OK sebelum menyatakan diri leader


def log(node_id, text):
    """Cetak log dengan jam supaya waktu deteksi dan election bisa dibaca."""
    print(f"{time.strftime('%H:%M:%S')} [Node {node_id}] {text}", flush=True)


class Node:
    def __init__(self, node_id: int, port: int, peers: dict):
        self.node_id = node_id
        self.port = port
        # peers: dict {peer_id: peer_port} untuk semua node LAIN
        self.peers = peers
        self.leader_id = None
        self.lock = threading.Lock()
        self.ok_event = threading.Event()           # diset saat menerima "OK"
        self.coordinator_event = threading.Event()  # diset saat menerima "COORDINATOR"
        self.electing = False                       # cegah dua election sekaligus

    # ---------- Infrastruktur jaringan (tidak diubah) ----------

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(("localhost", self.port))
        server.listen()
        log(self.node_id, f"Listening di port {self.port}")
        while True:
            conn, _ = server.accept()
            threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()

    def handle_connection(self, conn: socket.socket):
        with conn:
            data = conn.recv(1024).decode()
            if not data:
                return
            sender_id, msg_type = data.split(":")
            self.on_message(int(sender_id), msg_type)

    def send_message(self, target_port: int, msg_type: str) -> bool:
        """Kirim pesan ke node lain. Return False jika node target tidak merespons (dianggap mati)."""
        try:
            with socket.create_connection(("localhost", target_port), timeout=1.0) as s:
                s.sendall(f"{self.node_id}:{msg_type}".encode())
            return True
        except (ConnectionRefusedError, socket.timeout, OSError):
            return False

    # ---------- Logika Bully Algorithm ----------

    def on_message(self, sender_id: int, msg_type: str):
        """Dipanggil setiap kali node ini menerima pesan dari node lain."""
        if msg_type == "ELECTION":
            log(self.node_id, f"Menerima ELECTION dari node {sender_id}")
            if self.node_id > sender_id:
                self.send_message(self.peers[sender_id], "OK")
                # start_election memblokir (menunggu timeout), jalankan di thread sendiri
                threading.Thread(target=self.start_election, daemon=True).start()
        elif msg_type == "OK":
            log(self.node_id, f"Menerima OK dari node {sender_id} (ada node lebih tinggi yang hidup)")
            self.ok_event.set()
        elif msg_type == "COORDINATOR":
            with self.lock:
                self.leader_id = sender_id
            self.coordinator_event.set()
            log(self.node_id, f"Menerima COORDINATOR dari node {sender_id}, leader = {sender_id}")
        elif msg_type == "PING":
            pass  # cukup berhasil terkoneksi; tidak perlu balasan

    def start_election(self):
        """Dipanggil saat node ini mendeteksi leader tidak ada / tidak merespons."""
        while True:
            with self.lock:
                if self.electing:
                    return
                self.electing = True
            try:
                self.ok_event.clear()
                self.coordinator_event.clear()
                higher_peers = {pid: p for pid, p in self.peers.items() if pid > self.node_id}
                log(self.node_id, f"Memulai election ke peer lebih tinggi: {list(higher_peers)}")

                for pid, port in higher_peers.items():
                    self.send_message(port, "ELECTION")

                if not higher_peers or not self.ok_event.wait(ELECTION_TIMEOUT):
                    # tidak ada OK dalam batas waktu -> node ini menang
                    self.declare_leader()
                    return

                # ada node lebih tinggi yang hidup: berhenti mencalonkan diri, tunggu COORDINATOR
                log(self.node_id, "Ada node lebih tinggi, menunggu COORDINATOR")
                if self.coordinator_event.wait(ELECTION_TIMEOUT * 2):
                    return
                log(self.node_id, "COORDINATOR tidak datang, election diulang")
            finally:
                with self.lock:
                    self.electing = False

    def declare_leader(self):
        """Node ini menyatakan dirinya leader dan memberi tahu semua node lain."""
        with self.lock:
            self.leader_id = self.node_id
        log(self.node_id, "Tidak ada OK, saya menjadi LEADER. Kirim COORDINATOR ke semua node")
        for pid, port in self.peers.items():
            self.send_message(port, "COORDINATOR")

    def monitor_leader(self):
        """Loop periodik: cek apakah leader masih hidup, trigger election jika mati."""
        while True:
            time.sleep(3)
            with self.lock:
                leader = self.leader_id
            if leader is None or leader == self.node_id:
                continue
            log(self.node_id, f"PING ke leader node {leader}")
            if not self.send_message(self.peers[leader], "PING"):
                log(self.node_id, f"Leader node {leader} tidak merespons, dianggap mati")
                with self.lock:
                    if self.leader_id == leader:
                        self.leader_id = None
                self.start_election()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--id", type=int, required=True)
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--peers", type=str, required=True,
                        help="daftar port peer dipisah koma, mis. 5002,5003,5004,5005")
    args = parser.parse_args()

    # Konvensi port: id N selalu di port 5000+N
    peer_ports = [int(p) for p in args.peers.split(",")]
    peers = {port - 5000: port for port in peer_ports}

    node = Node(args.id, args.port, peers)

    threading.Thread(target=node.start_server, daemon=True).start()
    threading.Thread(target=node.monitor_leader, daemon=True).start()

    time.sleep(1)  # beri waktu node lain start dulu sebelum election awal
    node.start_election()

    while True:
        time.sleep(60)


if __name__ == "__main__":
    main()

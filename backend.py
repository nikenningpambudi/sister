import grpc
from concurrent import futures
import mysql.connector
import common_pb2
import common_pb2_grpc


class BackendService(common_pb2_grpc.BackendServicer):
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="localhost", user="root", password="", database="kasir_terdistribusi"
        )

    def ProsesTransaksi(self, request, context):
        cursor = self.conn.cursor(dictionary=True)

        # Validasi stok
        cursor.execute("SELECT stok, harga FROM barang WHERE id_barang = %s", (request.id_barang,))
        barang = cursor.fetchone()
        if not barang or barang["stok"] < request.jumlah:
            return common_pb2.TransactionResponse(
                success=False, message="Stok tidak cukup", total_harga=0, diskon=0
            )

        # Hitung total dan diskon
        total_harga = barang["harga"] * request.jumlah
        # diskon = int(total_harga * 0.1) if total_harga > 100000 else 0
        # total_harga -= diskon

        # Simpan transaksi
        cursor.execute(
            "INSERT INTO transaksi (id_barang, jumlah, total_harga) VALUES (%s, %s, %s)",
            (request.id_barang, request.jumlah, total_harga),
        )
        self.conn.commit()

        # Kirim permintaan ke Stok Barang untuk pembaruan stok
        with grpc.insecure_channel("localhost:50052") as channel:
            stub = common_pb2_grpc.StokBarangStub(channel)
            stok_request = common_pb2.StokUpdateRequest(
                id_barang=request.id_barang, jumlah_terjual=request.jumlah
            )
            stok_response = stub.UpdateStok(stok_request)
            if not stok_response.success:
                return common_pb2.TransactionResponse(
                    success=False, message=stok_response.message, total_harga=0
                )

        return common_pb2.TransactionResponse(
            success=True, message="Transaksi berhasil", total_harga=total_harga
        )

    def AmbilLaporan(self, request, context):
        cursor = self.conn.cursor(dictionary=True)
        query = "SELECT * FROM transaksi"

        if request.periode == "harian":
            query += " WHERE DATE(waktu) = CURDATE()"
        elif request.periode == "mingguan":
            query += " WHERE YEARWEEK(waktu, 1) = YEARWEEK(CURDATE(), 1)"

        cursor.execute(query)
        transaksi = cursor.fetchall()
        laporan = [f"ID Barang: {t['id_barang']}, Jumlah: {t['jumlah']}, Total: {t['total_harga']}" for t in transaksi]
        return common_pb2.LaporanResponse(laporan=laporan)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    common_pb2_grpc.add_BackendServicer_to_server(BackendService(), server)
    server.add_insecure_port("[::]:50051")
    print("Backend running on port 50051...")
    print("Berjalan pada node 1")
    server.start()
    server.wait_for_termination()


if __name__ == "__main__":
    serve()

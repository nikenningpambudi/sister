import grpc
import common_pb2
import common_pb2_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = common_pb2_grpc.BackendStub(channel)

        print("Pilih jenis laporan:")
        print("1. Harian")
        print("2. Mingguan")

        pilihan = input("Masukkan pilihan (1/2): ")
        periode = "harian" if pilihan == "1" else "mingguan"

        # Kirim permintaan laporan
        request = common_pb2.LaporanRequest(periode=periode)
        response = stub.AmbilLaporan(request)

        if response.laporan:
            print(f"Laporan {periode.capitalize()}:")
            for item in response.laporan:
                print(item)
        else:
            print(f"Tidak ada transaksi pada periode {periode.capitalize()}.")


if __name__ == "__main__":
    main()

import grpc
import common_pb2
import common_pb2_grpc


def main():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = common_pb2_grpc.BackendStub(channel)

        # Input transaksi
        transaksi = common_pb2.TransactionRequest(id_barang=1, jumlah=2)
        response = stub.ProsesTransaksi(transaksi)
        print(f"Transaksi: {response.message}, Total Harga: {response.total_harga}, Diskon: {response.diskon}")


if __name__ == "__main__":
    main()

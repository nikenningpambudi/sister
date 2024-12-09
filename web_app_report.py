from flask import Flask, render_template, request, redirect, url_for
import grpc
import common_pb2
import common_pb2_grpc

app = Flask(__name__, template_folder='templates2')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        periode = request.form['periode']
        
        # Redirect to the result page with the selected period
        return redirect(url_for('hasil_laporan', periode=periode, page=1))

    return render_template('report.html')

@app.route('/hasil_laporan')
def hasil_laporan():
    periode = request.args.get('periode')
    current_page = int(request.args.get('page', 1))
    
    # Connect to gRPC server (Backend)
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = common_pb2_grpc.BackendStub(channel)
        laporan_request = common_pb2.LaporanRequest(periode=periode)
        response = stub.AmbilLaporan(laporan_request)
    
    laporan = response.laporan
    items_per_page = 10
    total_pages = min((len(laporan) // items_per_page) + (1 if len(laporan) % items_per_page > 0 else 0), 3)
    
    # Paginate laporan list (slice the report list for the current page)
    start = (current_page - 1) * items_per_page
    end = start + items_per_page
    laporan = laporan[start:end]
    
    return render_template('hasil_laporan.html', laporan=laporan, total_pages=total_pages, current_page=current_page)

if __name__ == "__main__":
    app.run(host="localhost", port=50054, debug=True)

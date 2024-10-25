from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from fuzzywuzzy import fuzz, process
import pandas as pd

app = Flask(__name__)

# Konfigurasi lokasi folder penyimpanan dan ekstensi yang diizinkan
IMAGE_FOLDER = os.path.join('static', 'images')
UPLOAD_FOLDER = os.path.join('static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'xlsx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Data poster dengan kata kunci (tanpa ekstensi)
image_data = {
    'penambalan gigi': ['poster_imunisasi1', 'poster_imunisasi2', 'poster_covid1', 'poster_covid2', '4-revisi', '5-revisi'],
    'covid': ['poster_covid1', 'poster_covid2'],
    'jumpscare': ['abi'],
    # 'dokumen': ['MAKALAH','KUITANSI','LAPORANMAGANG','timeline_project','PKB']
}
# untuk dictionary dokumen tidak perlu menambahkan filenya di dalam dictionary dia bisa membaca langsung di folder uploads

# Fungsi untuk memeriksa ekstensi file yang diunggah
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Fungsi untuk mencari gambar berdasarkan kata kunci dengan fuzzy search
def find_images(keyword):
    found_images = []
    # Cari kata kunci yang mirip dalam image_data menggunakan fuzzy matching
    possible_matches = process.extract(keyword, image_data.keys(), limit=2, scorer=fuzz.ratio)
    
    # Ambil hasil terbaik yang memiliki rasio kecocokan lebih dari 50%
    for match, score in possible_matches:
        if score > 50:  # Threshold minimal kecocokan
            for image_name in image_data[match]:
                # Cek file dengan ekstensi .jpg dan .png
                for ext in ['jpg', 'png']:
                    image_path = os.path.join(IMAGE_FOLDER, f"{image_name}.{ext}")
                    if os.path.exists(image_path):
                        found_images.append(f"{image_name}.{ext}")
    return found_images

# Fungsi untuk membaca file Excel dan mengonversinya menjadi tabel HTML
def read_excel(file_path):
    df = pd.read_excel(file_path)
    return df.to_html(classes='table table-striped')

# Rute utama untuk halaman pencarian dan unggah file
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form['search'].lower()
        return redirect(url_for('search_results', search_term=search_term))
    return render_template('index.html')

# Rute untuk menampilkan hasil pencarian di halaman baru
@app.route('/results/<search_term>')
def search_results(search_term):
    # Pencarian gambar
    images = find_images(search_term)
    
    # Kondisi untuk memutuskan apakah ada gambar yang ditemukan
    not_found = len(images) == 0

    # Cek apakah pencarian dilakukan untuk dokumen
    # Jika pencarian bukan untuk dokumen, jangan tampilkan dokumen
    show_documents = search_term.lower() in ['dokumen', 'document']

    # Ambil daftar file dokumen jika 'show_documents' adalah True
    file_previews = []
    if show_documents:
        uploaded_files = os.listdir(app.config['UPLOAD_FOLDER'])
        for filename in uploaded_files:
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file_extension = filename.rsplit('.', 1)[1].lower()
            content = None

            if file_extension in ['pdf', 'docx', 'xlsx']:
                # Tampilkan jenis file sesuai tipe
                file_previews.append({'filename': filename, 'type': file_extension})

    return render_template('results.html', images=images, file_previews=file_previews, search_term=search_term, not_found=not_found)


# Rute untuk mengunduh file
@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    # Buat folder penyimpanan jika belum ada
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)

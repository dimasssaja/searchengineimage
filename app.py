from flask import Flask, render_template, request, redirect, url_for
import os
from fuzzywuzzy import fuzz, process

app = Flask(__name__)

# Lokasi folder gambar
IMAGE_FOLDER = os.path.join('static', 'images')

# Data poster dengan kata kunci (tanpa ekstensi)
image_data = {
    'penambalan gigi': ['poster_imunisasi1', 'poster_imunisasi2', 'poster_covid1', 'poster_covid2', '4-revisi', '5-revisi'],
    'covid': ['poster_covid1', 'poster_covid2'],
    'jumpscare': ['abi'],
}

# Fungsi untuk mencari gambar berdasarkan kata kunci dengan fuzzy search
def find_images(keyword):
    found_images = []
    # Cari kata kunci yang mirip dalam image_data menggunakan fuzzy matching
    possible_matches = process.extract(keyword, image_data.keys(), limit=2, scorer=fuzz.ratio)
    
    # Ambil hasil terbaik yang memiliki rasio kecocokan lebih dari 60%
    for match, score in possible_matches:
        if score > 60:  # Threshold minimal kecocokan
            for image_name in image_data[match]:
                # Cek file dengan ekstensi .jpg dan .png
                for ext in ['jpg', 'png']:
                    image_path = os.path.join(IMAGE_FOLDER, f"{image_name}.{ext}")
                    if os.path.exists(image_path):
                        found_images.append(f"{image_name}.{ext}")
    return found_images

# Rute utama untuk halaman pencarian
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_term = request.form['search'].lower()
        return redirect(url_for('search_results', search_term=search_term))
    return render_template('index.html')

# Rute untuk menampilkan hasil pencarian di halaman baru
@app.route('/results/<search_term>')
def search_results(search_term):
    images = find_images(search_term)
    if images:
        return render_template('results.html', images=images, search_term=search_term)
    else:
        return render_template('results.html', images=[], search_term=search_term, not_found=True)

if __name__ == '__main__':
    app.run(debug=True)

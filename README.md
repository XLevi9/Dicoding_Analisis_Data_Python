# E-Commerce Customer Analysis Dashboard 📊

## 📌 Deskripsi Proyek

Proyek ini menyajikan analisis visual dari dataset e-commerce dengan fokus pada:
- Pemetaan panas transaksi per kota
- Segmentasi pelanggan berdasarkan pola belanja
- Kontribusi transaksi per kota

## 📋 Struktur Dashboard

Dashboard memiliki 3 visualisasi utama:
1. **Geospatial Transaction Heatmap**: Peta interaktif yang menunjukkan konsentrasi transaksi di berbagai kota di Brazil
2. **Customer Spending Segmentation**: Segmentasi pelanggan berdasarkan total pengeluaran
3. **Transaction Contribution by City**: Tabel yang menampilkan kontribusi persentase masing-masing kota

## 🔧 Setup Environment

### Menggunakan Anaconda
```
conda create --name main-ds python=3.9
conda activate main-ds
pip install -r requirements.txt
```

### Menggunakan Shell/Terminal (Pipenv)
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## 📦 Dependensi

Berikut adalah package yang digunakan dalam proyek ini:
```
pandas==2.2.3
matplotlib==3.9.4
seaborn==0.13.2
folium==0.19.5
streamlit==1.45.0
streamlit-folium==0.15.1
```

## 🚀 Cara Menjalankan Dashboard

Untuk menjalankan dashboard di lingkungan lokal(Harus berada di folder root):
```
streamlit run Dashboard/dashboard.py
```

## 👨‍💻 Author

- XLevi9
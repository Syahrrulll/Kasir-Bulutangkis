# Kasir Bulutangkis (Python Flask)

Versi Python dari aplikasi kasir bulutangkis dengan fitur 100% lengkap:
- Keranjang belanja dinamis (tambah, update jumlah, hapus item)
- Perhitungan diskon fleksibel (0% - 25%)
- Perhitungan PPN 11%
- Perhitungan pembayaran, sisa kekurangan, dan kembalian
- Cetak struk belanja rapi & siap print

## Struktur File
```
Python/
├── app.py                # Backend Flask (Routing, Session, Logika Bisnis)
├── requirements.txt      # Dependensi (Flask)
├── run.bat               # Shortcut double-click untuk Windows
├── static/
│   ├── style.css         # Styling modern kasir
│   └── img/              # Foto-foto produk
└── templates/
    ├── index.html        # Halaman utama kasir
    └── struk.html        # Halaman cetak struk
```

## Cara Menjalankan

### Cara 1 (Paling Mudah di Windows):
Cukup **double-click** file `run.bat`.

### Cara 2 (Lewat Terminal / PowerShell):
1. Buka terminal di folder `Python`:
   ```powershell
   cd "e:\Program\PHP\Kasir Bulutangkis\Python"
   ```
2. Jalankan:
   ```powershell
   python app.py
   ```
3. Buka browser di:
   👉 **http://127.0.0.1:5000**

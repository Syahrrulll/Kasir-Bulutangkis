from flask import Flask, render_template, request, session, redirect, url_for
from datetime import datetime
import random

app = Flask(__name__)
app.secret_key = 'kasir_bulutangkis_super_secret_key_2026'

# ====================== DATA PRODUK ======================
PRODUK = [
    {'kode': 'L1', 'nama': 'Sewa Lapangan',      'harga': 50000,  'satuan': 'jam',   'img': 'img/lapangan.jpg'},
    {'kode': 'L2', 'nama': 'Sewa Lapangan VIP',  'harga': 100000, 'satuan': 'jam',   'img': 'img/lapangan.jpg'},
    {'kode': 'S1', 'nama': 'Shuttlecock',         'harga': 35000,  'satuan': 'tube',  'img': 'img/shuttlecock.jpg'},
    {'kode': 'S2', 'nama': 'Shuttlecock Premium', 'harga': 55000,  'satuan': 'tube',  'img': 'img/shuttlecock.jpg'},
    {'kode': 'R1', 'nama': 'Sewa Raket',          'harga': 15000,  'satuan': 'sesi',  'img': 'img/raket.jpg'},
    {'kode': 'M1', 'nama': 'Air Mineral',          'harga': 5000,   'satuan': 'botol', 'img': 'img/air_mineral.jpg'},
    {'kode': 'M2', 'nama': 'Minuman Isotonik',    'harga': 8000,   'satuan': 'botol', 'img': 'img/isotonik.jpg'},
    {'kode': 'K1', 'nama': 'Nasi Goreng',          'harga': 20000,  'satuan': 'porsi', 'img': 'img/nasi_goreng.jpg'},
]
PRODUK_MAP = {p['kode']: p for p in PRODUK}

# ====================== HELPER FORMAT RUPIAH ======================
def rp(n):
    try:
        val = int(round(float(n)))
        return f"Rp {val:,}".replace(",", ".")
    except (ValueError, TypeError):
        return "Rp 0"

app.jinja_env.filters['rp'] = rp
app.jinja_env.globals['rp'] = rp

def generate_trx():
    return f"TRX-{datetime.now().strftime('%Y%m%d')}-{random.randint(100, 999)}"

# ====================== ROUTES ======================
@app.route('/', methods=['GET', 'POST'])
def index():
    if 'keranjang' not in session:
        session['keranjang'] = {}
    if 'diskon_pct' not in session:
        session['diskon_pct'] = 0
    if 'bayar' not in session:
        session['bayar'] = 0
    if 'no_trx' not in session:
        session['no_trx'] = generate_trx()

    # Handle POST Actions
    if request.method == 'POST':
        action = request.form.get('action', '')

        if action == 'tambah':
            kode = request.form.get('kode', '')
            try:
                qty = max(1, int(request.form.get('qty', 1)))
            except ValueError:
                qty = 1

            if kode in PRODUK_MAP:
                keranjang = session['keranjang']
                if kode in keranjang:
                    keranjang[kode]['qty'] += qty
                else:
                    keranjang[kode] = {
                        'nama': PRODUK_MAP[kode]['nama'],
                        'harga': PRODUK_MAP[kode]['harga'],
                        'satuan': PRODUK_MAP[kode]['satuan'],
                        'qty': qty
                    }
                session['keranjang'] = keranjang
                session.modified = True
                session['notif'] = f"ok:{PRODUK_MAP[kode]['nama']} ditambahkan."

        elif action == 'hapus':
            kode = request.form.get('kode', '')
            keranjang = session['keranjang']
            if kode in keranjang:
                del keranjang[kode]
                session['keranjang'] = keranjang
                session.modified = True
                session['notif'] = "ok:"

        elif action == 'update_qty':
            kode = request.form.get('kode', '')
            try:
                qty = int(request.form.get('qty', 1))
            except ValueError:
                qty = 1

            keranjang = session['keranjang']
            if qty <= 0:
                if kode in keranjang:
                    del keranjang[kode]
            elif kode in keranjang:
                keranjang[kode]['qty'] = min(99, qty)

            session['keranjang'] = keranjang
            session.modified = True
            session['notif'] = "ok:Jumlah diperbarui."

        elif action == 'set_diskon':
            try:
                diskon = int(request.form.get('diskon', 0))
            except ValueError:
                diskon = 0
            session['diskon_pct'] = max(0, min(100, diskon))
            session.modified = True
            session['notif'] = f"ok:Diskon {session['diskon_pct']}% diterapkan."

        elif action == 'bayar':
            try:
                bayar = max(0, int(request.form.get('bayar', 0)))
            except ValueError:
                bayar = 0
            session['bayar'] = bayar
            session.modified = True

        elif action == 'reset':
            session['keranjang'] = {}
            session['diskon_pct'] = 0
            session['bayar'] = 0
            session['no_trx'] = generate_trx()
            session.modified = True
            session['notif'] = "ok:Transaksi direset."

        return redirect(url_for('index'))

    # Kalkulasi
    keranjang = session.get('keranjang', {})
    diskon_pct = session.get('diskon_pct', 0)
    bayar = session.get('bayar', 0)

    subtotal = sum(item['harga'] * item['qty'] for item in keranjang.values())
    diskon_nominal = int(round(subtotal * diskon_pct / 100))
    setelah_diskon = subtotal - diskon_nominal
    pajak = int(round(setelah_diskon * 0.11))  # PPN 11%
    total = setelah_diskon + pajak
    kembalian = bayar - total
    tampil_bayar = (bayar > 0)

    # Notif flash
    notif_raw = session.pop('notif', '')
    notif_type = ''
    notif = ''
    if notif_raw and ':' in notif_raw:
        notif_type, notif = notif_raw.split(':', 1)

    tanggal = datetime.now().strftime('%d/%m/%Y %H:%M')
    no_trx = session.get('no_trx', generate_trx())

    return render_template(
        'index.html',
        produk=PRODUK,
        keranjang=keranjang,
        diskon_pct=diskon_pct,
        diskon_nominal=diskon_nominal,
        subtotal=subtotal,
        pajak=pajak,
        total=total,
        bayar=bayar,
        kembalian=kembalian,
        tampil_bayar=tampil_bayar,
        notif=notif,
        notif_type=notif_type,
        tanggal=tanggal,
        no_trx=no_trx
    )

@app.route('/struk')
def struk():
    keranjang = session.get('keranjang', {})
    diskon_pct = session.get('diskon_pct', 0)

    bayar_param = request.args.get('bayar')
    if bayar_param is not None:
        try:
            bayar_sesi = int(bayar_param)
        except ValueError:
            bayar_sesi = int(session.get('bayar', 0))
    else:
        bayar_sesi = int(session.get('bayar', 0))

    subtotal = sum(item['harga'] * item['qty'] for item in keranjang.values())
    diskon_nominal = int(round(subtotal * diskon_pct / 100))
    setelah_diskon = subtotal - diskon_nominal
    pajak = int(round(setelah_diskon * 0.11))
    total = setelah_diskon + pajak
    kembalian = bayar_sesi - total

    tanggal = datetime.now().strftime('%d/%m/%Y %H:%M')
    no_trx = session.get('no_trx', generate_trx())

    return render_template(
        'struk.html',
        keranjang=keranjang,
        diskon_pct=diskon_pct,
        diskon_nominal=diskon_nominal,
        subtotal=subtotal,
        pajak=pajak,
        total=total,
        bayar_sesi=bayar_sesi,
        kembalian=kembalian,
        tanggal=tanggal,
        no_trx=no_trx
    )

if __name__ == '__main__':
    print("=" * 55)
    print("  🏸 KASIR BULUTANGKIS (PYTHON FLASK) 🏸")
    print("  Server berjalan di: http://127.0.0.1:5000")
    print("  Tekan CTRL + C untuk menghentikan server.")
    print("=" * 55)
    app.run(host='127.0.0.1', port=5000, debug=True)

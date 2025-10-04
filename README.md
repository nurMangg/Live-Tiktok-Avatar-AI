# TikTok Live Streaming dengan AI Avatar

Website profesional untuk live streaming TikTok menggunakan AI Avatar dengan fitur kustomisasi lengkap.

**🛍️ KHUSUS UNTUK LIVE SHOPPING & JUALAN PRODUK!**

Aplikasi ini dirancang khusus untuk membantu Anda **jualan produk di TikTok Shop** dengan lebih efisien menggunakan AI Avatar.

## 🌟 Fitur Utama

### 1. 🛒 Product Management (LIVE SHOPPING)
- **Katalog produk lengkap** dengan gambar, harga, stok
- **Flash Sale** dengan countdown timer
- **Product overlay** tampil di video saat pitch
- **Diskon & promo** otomatis terhitung
- **Stock tracking** real-time
- **Script templates** khusus jualan produk

### 2. 🤖 AI Avatar
- Pilihan berbagai avatar (Default, Female, Male, Custom)
- Upload avatar custom (gambar atau video)
- Animasi gesture dan lip-sync otomatis
- Kontrol intensitas gesture
- **Auto product pitch** setiap 5 menit

### 3. 🎤 Voice & Speech
- Multiple voice types (Female/Male voices)
- Kontrol kecepatan bicara (0.5x - 2x)
- Kontrol pitch (-10 hingga +10)
- Text-to-speech integration
- **Product pitch templates** siap pakai

### 4. 📡 Live Streaming
- Integrasi langsung dengan TikTok
- Kualitas stream HD (480p - 1080p)
- Kontrol bitrate dan FPS
- Background blur/custom
- Screen sharing support

### 5. 💬 Chat & Interaksi
- Live chat real-time
- Auto greeting untuk viewer baru
- Auto thank you untuk gifts
- **Auto order confirmation**
- Chat moderation otomatis
- Script queue system

### 6. 📈 Analytics
- Viewer count real-time
- Like counter
- Comment counter
- Stream duration tracker
- Gift notifications
- **Sales metrics**

## 🚀 Instalasi

### Prerequisites
- Node.js v16 atau lebih baru
- Python 3.8 atau lebih baru
- npm atau yarn

### 1. Install Dependencies Node.js

```bash
npm install
```

### 2. Install Dependencies Python

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi

Buat file `.env` di root folder:

```env
# TikTok API Configuration
TIKTOK_CLIENT_KEY=your_tiktok_client_key_here
TIKTOK_CLIENT_SECRET=your_tiktok_client_secret_here
TIKTOK_REDIRECT_URI=http://localhost:3000/auth/callback

# Server Configuration
PORT=3000
PYTHON_PORT=5000

# AI Avatar Configuration
AVATAR_API_KEY=your_avatar_api_key_here
AVATAR_MODEL=default

# Stream Configuration
STREAM_KEY=your_stream_key_here
RTMP_URL=rtmp://your-rtmp-server/live
```

## 🎮 Cara Menggunakan

### 1. Start Backend Servers

Terminal 1 - Node.js Server:
```bash
npm start
```

Terminal 2 - Python AI Server:
```bash
python avatar_server.py
```

### 2. Buka Browser

Akses aplikasi di: `http://localhost:3000`

### 3. Hubungkan TikTok

1. Klik tombol "Hubungkan TikTok"
2. Login dengan akun TikTok
3. Berikan izin akses

### 4. Setup Avatar

1. Pilih avatar dari galeri
2. Atau upload avatar custom
3. Sesuaikan voice type dan pengaturan

### 5. Mulai Streaming

1. Atur kualitas stream
2. Tambahkan script ke queue (optional)
3. Klik "Mulai Streaming"
4. Interaksi dengan viewers!

## 📁 Struktur Folder

```
Live Tikotok AI/
├── index.html          # Main HTML interface
├── styles.css          # Styling dan UI
├── app.js             # Frontend JavaScript
├── server.js          # Node.js backend
├── avatar_server.py   # Python AI backend
├── package.json       # Node dependencies
├── requirements.txt   # Python dependencies
├── avatars/          # Avatar storage
├── temp/             # Temporary files
└── README.md         # Dokumentasi
```

## 🎨 Fitur Custom

### Upload Custom Avatar

1. Klik avatar "Upload" di galeri
2. Pilih file gambar atau video
3. Avatar akan diproses otomatis

### Membuat Script Queue

1. Tulis script di textarea
2. Klik "Tambah ke Queue"
3. Script akan diucapkan secara berurutan

### Auto Response

Aktifkan fitur auto response untuk:
- Menyapa viewer baru otomatis
- Ucapkan terima kasih untuk gifts
- Moderasi chat otomatis

## 🔧 API Integration

### TikTok API

Untuk mendapatkan TikTok API credentials:
1. Daftar di [TikTok for Developers](https://developers.tiktok.com/)
2. Buat aplikasi baru
3. Dapatkan Client Key dan Client Secret
4. Set redirect URI

### Text-to-Speech Options

Aplikasi mendukung integrasi dengan:
- Google Cloud Text-to-Speech
- Amazon Polly
- Microsoft Azure Speech
- ElevenLabs

Edit `avatar_server.py` untuk mengintegrasikan TTS provider pilihan.

## 🎯 Pengaturan Stream

### Kualitas yang Direkomendasikan

| Kualitas | Bitrate | FPS | Use Case |
|----------|---------|-----|----------|
| 1080p | 4000 kbps | 30-60 | High-end streaming |
| 720p | 2500 kbps | 30 | Balanced (Recommended) |
| 480p | 1500 kbps | 24 | Low bandwidth |

## 🐛 Troubleshooting

### Stream tidak mulai
- Pastikan kedua server berjalan
- Cek koneksi TikTok
- Periksa console browser untuk error

### Avatar tidak muncul
- Pastikan Python server running
- Cek file avatar di folder `avatars/`
- Restart Python server

### Chat tidak masuk
- Verifikasi koneksi Socket.IO
- Cek TikTok API credentials
- Periksa network tab di DevTools

## 🔒 Security Notes

- Jangan commit file `.env` ke git
- Gunakan HTTPS untuk production
- Simpan API keys dengan aman
- Validasi semua input user


## 🛍️ Panduan Khusus Live Shopping

Untuk panduan lengkap jualan produk, baca:
- **[LIVE_SHOPPING_GUIDE.md](LIVE_SHOPPING_GUIDE.md)** - Panduan lengkap live shopping
- **[products_example.json](products_example.json)** - Contoh data produk

### Quick Start Live Shopping:

1. **Tambah Produk**: Klik "Tambah Produk" di panel kiri
2. **Upload gambar** dan isi detail produk
3. **Set harga promo** dan stok
4. **Enable Flash Sale** (optional)
5. **Pilih script template** untuk pitch produk
6. **Mulai streaming** dan klik produk untuk tampilkan
7. **Monitor penjualan** di panel kanan

## 📄 License

MIT License - Feel free to use for personal and commercial projects
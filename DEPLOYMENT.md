# Panduan Deployment ke VPS Ubuntu

Dokumen ini menjelaskan cara men-deploy bot Telegram ini ke VPS dengan sistem operasi Ubuntu.

Ada dua metode yang direkomendasikan:
1. **Docker (Disarankan)**: Lebih mudah, tidak mengotori sistem, sudah termasuk database.
2. **Manual (Systemd)**: Lebih ringan resource jika VPS sangat kecil (RAM < 1GB).

---

## Prasyarat

1. **VPS Ubuntu** (20.04 atau 22.04 LTS).
2. **Domain/IP Address** VPS.
3. **Akses SSH** `root` atau user dengan hak `sudo`.
4. **Environment Variables**: Pastikan Anda memiliki nilai untuk `BOT_TOKEN` dan `ADMIN_IDS`.

---

## Persiapan Server

1. Masuk ke VPS:
   ```bash
   ssh root@<IP_ADDRESS_VPS>
   ```

2. Update sistem:
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. Install Git:
   ```bash
   sudo apt install git -y
   ```

---

## Opsi 1: Deployment dengan Docker (Disarankan)

Metode ini akan menjalankan bot dan database PostgreSQL dalam container terisolasi.

### 1. Install Docker & Docker Compose
```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Verifikasi instalasi
sudo docker --version
sudo docker compose version
```

### 2. Clone Repository
```bash
git clone https://github.com/viteprodev/botinvest.git
cd botinvest
```


### 3. Konfigurasi Environment (.env)
Buat file `.env` dari contoh atau buat baru:
```bash
nano .env
```
Isi dengan data Anda:

**Opsi A: Menggunakan Supabase (External Database)**
Jika Anda menggunakan Supabase, ambil *Connection String (URI)* dari dashboard Supabase (Settings -> Database -> Connection String -> URI).
Mode: `Transaction` (port 6543) direkomendasikan untuk serverless, tapi `Session` (port 5432) juga oke untuk VPS.

```ini
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_IDS=123456789,987654321
# Ganti PASSWORD dengan password database Supabase Anda
DATABASE_URL=postgresql://postgres.xxxx:PASSWORD@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres
```

**Opsi B: Menggunakan Local DB (Docker)**
Jika ingin database lokal (harus uncomment bagian `db` di `docker-compose.yml`):
```ini
DATABASE_URL=postgresql://botuser:botpassword@db:5432/botdb
```
*Catatan: Password database di atas sesuai dengan default di `docker-compose.yml`. Ubah jika perlu.*

### 4. Jalankan Bot
```bash
sudo docker compose up -d --build
```
Bot akan berjalan di background.

### Perintah Berguna Docker:
- **Lihat log**: `sudo docker compose logs -f`
- **Stop bot**: `sudo docker compose down`
- **Restart bot**: `sudo docker compose restart`
- **Update kode**:
  ```bash
  git pull
  sudo docker compose up -d --build
  ```

---

## Opsi 2: Deployment Manual (Systemd)

Gunakan metode ini jika Anda tidak ingin menggunakan Docker.

### 1. Install Python & PostgreSQL
```bash
sudo apt install python3-pip python3-venv postgresql postgresql-contrib libpq-dev -y
```

### 2. Setup Database
```bash
# Masuk user postgres
sudo -u postgres psql

# Di dalam shell psql:
CREATE DATABASE botinvest;
CREATE USER botuser WITH PASSWORD 'password_rahasia_anda';
GRANT ALL PRIVILEGES ON DATABASE botinvest TO botuser;
\q
```

### 3. Clone & Setup Project
```bash
# Clone di home folder
cd ~
git clone https://github.com/viteprodev/botinvest.git
cd botinvest

# Buat Virtual Environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Konfigurasi Environment (.env)
```bash
nano .env
```
Isi:
```ini
BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_IDS=123456789
DATABASE_URL=postgresql://botuser:password_rahasia_anda@localhost:5432/botinvest
```

### 5. Buat Service Systemd
Agar bot tetap jalan setelah SSH ditutup dan auto-start saat reboot.

```bash
sudo nano /etc/systemd/system/botinvest.service
```
Isi (sesuaikan path `/root` atau `/home/username`):
```ini
[Unit]
Description=Telegram Bot Invest
After=network.target postgresql.service

[Service]
User=root
WorkingDirectory=/root/botinvest
# Path ke uvicorn di dalam venv
ExecStart=/root/botinvest/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
EnvironmentFile=/root/botinvest/.env

[Install]
WantedBy=multi-user.target
```

### 6. Jalankan Service
```bash
sudo systemctl daemon-reload
sudo systemctl start botinvest
sudo systemctl enable botinvest
sudo systemctl status botinvest
```

---

## Cek Status
Setelah deploy, coba chat bot Anda di Telegram dan ketik `/start`.
Jika menggunakan Webhook (opsional, perlu domain SSL), pastikan port 8000 bisa diakses dari luar atau setup Nginx sebagai Reverse Proxy. 
Namun, config saat ini menggunakan **Polling** (default `python-telegram-bot` jika tidak di set webhook secara eksplisit di kode), jadi tidak perlu membuka port input dari luar, cukup outbound internet.

*Catatan: Kode `main.py` Anda menjalankan server FastAPI + updater polling. Jadi ini aman dibelakang firewall tanpa port forwarding untuk telegram updates.*

import os
import subprocess
import time
import sys
from pathlib import Path


# Sabit dosya konumları ve Drive linkleri (Bu konumları daha sonra değiştirebilirsiniz)
MEDIA_DIR = "/Tokyo2"  # Termux, Linux veya Windows'ta geçerli konumu kullanabilirsiniz
VIDEO_FILE = os.path.join(MEDIA_DIR, "Loop.mp4")
AUDIO_FILE = os.path.join(MEDIA_DIR, "Music.aac")
DRIVE_VIDEO_URL = "https://drive.google.com/file/d/1xzIcYgyuJqna28gl-jwTUmJJvRydY9wI/view?usp=drive_link"
DRIVE_AUDIO_URL = "https://drive.google.com/file/d/1YGinMwVJK90QxCZM-F9NkiwXsyThUoAx/view?usp=drive_link"

# Komut çalıştırıcı
def run_command(command):
    process = subprocess.run(command, shell=True, text=True)
    if process.returncode != 0:
        print(f"Komut başarısız: {command}")
        return False
    return True

# Google Drive'dan dosya indir (Gerekli --fuzzy parametresi eklenmiş)
def download_file(drive_url, destination):
    print(f"{destination} indiriliyor...")
    command = f"gdown --fuzzy {drive_url} -O \"{destination}\""
    run_command(command)

# Eksik dosyaları kontrol et ve indir
def download_missing_files():
    # Dosya yolunu kontrol et, eğer yoksa oluştur
    if not os.path.exists(MEDIA_DIR):
        print(f"{MEDIA_DIR} bulunamadı, oluşturuluyor...")
        os.makedirs(MEDIA_DIR)

    # Video dosyasının mevcut olup olmadığını kontrol et
    if not Path(VIDEO_FILE).is_file():
        print(f"{VIDEO_FILE} bulunamadı, indiriliyor...")
        download_file(DRIVE_VIDEO_URL, VIDEO_FILE)
    
    # Ses dosyasının mevcut olup olmadığını kontrol et
    if not Path(AUDIO_FILE).is_file():
        print(f"{AUDIO_FILE} bulunamadı, indiriliyor...")
        download_file(DRIVE_AUDIO_URL, AUDIO_FILE)

# Ana yayın fonksiyonu
def start_stream(rtmp_url):
    # Yayın döngüsü
    while True:
        # İlgili RTMP URL için FFmpeg komutunu oluştur
        print(f"Yayın başlıyor: {rtmp_url}")
        command = (
            f"ffmpeg -stream_loop -1 -re -i \"{VIDEO_FILE}\" -stream_loop -1 -re -i \"{AUDIO_FILE}\" "
            f"-c:v copy -c:a aac -f flv {rtmp_url}"
        )

        success = run_command(command)
        
        # Eğer işlem başarısızsa yeniden başlatmak için bir gecikme ekleyelim
        if not success:
            print("Yayın hata verdi, yeniden başlatılıyor...")
            time.sleep(5)  # Bekleme süresi
        else:
            print("Yayın tamamlandı.")
            break  # Başarılı yayın yapıldıysa döngü sonlandırılır

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Kullanım: python stream_reliable.py <RTMP_URL>")
        sys.exit(1)

    rtmp_url = sys.argv[1]

    # Bağımlılık kontrolü
    try:
        subprocess.run(["gdown", "--help"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    except subprocess.CalledProcessError:
        print("gdown bağımlılığı eksik. Lütfen yükleyin: pip install gdown")
        sys.exit(1)

    # Eksik dosyaları indir
    download_missing_files()

    # Yayını başlat
    start_stream(rtmp_url)

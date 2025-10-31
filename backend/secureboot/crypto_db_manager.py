# secureboot/crypto_db_manager.py
import os
import sys
import sqlite3
from .crypto_win import CryptoSession

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC_PATH = os.path.join(BASE_DIR, "db.sqlite3.enc")
DB_PATH  = os.path.join(BASE_DIR, "db.sqlite3")

def decrypt_db(passphrase: str):
    """
    1. CryptoSession(passphrase) → MD4 -> DeriveKey -> 3DES -> ECB
    2. Читаем db.sqlite3.enc целиком.
    3. CryptDecrypt(...) -> plaintext -> db.sqlite3.
    4. Проверяем наличие администратора (is_superuser=1).
    5. Если админа нет → немедленный sys.exit(1). Это пункт 4+5. :contentReference[oaicite:15]{index=15}
    """

    if not os.path.exists(ENC_PATH):
        print("Файл db.sqlite3.enc не найден. Нечего расшифровывать.")
        sys.exit(1)

    sess = CryptoSession(passphrase)

    with open(ENC_PATH, "rb") as f:
        ciphertext = f.read()

    plaintext = sess.decrypt_buffer(ciphertext, final=True)

    with open(DB_PATH, "wb") as out:
        out.write(plaintext)

    # Проверяем администратора
    if not has_admin(DB_PATH):
        secure_delete(DB_PATH)
        sess.close()
        print("Неверная парольная фраза или нет администратора -> отказ запуска")
        sys.exit(1)

    sess.close()


def encrypt_db(passphrase: str):
    """
    1. Читаем db.sqlite3.
    2. Шифруем через CryptoSession(passphrase).
    3. Пишем результат в db.sqlite3.enc.
    4. Стираем и удаляем db.sqlite3.
    Это пункт 3 и пункт 6 методички. :contentReference[oaicite:16]{index=16}
    """
    if not os.path.exists(DB_PATH):
        print("Нет открытой базы db.sqlite3, пропускаю.")
        return

    sess = CryptoSession(passphrase)

    with open(DB_PATH, "rb") as f:
        plaintext = f.read()

    ciphertext = sess.encrypt_buffer(plaintext, final=True)

    with open(ENC_PATH, "wb") as out:
        out.write(ciphertext)

    sess.close()

    secure_delete(DB_PATH)


def secure_delete(path: str):
    if not os.path.exists(path):
        return
    size = os.path.getsize(path)
    with open(path, "r+b") as f:
        f.write(b"\x00" * size)
        f.flush()
        os.fsync(f.fileno())
    os.remove(path)


def has_admin(db_path: str) -> bool:
    """
    Проверка условия из п.4:
    'Правильность парольной фразы определяется по наличию ... администратора' :contentReference[oaicite:17]{index=17}
    Для стандартной Django таблицы auth_user проверяем is_superuser=1.
    Если у тебя кастомная модель пользователя — поменяй запрос.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    try:
        cur.execute("SELECT COUNT(*) FROM auth_user WHERE is_superuser=1")
        row = cur.fetchone()
        count_admin = row[0] if row else 0
    except Exception:
        count_admin = 0
    conn.close()
    return count_admin > 0

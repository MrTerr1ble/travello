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
    Возвращает True, если найден хотя бы один пользователь с правами администратора.
    Мы пробуем сначала кастомную таблицу users_user (для кастомной модели),
    а если её нет, fallback на стандартную auth_user.
    """

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    count_admin = 0

    # 1. Попытка: кастомная модель пользователя
    try:
        cur.execute("SELECT COUNT(*) FROM users_user WHERE is_superuser=1")
        row = cur.fetchone()
        if row and row[0] > 0:
            count_admin = row[0]
    except Exception:
        pass

    # 2. Если пока не нашли, пробуем стандартную таблицу auth_user
    if count_admin == 0:
        try:
            cur.execute("SELECT COUNT(*) FROM auth_user WHERE is_superuser=1")
            row = cur.fetchone()
            if row and row[0] > 0:
                count_admin = row[0]
        except Exception:
            pass

    conn.close()
    return count_admin > 0

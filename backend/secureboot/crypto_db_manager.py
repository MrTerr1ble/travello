# secureboot/crypto_db_manager.py
import os
import sys
import sqlite3
from .crypto_win import CryptoSession

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENC_PATH = os.path.join(BASE_DIR, "db.sqlite3.enc")
DB_PATH  = os.path.join(BASE_DIR, "db.sqlite3")

CHUNK_SIZE = 4096

def decrypt_db(passphrase: str):
    """
    1. Открываем сеанс CryptoAPI с парольной фразой.
    2. Читаем db.sqlite3.enc поблочно, прогоняем через CryptDecrypt.
    3. Собираем в db.sqlite3 (временный открытый файл).
    4. Проверяем, что в базе есть админ.
    """

    if not os.path.exists(ENC_PATH):
        print("Нет зашифрованной базы (db.sqlite3.enc). Возможно первый запуск?")
        # Если это первый запуск, можно решить иначе:
        # - возможно db.sqlite3 уже существует в открытом виде и мы потом зашифруем при остановке.
        # Но для лабы лучше требовать ENC_PATH.
        sys.exit(1)

    sess = CryptoSession(passphrase)

    with open(ENC_PATH, "rb") as enc_f, open(DB_PATH, "wb") as db_f:
        while True:
            chunk = enc_f.read(CHUNK_SIZE)
            if not chunk:
                break
            # финальный блок мы узнаем только постфактум,
            # поэтому для простоты читаем всё целиком и расшифровываем разом:
            # Для больших файлов лучше буферизовать. Для защиты в лабе можно читать целиком.
            # Упростим: перечитаем файл полностью сразу.
        # --- упрощённый путь для лабораторки:
    with open(ENC_PATH, "rb") as enc_f:
        data_enc = enc_f.read()
    # один вызов decrypt_buffer(final=True) для простоты
    plaintext = sess.decrypt_buffer(data_enc, final=True)
    with open(DB_PATH, "wb") as db_f:
        db_f.write(plaintext)

    # проверка администратора
    if not has_admin(DB_PATH):
        # убиваем незашифрованную базу, чтобы не осталась в открытом виде
        try:
            secure_delete(DB_PATH)
        except:
            pass
        sess.close()
        print("Нет администратора или неверная парольная фраза -> отказ запуска")
        sys.exit(1)

    sess.close()


def encrypt_db(passphrase: str):
    """
    1. Читаем db.sqlite3
    2. Шифруем через CryptoAPI
    3. Записываем db.sqlite3.enc
    4. Затираем и удаляем db.sqlite3
    """
    if not os.path.exists(DB_PATH):
        print("Открытой базы нет, нечего шифровать.")
        return

    sess = CryptoSession(passphrase)

    with open(DB_PATH, "rb") as db_f:
        plaintext = db_f.read()

    ciphertext = sess.encrypt_buffer(plaintext, final=True)

    with open(ENC_PATH, "wb") as enc_f:
        enc_f.write(ciphertext)

    sess.close()

    secure_delete(DB_PATH)


def secure_delete(path: str):
    """
    Перезаписать файл нулями и удалить.
    Это реализует пункт:
    «старое содержимое файла учетных записей ... стирается»
    и «временный файл ... должен быть удален». :contentReference[oaicite:4]{index=4}
    """
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
    Открываем sqlite и убеждаемся, что есть админ.
    Это прямая реализация требования:
    «Правильность введенной парольной фразы определяется по наличию ... администратора» (п.4). :contentReference[oaicite:5]{index=5}
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    # адаптируй ниже под твою таблицу пользователей.
    # В стандартной Django: auth_user (is_superuser=1)
    try:
        cur.execute("SELECT COUNT(*) FROM auth_user WHERE is_superuser=1")
        row = cur.fetchone()
        count_admin = row[0] if row else 0
        conn.close()
        return count_admin > 0
    except Exception:
        conn.close()
        return False

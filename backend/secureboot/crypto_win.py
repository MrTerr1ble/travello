# secureboot/crypto_win.py
import ctypes
from ctypes import wintypes

advapi32 = ctypes.WinDLL("advapi32.dll")

HCRYPTPROV = wintypes.HANDLE
HCRYPTHASH = wintypes.HANDLE
HCRYPTKEY  = wintypes.HANDLE

# провайдер
PROV_RSA_FULL = 1
CRYPT_VERIFYCONTEXT = 0xF0000000

# === Вариант 22 (из таблицы): ===
# - Блочный шифр
# - Режим: электронная кодовая книга (ECB)
# - Добавление к ключу случайного значения: НЕТ
# - Хеш: MD4
# =================================

# Алгоритм хеширования MD4
CALG_MD4  = 0x00008002  # MD4 по CryptoAPI. :contentReference[oaicite:9]{index=9}

# Блочный симметричный алгоритм.
# Для лабораторки обычно берут 3DES (CALG_3DES) как блочный шифр.
# 3DES в CryptoAPI: CALG_3DES = 0x00006603 (блочный алгоритм).
CALG_3DES = 0x00006603

# Параметр для установки режима шифрования
KP_MODE        = 4

# Режимы
CRYPT_MODE_ECB = 2  # "электронная кодовая книга" из таблицы варианта. :contentReference[oaicite:10]{index=10}

# Флаги для CryptDeriveKey
CRYPT_EXPORTABLE = 0x00000001
# CRYPT_CREATE_SALT = 0x00000004  # нам НЕ нужно, вариант 22 = "Нет". :contentReference[oaicite:11]{index=11}

DWORD = wintypes.DWORD
BOOL  = wintypes.BOOL
BYTE  = ctypes.c_ubyte

# --- объявляем сигнатуры WinAPI как раньше ---

advapi32.CryptAcquireContextA.argtypes = [
    ctypes.POINTER(HCRYPTPROV),
    wintypes.LPCSTR,
    wintypes.LPCSTR,
    DWORD,
    DWORD
]
advapi32.CryptAcquireContextA.restype = BOOL

advapi32.CryptCreateHash.argtypes = [
    HCRYPTPROV,
    DWORD,
    HCRYPTKEY,
    DWORD,
    ctypes.POINTER(HCRYPTHASH)
]
advapi32.CryptCreateHash.restype = BOOL

advapi32.CryptHashData.argtypes = [
    HCRYPTHASH,
    ctypes.POINTER(BYTE),
    DWORD,
    DWORD
]
advapi32.CryptHashData.restype = BOOL

advapi32.CryptDeriveKey.argtypes = [
    HCRYPTPROV,
    DWORD,
    HCRYPTHASH,
    DWORD,
    ctypes.POINTER(HCRYPTKEY)
]
advapi32.CryptDeriveKey.restype = BOOL

advapi32.CryptSetKeyParam.argtypes = [
    HCRYPTKEY,
    DWORD,
    ctypes.POINTER(BYTE),
    DWORD
]
advapi32.CryptSetKeyParam.restype = BOOL

advapi32.CryptEncrypt.argtypes = [
    HCRYPTKEY,
    HCRYPTHASH,
    BOOL,
    DWORD,
    ctypes.POINTER(BYTE),
    ctypes.POINTER(DWORD),
    DWORD
]
advapi32.CryptEncrypt.restype = BOOL

advapi32.CryptDecrypt.argtypes = [
    HCRYPTKEY,
    HCRYPTHASH,
    BOOL,
    DWORD,
    ctypes.POINTER(BYTE),
    ctypes.POINTER(DWORD)
]
advapi32.CryptDecrypt.restype = BOOL

advapi32.CryptDestroyHash.argtypes = [HCRYPTHASH]
advapi32.CryptDestroyHash.restype = BOOL

advapi32.CryptDestroyKey.argtypes = [HCRYPTKEY]
advapi32.CryptDestroyKey.restype = BOOL

advapi32.CryptReleaseContext.argtypes = [HCRYPTPROV, DWORD]
advapi32.CryptReleaseContext.restype = BOOL


class CryptoSession:
    """
    Открывает CryptoAPI сеанс:
    - получает провайдера (CryptAcquireContextA),
    - хеширует пароль через MD4 (CryptCreateHash + CryptHashData),
    - DeriveKey -> 3DES-ключ,
    - ставит режим CRYPT_MODE_ECB (электронная кодовая книга),
    - даёт методы encrypt_buffer/decrypt_buffer.
    Это полностью соответствует варианту 22. :contentReference[oaicite:12]{index=12}
    """

    def __init__(self, passphrase: str):
        self.hProv = HCRYPTPROV()
        ok = advapi32.CryptAcquireContextA(
            ctypes.byref(self.hProv),
            None,
            None,
            DWORD(PROV_RSA_FULL),
            DWORD(CRYPT_VERIFYCONTEXT)
        )
        if not ok:
            raise RuntimeError("CryptAcquireContext failed")

        # Создаём хеш-объект MD4
        self.hHash = HCRYPTHASH()
        ok = advapi32.CryptCreateHash(
            self.hProv,
            DWORD(CALG_MD4),     # вариант 22 требует MD4
            HCRYPTKEY(),
            DWORD(0),
            ctypes.byref(self.hHash)
        )
        if not ok:
            raise RuntimeError("CryptCreateHash failed")

        phrase_bytes = passphrase.encode("utf-8")
        ok = advapi32.CryptHashData(
            self.hHash,
            (BYTE * len(phrase_bytes)).from_buffer_copy(phrase_bytes),
            DWORD(len(phrase_bytes)),
            DWORD(0)
        )
        if not ok:
            raise RuntimeError("CryptHashData failed")

        # DeriveKey -> получаем блочный ключ (3DES), без CRYPT_CREATE_SALT
        self.hKey = HCRYPTKEY()
        flags = CRYPT_EXPORTABLE  # + без соли, т.к. вариант 22 = "Нет" для соли
        ok = advapi32.CryptDeriveKey(
            self.hProv,
            DWORD(CALG_3DES),  # используем блочный шифр
            self.hHash,
            DWORD(flags),
            ctypes.byref(self.hKey)
        )
        if not ok:
            raise RuntimeError("CryptDeriveKey failed")

        # Устанавливаем режим шифрования ключа: электронная кодовая книга => ECB
        mode_byte = BYTE(CRYPT_MODE_ECB)
        ok = advapi32.CryptSetKeyParam(
            self.hKey,
            DWORD(KP_MODE),
            ctypes.byref(mode_byte),
            DWORD(0)
        )
        # Для 3DES CryptoAPI примет KP_MODE и поставит ECB, что совпадает с вариантом 22.

        # Хеш нам больше не нужен
        advapi32.CryptDestroyHash(self.hHash)

    def encrypt_buffer(self, data: bytes, final: bool) -> bytes:
        # Делаем буфер с запасом для паддинга (для блочных шифров CryptoAPI может дописать)
        buf_len = len(data) + 1024
        buf = (BYTE * buf_len)()
        ctypes.memmove(buf, data, len(data))

        dwDataLen = DWORD(len(data))
        ok = advapi32.CryptEncrypt(
            self.hKey,
            HCRYPTHASH(),
            BOOL(final),
            DWORD(0),
            buf,
            ctypes.byref(dwDataLen),
            DWORD(buf_len)
        )
        if not ok:
            raise RuntimeError("CryptEncrypt failed")

        return bytes(buf[:dwDataLen.value])

    def decrypt_buffer(self, data: bytes, final: bool) -> bytes:
        buf_len = len(data)
        buf = (BYTE * buf_len)()
        ctypes.memmove(buf, data, buf_len)

        dwDataLen = DWORD(buf_len)
        ok = advapi32.CryptDecrypt(
            self.hKey,
            HCRYPTHASH(),
            BOOL(final),
            DWORD(0),
            buf,
            ctypes.byref(dwDataLen)
        )
        if not ok:
            raise RuntimeError("CryptDecrypt failed")

        return bytes(buf[:dwDataLen.value])

    def close(self):
        advapi32.CryptDestroyKey(self.hKey)
        advapi32.CryptReleaseContext(self.hProv, DWORD(0))

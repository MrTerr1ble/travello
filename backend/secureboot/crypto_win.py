# secureboot/crypto_win.py
import ctypes
from ctypes import wintypes

advapi32 = ctypes.WinDLL("advapi32.dll")

# Типы / константы CryptoAPI -----------------

HCRYPTPROV = wintypes.HANDLE
HCRYPTHASH = wintypes.HANDLE
HCRYPTKEY  = wintypes.HANDLE

PROV_RSA_FULL = 1  # классика для CryptAcquireContext

CRYPT_VERIFYCONTEXT = 0xF0000000

# Алгоритмы хеширования (подставь свой по варианту)
# например MD5 = 0x00008003, SHA1 = 0x00008004, MD4 = 0x00008002, MD2 = 0x00008001
CALG_MD2  = 0x00008001
CALG_MD4  = 0x00008002
CALG_MD5  = 0x00008003
CALG_SHA1 = 0x00008004

# Алгоритмы симметричного шифра (подставь свой по варианту)
# Пример: RC4 (потоковый) = 0x6801
#         3DES = 0x6603
#         AES-256 в старом CryptoAPI не классический, но допустим CALG_3DES/RC4 и т.д.
CALG_RC4  = 0x00006801
CALG_3DES = 0x00006603

# Параметр для установки режима
KP_MODE        = 4

# Режимы
CRYPT_MODE_ECB = 2
CRYPT_MODE_CBC = 1
CRYPT_MODE_CFB = 4

# Флаги для CryptDeriveKey
# CRYPT_CREATE_SALT = 0x00000004  <-- если по варианту "Добавление к ключу" = Да
CRYPT_EXPORTABLE = 0x00000001
CRYPT_CREATE_SALT = 0x00000004

# Буфер для размеров
DWORD = wintypes.DWORD
BOOL  = wintypes.BOOL
BYTE  = ctypes.c_ubyte

# Объявление сигнатур WinAPI -----------------

# BOOL CryptAcquireContextA(
#   HCRYPTPROV *phProv,
#   LPCSTR     pszContainer,
#   LPCSTR     pszProvider,
#   DWORD      dwProvType,
#   DWORD      dwFlags
# );
advapi32.CryptAcquireContextA.argtypes = [
    ctypes.POINTER(HCRYPTPROV),
    wintypes.LPCSTR,
    wintypes.LPCSTR,
    DWORD,
    DWORD
]
advapi32.CryptAcquireContextA.restype = BOOL

# BOOL CryptCreateHash(
#   HCRYPTPROV hProv,
#   ALG_ID    Algid,
#   HCRYPTKEY hKey,
#   DWORD     dwFlags,
#   HCRYPTHASH *phHash
# );
advapi32.CryptCreateHash.argtypes = [
    HCRYPTPROV,
    DWORD,
    HCRYPTKEY,
    DWORD,
    ctypes.POINTER(HCRYPTHASH)
]
advapi32.CryptCreateHash.restype = BOOL

# BOOL CryptHashData(
#   HCRYPTHASH hHash,
#   BYTE       *pbData,
#   DWORD      dwDataLen,
#   DWORD      dwFlags
# );
advapi32.CryptHashData.argtypes = [
    HCRYPTHASH,
    ctypes.POINTER(BYTE),
    DWORD,
    DWORD
]
advapi32.CryptHashData.restype = BOOL

# BOOL CryptDeriveKey(
#   HCRYPTPROV hProv,
#   ALG_ID    Algid,
#   HCRYPTHASH hBaseData,
#   DWORD     dwFlags,
#   HCRYPTKEY *phKey
# );
advapi32.CryptDeriveKey.argtypes = [
    HCRYPTPROV,
    DWORD,
    HCRYPTHASH,
    DWORD,
    ctypes.POINTER(HCRYPTKEY)
]
advapi32.CryptDeriveKey.restype = BOOL

# BOOL CryptSetKeyParam(
#   HCRYPTKEY hKey,
#   DWORD     dwParam,
#   BYTE      *pbData,
#   DWORD     dwFlags
# );
advapi32.CryptSetKeyParam.argtypes = [
    HCRYPTKEY,
    DWORD,
    ctypes.POINTER(BYTE),
    DWORD
]
advapi32.CryptSetKeyParam.restype = BOOL

# BOOL CryptEncrypt(
#   HCRYPTKEY  hKey,
#   HCRYPTHASH hHash,
#   BOOL       Final,
#   DWORD      dwFlags,
#   BYTE       *pbData,
#   DWORD      *pdwDataLen,
#   DWORD      dwBufLen
# );
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

# BOOL CryptDecrypt(
#   HCRYPTKEY  hKey,
#   HCRYPTHASH hHash,
#   BOOL       Final,
#   DWORD      dwFlags,
#   BYTE       *pbData,
#   DWORD      *pdwDataLen
# );
advapi32.CryptDecrypt.argtypes = [
    HCRYPTKEY,
    HCRYPTHASH,
    BOOL,
    DWORD,
    ctypes.POINTER(BYTE),
    ctypes.POINTER(DWORD)
]
advapi32.CryptDecrypt.restype = BOOL

# BOOL CryptDestroyHash(HCRYPTHASH hHash);
advapi32.CryptDestroyHash.argtypes = [HCRYPTHASH]
advapi32.CryptDestroyHash.restype = BOOL

# BOOL CryptDestroyKey(HCRYPTKEY hKey);
advapi32.CryptDestroyKey.argtypes = [HCRYPTKEY]
advapi32.CryptDestroyKey.restype = BOOL

# BOOL CryptReleaseContext(HCRYPTPROV hProv, DWORD dwFlags);
advapi32.CryptReleaseContext.argtypes = [HCRYPTPROV, DWORD]
advapi32.CryptReleaseContext.restype = BOOL


# Вспомогательные функции высокого уровня -----------------

class CryptoSession:
    def __init__(self, passphrase: str):
        """
        1. Acquire provider
        2. Create hash for passphrase
        3. Derive symmetric key
        4. Set cipher mode
        Всё по твоему варианту.
        """
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

        # Создаём хеш
        self.hHash = HCRYPTHASH()
        # TODO: подставь нужный алгоритм хеширования из своего варианта:
        # например CALG_MD5, CALG_MD4, CALG_MD2, CALG_SHA1
        HASH_ALG = CALG_MD5  # TODO
        ok = advapi32.CryptCreateHash(
            self.hProv,
            DWORD(HASH_ALG),
            HCRYPTKEY(),  # 0
            DWORD(0),
            ctypes.byref(self.hHash)
        )
        if not ok:
            raise RuntimeError("CryptCreateHash failed")

        # Кормим парольную фразу в хеш
        phrase_bytes = passphrase.encode("utf-8")
        ok = advapi32.CryptHashData(
            self.hHash,
            (BYTE * len(phrase_bytes)).from_buffer_copy(phrase_bytes),
            DWORD(len(phrase_bytes)),
            DWORD(0)
        )
        if not ok:
            raise RuntimeError("CryptHashData failed")

        # Получаем сеансовый ключ
        self.hKey = HCRYPTKEY()

        # TODO: подставь свой алгоритм симметричного шифра из варианта:
        # - потоковый (например RC4 -> CALG_RC4)
        # - блочный (например 3DES -> CALG_3DES)
        KEY_ALG = CALG_RC4  # TODO

        # Флаги для DeriveKey:
        # - CRYPT_CREATE_SALT если по твоему варианту "Добавление к ключу" = Да
        # - CRYPT_EXPORTABLE обычно ок, чтобы ключ можно было использовать
        flags = CRYPT_EXPORTABLE
        # TODO: если у тебя "Добавление к ключу случайного значения" = Да
        # flags |= CRYPT_CREATE_SALT

        ok = advapi32.CryptDeriveKey(
            self.hProv,
            DWORD(KEY_ALG),
            self.hHash,
            DWORD(flags),
            ctypes.byref(self.hKey)
        )
        if not ok:
            raise RuntimeError("CryptDeriveKey failed")

        # Устанавливаем режим шифрования, если блочный шифр:
        # Варианты:
        #   Electronnaya kodovaya kniga -> CRYPT_MODE_ECB
        #   Sceplenie blokov shifra    -> CRYPT_MODE_CBC
        #   Obratnaya svyaz po shifr.  -> CRYPT_MODE_CFB
        CIPHER_MODE = CRYPT_MODE_CBC  # TODO: выбрать из варианта

        mode_byte = BYTE(CIPHER_MODE)
        ok = advapi32.CryptSetKeyParam(
            self.hKey,
            DWORD(KP_MODE),
            ctypes.byref(mode_byte),
            DWORD(0)
        )
        # Важно: для потоковых шифров типа RC4 KP_MODE может быть игнорирован.
        # Если у тебя потоковый алгоритм и методичка говорит "потоковый", ты это можешь пропустить.

        # уничтожим хеш (ключ уже выведен)
        advapi32.CryptDestroyHash(self.hHash)

    def encrypt_buffer(self, chunk: bytes, final: bool) -> bytes:
        """
        Оборачивает CryptEncrypt для блока данных.
        Мы должны дать буфер с запасом.
        """
        # делаем копию chunk в изменяемый буфер
        buf_len = len(chunk) + 1024  # запас, CryptoAPI может дописать паддинг
        buf = (BYTE * buf_len)()
        ctypes.memmove(buf, chunk, len(chunk))

        dwDataLen = DWORD(len(chunk))
        ok = advapi32.CryptEncrypt(
            self.hKey,
            HCRYPTHASH(),  # 0
            BOOL(final),
            DWORD(0),
            buf,
            ctypes.byref(dwDataLen),
            DWORD(buf_len)
        )
        if not ok:
            raise RuntimeError("CryptEncrypt failed")

        return bytes(buf[:dwDataLen.value])

    def decrypt_buffer(self, chunk: bytes, final: bool) -> bytes:
        buf_len = len(chunk)
        buf = (BYTE * buf_len)()
        ctypes.memmove(buf, chunk, buf_len)

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

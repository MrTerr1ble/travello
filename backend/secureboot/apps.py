# secureboot/apps.py
from django.apps import AppConfig
import os
import sys
from .crypto_db_manager import decrypt_db


class SecureBootConfig(AppConfig):
    name = "secureboot"

    def ready(self):
        # На старте сервера мы обязаны расшифровать хранилище
        # и проверить администратора.
        passphrase = os.getenv("LAB_MASTER_PASSPHRASE")
        if not passphrase:
            print("LAB_MASTER_PASSPHRASE не задан -> отказ запуска (это пункт 5)")
            sys.exit(1)

        decrypt_db(passphrase)
        # Если пароль неверный, decrypt_db сам сделает sys.exit().
        # Если всё ок — Django продолжит грузиться.

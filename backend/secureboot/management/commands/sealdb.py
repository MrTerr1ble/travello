# secureboot/management/commands/sealdb.py
from django.core.management.base import BaseCommand
import os
from secureboot.crypto_db_manager import encrypt_db

class Command(BaseCommand):
    help = "Зашифровать текущую SQLite-базу в db.sqlite3.enc (3DES+ECB, ключ из MD4 пароля) и уничтожить открытый db.sqlite3"

    def handle(self, *args, **options):
        passphrase = os.getenv("LAB_MASTER_PASSPHRASE")
        if not passphrase:
            self.stderr.write("Нет LAB_MASTER_PASSPHRASE, не могу зашифровать.")
            return

        encrypt_db(passphrase)
        self.stdout.write(self.style.SUCCESS(
            "Готово: база зашифрована CryptoAPI (блочный шифр в режиме ECB, ключ из MD4), открытый файл удалён."
        ))

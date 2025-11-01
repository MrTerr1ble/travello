from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
import os
import sys
from secureboot.crypto_db_manager import encrypt_db, decrypt_db, ENC_PATH

class Command(BaseCommand):
    help = (
        "Запускает сервер разработки с автоматической расшифровкой БД перед стартом "
        "и автоматическим шифрованием при остановке. "
        "Это удобная обёртка для демонстрации лабораторки."
    )

    def add_arguments(self, parser):
        # Пробрасываем стандартные аргументы runserver (host, port и т.д.)
        parser.add_argument(
            "addrport",
            nargs="?",
            help="Optional port number, or ipaddr:port",
        )

    def handle(self, *args, **options):
        # 1. Проверяем, что у нас есть LAB_MASTER_PASSPHRASE
        passphrase = os.getenv("LAB_MASTER_PASSPHRASE")
        if not passphrase:
            self.stderr.write(
                "LAB_MASTER_PASSPHRASE не задан -> отказ запуска (требование п.5)."
            )
            sys.exit(1)

        # 2. Если db.sqlite3.enc существует — расшифровываем её
        #    и проверяем наличие администратора.
        #    Если не существует — это либо первичный запуск до шифрования,
        #    либо ты работаешь в режиме отладки (не зашифровано ещё).
        enc_exists = os.path.exists(ENC_PATH)
        if enc_exists:
            decrypt_db(passphrase)
            # decrypt_db сам вызовет sys.exit(1), если пароль неверный
            # или нет администратора.

        # 3. Запускаем стандартный runserver внутри try/except,
        #    чтобы перехватить Ctrl+C.
        try:
            addrport = options.get("addrport")
            if addrport:
                call_command("runserver", addrport)
            else:
                call_command("runserver")
        except KeyboardInterrupt:
            self.stdout.write("Остановка сервера по Ctrl+C ...")
        finally:
            # 4. При завершении работы:
            #    - если расшифрованная db.sqlite3 существует,
            #      шифруем её обратно в db.sqlite3.enc (encrypt_db),
            #      удаляем открытый файл.
            if os.path.exists(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "db.sqlite3")):
                try:
                    encrypt_db(passphrase)
                    self.stdout.write(
                        self.style.SUCCESS(
                            "Актуальная база зашифрована и очищена (авто-seal)."
                        )
                    )
                except Exception as e:
                    self.stderr.write(f"Не удалось автоматически зашифровать базу: {e}")

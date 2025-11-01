from django.apps import AppConfig
import os
import sys
from .crypto_db_manager import decrypt_db, ENC_PATH

class SecureBootConfig(AppConfig):
    name = "secureboot"

    def ready(self):
        argv = sys.argv
        current_cmd = argv[1] if len(argv) > 1 else None

        enc_exists = os.path.exists(ENC_PATH)

        # Команды, которым разрешено работать без немедленной расшифровки/пароля
        # до того как мы вообще впервые включили защиту.
        init_ok_commands = {
            "makemigrations",
            "migrate",
            "createsuperuser",
            "shell",
            "dbshell",
            "sealdb",             # первичное запечатывание до появления enc-файла
            "runserver_secure",   # мы сами расшифруем внутри команды
        }

        # Если зашифрованная база ещё не создана (enc_exists == False)
        # и команда - одна из разрешённых инициализационных,
        # то просто выходим (не требуем пароль).
        if not enc_exists and current_cmd in init_ok_commands:
            return

        # Если команда runserver_secure (наша обёртка),
        # то тоже не дергаем decrypt_db тут, потому что команда сама всё сделает.
        if current_cmd == "runserver_secure":
            return

        # Всё остальное:
        # - база уже зашифрована ИЛИ
        # - команда не в списке разрешённых
        # -> значит включаем строгую модель защиты, как в лабе.
        passphrase = os.getenv("LAB_MASTER_PASSPHRASE")
        if not passphrase:
            print("LAB_MASTER_PASSPHRASE не задан -> отказ запуска (требование п.5).")
            sys.exit(1)

        decrypt_db(passphrase)
        # decrypt_db сам завершит процесс, если нет админа или пароль не подошёл.

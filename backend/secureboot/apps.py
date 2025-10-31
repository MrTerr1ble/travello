from django.apps import AppConfig
import os
import sys
import inspect
from django.core.management import get_commands
from .crypto_db_manager import decrypt_db, ENC_PATH


class SecureBootConfig(AppConfig):
    name = "secureboot"

    def ready(self):
        """
        Логика:
        1. Если мы запускаем manage.py для команд типа makemigrations, migrate, createsuperuser,
           и зашифрованной базы ещё НЕТ -> даём Django спокойно работать без защиты.
           Это нужно для первичной инициализации, когда ещё нет admin и нет db.sqlite3.enc.
        2. Если мы запускаем runserver ИЛИ у нас уже есть зашифрованная база db.sqlite3.enc,
           то включаем защиту:
            - требуем LAB_MASTER_PASSPHRASE,
            - пытаемся расшифровать db.sqlite3.enc,
            - проверяем наличие админа,
            - при провале выходим.
        """

        # Попробуем понять, какую management-команду сейчас выполняют.
        # В Django при вызове manage.py команда идёт как argv[1]
        argv = sys.argv  # например: ["manage.py", "createsuperuser", ...]
        current_cmd = argv[1] if len(argv) > 1 else None

        # Команды, которые должны иметь возможность работать до включения защиты,
        # когда мы ещё инициализируем базу и создаём первого суперпользователя.
        init_ok_commands = {
            "makemigrations",
            "migrate",
            "createsuperuser",
            "shell",
            "dbshell",
        }

        enc_exists = os.path.exists(ENC_PATH)

        # Сценарий А:
        # - у нас НЕТ зашифрованной базы (db.sqlite3.enc ещё не создан)
        # - и мы запускаем init-команду (migrate, createsuperuser и т.д.)
        # Тогда просто выходим, НЕ требуя пароль и НЕ расшифровывая ничего.
        if not enc_exists and current_cmd in init_ok_commands:
            # Это "до защиты": ты сейчас как раз пытаешься создать суперюзера.
            return

        # Сценарий Б:
        # Если мы дошли сюда, значит ИЛИ:
        #   - зашифрованная база уже существует  (enc_exists == True)
        #   - ИЛИ это не init-команда (например runserver)
        #
        # => Защита должна работать на полную.

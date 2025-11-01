import re

PASSWORD_DIGIT_LETTER_DIGIT_REGEX = r"\d+[A-Za-zА-Яа-яЁё]+\d+"
PASSWORD_DIGIT_LETTER_DIGIT_PATTERN = re.compile(PASSWORD_DIGIT_LETTER_DIGIT_REGEX)
PASSWORD_DIGIT_LETTER_DIGIT_MESSAGE = (
    "Пароль должен состоять из цифр, затем букв и снова цифр."
)


def is_digit_letter_digit_password(password: str) -> bool:
    """Return True if password matches the digit-letter-digit pattern."""
    return bool(PASSWORD_DIGIT_LETTER_DIGIT_PATTERN.fullmatch(password or ""))

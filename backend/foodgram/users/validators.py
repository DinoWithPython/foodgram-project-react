import string

from rest_framework.validators import ValidationError


def validate_username(value):
    """Проверка имени и возврат не корректных символов."""
    forbidden_characters = []
    for symbol in value:
        if symbol in string.punctuation and symbol not in ".@+-_":
            forbidden_characters.append(symbol)
        if symbol in string.whitespace:
            forbidden_characters.append(symbol)
    if len(forbidden_characters) != 0:
        raise ValidationError(
            f'Введены не допустимые символы: {"".join(forbidden_characters)}'
            f"Не допускаются: пробел(перенос строки и т.п.) и символы, кроме . @ + - _"
        )

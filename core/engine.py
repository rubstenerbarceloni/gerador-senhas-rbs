from __future__ import annotations

import hashlib
import hmac
import math
import string
import unicodedata
from dataclasses import dataclass


ALGORITHM_VERSIONS = ("RBS-1", "RBS-2")
CURRENT_VERSION = "RBS-2"

UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits

PROFILE_SYMBOLS = {
    "Universal": "!@#$%&*+-_=?.",
    "Microsoft": "!@#$%&*+-_=?.",
    "Google": "!@#$%&*+-_=?.",
    "Apple": "!@#$%&*+-_=?.",
    "Bancos": "!@#$%&*+-_",
    "Gov.br": "!@#$%&*+-_",
    "Sem símbolos": "",
}

PROFILE_DESCRIPTIONS = {
    "Universal": "Letras, números e símbolos comuns.",
    "Microsoft": "Conjunto conservador de caracteres comuns.",
    "Google": "Conjunto conservador de caracteres comuns.",
    "Apple": "Conjunto conservador de caracteres comuns.",
    "Bancos": "Símbolos reduzidos para maior aceitação.",
    "Gov.br": "Símbolos reduzidos para maior aceitação.",
    "Sem símbolos": "Somente letras e números.",
}

ORIGINAL_SUFFIX = "@92#$&@#"
APP_DOMAIN = b"GERADOR-SENHAS-RBS"


@dataclass(frozen=True)
class PasswordPolicy:
    uppercase: bool = True
    lowercase: bool = True
    digits: bool = True
    symbols: bool = True


@dataclass(frozen=True)
class StrengthResult:
    score: int
    label: str
    estimated_bits: float


def remove_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(
        char for char in normalized
        if unicodedata.category(char) != "Mn"
    )


def clean_original_word(text: str) -> str:
    return "".join(
        char for char in remove_accents(text.strip())
        if char.isalpha()
    )


def normalize_field(text: str) -> str:
    """
    Normaliza dados contextuais para recuperar a mesma senha mesmo
    com diferenças de maiúsculas/minúsculas e espaços externos.
    """
    return " ".join(
        remove_accents(text.strip()).casefold().split()
    )


def generate_original_password(original_word: str) -> str:
    word = clean_original_word(original_word)

    if len(word) < 3:
        raise ValueError("Informe uma palavra com pelo menos três letras.")

    return (
        f"{word[-1].upper()}"
        f"$19"
        f"{word[0].lower()}"
        f"&02"
        f"{word[2].lower()}"
        f"{ORIGINAL_SUFFIX}"
    )


def _validate_intelligent_inputs(
    service: str,
    master_word: str,
    length: int,
    profile: str,
    version: str,
) -> None:
    if not normalize_field(service):
        raise ValueError("Informe o site, aplicativo ou sistema.")

    if len(master_word.strip()) < 4:
        raise ValueError(
            "A palavra mestra deve possuir pelo menos quatro caracteres."
        )

    if not 8 <= length <= 64:
        raise ValueError("Escolha um tamanho entre 8 e 64 caracteres.")

    if profile not in PROFILE_SYMBOLS:
        raise ValueError("Perfil de caracteres inválido.")

    if version not in ALGORITHM_VERSIONS:
        raise ValueError("Versão do algoritmo inválida.")


def _derive_bytes(
    *,
    service: str,
    username: str,
    master_word: str,
    length: int,
    profile: str,
    version: str,
    counter: int,
    output_length: int,
) -> bytes:
    """
    Deriva bytes pseudoaleatórios por HMAC-SHA256.

    A senha não é salva. Os mesmos dados sempre geram os mesmos bytes.
    """
    message = "|".join(
        [
            version,
            normalize_field(service),
            normalize_field(username),
            str(length),
            profile,
            str(counter),
        ]
    ).encode("utf-8")

    # A palavra mestra atua como chave do HMAC.
    key = (
        APP_DOMAIN
        + b"|"
        + unicodedata.normalize("NFC", master_word.strip()).encode("utf-8")
    )

    output = bytearray()
    block_counter = 1

    while len(output) < output_length:
        output.extend(
            hmac.new(
                key,
                message + block_counter.to_bytes(4, "big"),
                hashlib.sha256,
            ).digest()
        )
        block_counter += 1

    return bytes(output[:output_length])


def _character_groups(
    profile: str,
    policy: PasswordPolicy,
) -> list[str]:
    groups: list[str] = []

    if policy.uppercase:
        groups.append(UPPERCASE)
    if policy.lowercase:
        groups.append(LOWERCASE)
    if policy.digits:
        groups.append(DIGITS)
    if policy.symbols and PROFILE_SYMBOLS[profile]:
        groups.append(PROFILE_SYMBOLS[profile])

    if not groups:
        raise ValueError("Selecione pelo menos um tipo de caractere.")

    return groups


def generate_intelligent_password(
    *,
    service: str,
    username: str,
    master_word: str,
    length: int = 20,
    profile: str = "Universal",
    version: str = CURRENT_VERSION,
    counter: int = 1,
    policy: PasswordPolicy = PasswordPolicy(),
) -> str:
    """
    Gera uma senha de aparência aleatória e totalmente reproduzível.

    Entradas que precisam ser repetidas para recuperação:
    serviço + usuário + palavra mestra + tamanho + perfil + versão + contador.
    """
    _validate_intelligent_inputs(
        service=service,
        master_word=master_word,
        length=length,
        profile=profile,
        version=version,
    )

    if not 1 <= counter <= 99:
        raise ValueError("A variação deve estar entre 1 e 99.")

    groups = _character_groups(profile, policy)

    if length < len(groups):
        raise ValueError(
            "O tamanho é insuficiente para os tipos de caracteres selecionados."
        )

    byte_count = (length * 4) + 128
    random_bytes = _derive_bytes(
        service=service,
        username=username,
        master_word=master_word,
        length=length,
        profile=profile,
        version=version,
        counter=counter,
        output_length=byte_count,
    )

    characters: list[str] = []

    # Garante pelo menos um caractere de cada grupo selecionado.
    for index, group in enumerate(groups):
        characters.append(group[random_bytes[index] % len(group)])

    alphabet = "".join(groups)
    offset = len(groups)

    while len(characters) < length:
        byte_value = random_bytes[offset]
        characters.append(alphabet[byte_value % len(alphabet)])
        offset += 1

    # Fisher-Yates determinístico.
    for index in range(length - 1, 0, -1):
        swap_index = random_bytes[offset] % (index + 1)
        characters[index], characters[swap_index] = (
            characters[swap_index],
            characters[index],
        )
        offset += 1

    return "".join(characters)


def evaluate_strength(password: str) -> StrengthResult:
    if not password:
        return StrengthResult(0, "Não avaliada", 0.0)

    alphabet_size = 0
    if any(char.isupper() for char in password):
        alphabet_size += 26
    if any(char.islower() for char in password):
        alphabet_size += 26
    if any(char.isdigit() for char in password):
        alphabet_size += 10
    if any(not char.isalnum() for char in password):
        alphabet_size += 15

    estimated_bits = (
        len(password) * math.log2(max(alphabet_size, 1))
        if alphabet_size
        else 0.0
    )

    score = 0
    score += min(len(password) // 4, 4)
    score += int(any(char.isupper() for char in password))
    score += int(any(char.islower() for char in password))
    score += int(any(char.isdigit() for char in password))
    score += int(any(not char.isalnum() for char in password))
    score = min(score, 8)

    if score <= 3:
        label = "Fraca"
    elif score <= 5:
        label = "Razoável"
    elif score <= 7:
        label = "Forte"
    else:
        label = "Muito forte"

    return StrengthResult(score, label, estimated_bits)

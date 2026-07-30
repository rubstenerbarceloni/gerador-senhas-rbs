from core.engine import (
    PasswordPolicy,
    evaluate_strength,
    generate_intelligent_password,
    generate_original_password,
)


def run_tests() -> None:
    assert generate_original_password("Paulo") == "O$19p&02u@92#$&@#"
    assert generate_original_password("PAULO") == "O$19p&02u@92#$&@#"

    params = dict(
        service="gmail.com",
        username="rubstener",
        master_word="Paulo",
        length=20,
        profile="Universal",
        version="RBS-2",
        counter=1,
        policy=PasswordPolicy(),
    )

    first = generate_intelligent_password(**params)
    second = generate_intelligent_password(**params)

    assert first == second
    assert len(first) == 20
    assert any(char.isupper() for char in first)
    assert any(char.islower() for char in first)
    assert any(char.isdigit() for char in first)
    assert any(not char.isalnum() for char in first)

    changed = generate_intelligent_password(
        **{**params, "service": "facebook.com"}
    )
    assert changed != first

    no_symbols = generate_intelligent_password(
        service="exemplo.com",
        username="usuario",
        master_word="MinhaPalavra",
        length=16,
        profile="Sem símbolos",
        version="RBS-2",
        counter=1,
        policy=PasswordPolicy(symbols=False),
    )
    assert no_symbols.isalnum()

    strength = evaluate_strength(first)
    assert strength.score > 0

    print("Todos os testes foram aprovados.")
    print("Senha determinística de teste:", first)


if __name__ == "__main__":
    run_tests()

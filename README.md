<<<<<<< HEAD
# Gerador de Senhas - RBS 3.0

Aplicativo multiplataforma em Python e Flet. Nenhuma senha, palavra mestra
ou dado de conta é armazenado.

## Modos

### Clássico

Mantém a regra original:

```text
Paulo -> O$19p&02u@92#$&@#
```

### Inteligente

A senha é derivada de:

- site, aplicativo ou sistema;
- usuário;
- palavra mestra;
- tamanho;
- perfil de caracteres;
- versão do algoritmo;
- variação;
- tipos obrigatórios de caracteres.

Repetindo exatamente os mesmos dados, a mesma versão do aplicativo gera
a mesma senha.

## Executar no PyCharm

1. Descompacte o projeto.
2. Abra a pasta `Gerador_Senhas_RBS_v3` no PyCharm.
3. Configure Python 3.10 ou superior.
4. No Terminal do PyCharm, execute:

```bash
python -m pip install -r requirements.txt
python main.py
```

O arquivo principal é `main.py`.

## Testar a lógica

```bash
python tests/test_engine.py
```

## Gerar Windows

No Windows:

```bat
scripts\build_windows.bat
```

Depois, abra `installer\GeradorSenhasRBS.iss` no Inno Setup para criar
um instalador tradicional.

## Gerar Android

APK para instalação direta:

```bat
scripts\build_android_apk.bat
```

AAB para Google Play:

```bat
scripts\build_android_aab.bat
```

## Gerar iOS

O IPA exige macOS, Xcode e configuração de assinatura Apple:

```bash
bash scripts/build_ios.sh
```

## Recuperação

Anote ou memorize os parâmetros utilizados. O aplicativo não consegue
descobrir os parâmetros originais a partir da senha, pois não mantém arquivo,
histórico nem banco de dados.

## Segurança

O modo inteligente utiliza HMAC-SHA256 da biblioteca padrão do Python.
Ele oferece separação por serviço e reprodução determinística. Ainda assim,
uma palavra mestra fraca ou previsível reduz a segurança. Prefira uma frase
mestra longa, exclusiva e difícil de adivinhar.
=======
# gerador-senhas-rbs
gerador-senhas-rbs
>>>>>>> e61156e22e70d240829c89d9ddb774c58ce8008b

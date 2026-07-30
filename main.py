from __future__ import annotations

import inspect
from typing import Any

import flet as ft

from core.engine import (
    ALGORITHM_VERSIONS,
    CURRENT_VERSION,
    PROFILE_DESCRIPTIONS,
    PROFILE_SYMBOLS,
    PasswordPolicy,
    evaluate_strength,
    generate_intelligent_password,
    generate_original_password,
)


APP_NAME = "Gerador de Senhas - RBS"

# Compatibilidade entre versões do Flet.
COLORS = ft.Colors if hasattr(ft, "Colors") else ft.colors
ICONS = ft.Icons if hasattr(ft, "Icons") else ft.icons


def make_dropdown_option(value: str) -> Any:
    """Cria uma opção de Dropdown nas APIs nova e antiga do Flet."""
    if hasattr(ft, "DropdownOption"):
        return ft.DropdownOption(key=value, text=value)

    return ft.dropdown.Option(key=value, text=value)


def make_button(
    button_class: Any,
    label: str,
    *,
    icon: Any,
    on_click: Any,
    height: int | None = None,
) -> Any:
    """
    Cria botões de forma compatível com versões que usam:
    - text=
    - content=
    - primeiro argumento posicional
    """
    parameters = inspect.signature(button_class).parameters
    kwargs: dict[str, Any] = {
        "icon": icon,
        "on_click": on_click,
    }

    if height is not None:
        kwargs["height"] = height

    if "content" in parameters:
        kwargs["content"] = ft.Text(label)
        return button_class(**kwargs)

    if "text" in parameters:
        kwargs["text"] = label
        return button_class(**kwargs)

    return button_class(ft.Text(label), **kwargs)


def main(page: ft.Page) -> None:
    page.title = APP_NAME
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.padding = 16
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.bgcolor = COLORS.SURFACE

    # Configuração da janela desktop.
    if hasattr(page, "window"):
        page.window.width = 720
        page.window.height = 900
        page.window.min_width = 390
        page.window.min_height = 650

    password_is_visible = False

    title = ft.Text(
        APP_NAME,
        size=28,
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER,
    )

    subtitle = ft.Text(
        "Senhas reproduzíveis, sem banco de dados e sem armazenamento.",
        size=14,
        color=COLORS.ON_SURFACE_VARIANT,
        text_align=ft.TextAlign.CENTER,
    )

    original_word = ft.TextField(
        label="Palavra original",
        hint_text="Exemplo: Paulo",
        prefix_icon=ICONS.TEXT_FIELDS,
        border_radius=14,
        autocorrect=False,
        enable_suggestions=False,
        visible=False,
    )

    service = ft.TextField(
        label="Site, aplicativo ou sistema",
        hint_text="Exemplo: gmail.com",
        prefix_icon=ICONS.PUBLIC,
        border_radius=14,
        autocorrect=False,
        enable_suggestions=False,
        autofocus=True,
    )

    username = ft.TextField(
        label="Usuário ou identificação",
        hint_text="Exemplo: rubstener",
        prefix_icon=ICONS.PERSON,
        border_radius=14,
        autocorrect=False,
        enable_suggestions=False,
    )

    master_word = ft.TextField(
        label="Palavra mestra",
        hint_text="Use sempre exatamente a mesma",
        prefix_icon=ICONS.KEY,
        password=True,
        can_reveal_password=True,
        border_radius=14,
        autocorrect=False,
        enable_suggestions=False,
    )

    length_label = ft.Text(
        "Tamanho: 20 caracteres",
        weight=ft.FontWeight.W_600,
    )

    length_slider = ft.Slider(
        min=8,
        max=64,
        divisions=56,
        value=20,
        label="{value}",
    )

    profile = ft.Dropdown(
        label="Perfil de caracteres",
        value="Universal",
        options=[
            make_dropdown_option(name)
            for name in PROFILE_SYMBOLS
        ],
        border_radius=14,
    )

    profile_description = ft.Text(
        PROFILE_DESCRIPTIONS["Universal"],
        size=12,
        color=COLORS.ON_SURFACE_VARIANT,
    )

    version = ft.Dropdown(
        label="Versão do algoritmo",
        value=CURRENT_VERSION,
        options=[
            make_dropdown_option(item)
            for item in ALGORITHM_VERSIONS
        ],
        border_radius=14,
    )

    variation = ft.TextField(
        label="Variação",
        value="1",
        hint_text="1 a 99",
        prefix_icon=ICONS.REPEAT,
        keyboard_type=ft.KeyboardType.NUMBER,
        border_radius=14,
        width=150,
    )

    use_uppercase = ft.Checkbox(label="A–Z", value=True)
    use_lowercase = ft.Checkbox(label="a–z", value=True)
    use_digits = ft.Checkbox(label="0–9", value=True)
    use_symbols = ft.Checkbox(label="Símbolos", value=True)

    result = ft.TextField(
        label="Senha gerada",
        value="",
        read_only=True,
        password=True,
        can_reveal_password=False,
        prefix_icon=ICONS.PASSWORD,
        border_radius=14,
        expand=True,
        text_style=ft.TextStyle(
            size=18,
            weight=ft.FontWeight.BOLD,
            font_family="monospace",
        ),
    )

    status = ft.Text(
        "",
        size=13,
        text_align=ft.TextAlign.CENTER,
    )

    strength_label = ft.Text(
        "Força: não avaliada",
        weight=ft.FontWeight.BOLD,
    )

    strength_bar = ft.ProgressBar(value=0)
    requirements = ft.Text("", size=13)

    recovery_note = ft.Container(
        padding=14,
        border_radius=14,
        bgcolor=COLORS.SURFACE_CONTAINER_HIGHEST,
        content=ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Icon(ICONS.INFO_OUTLINE),
                        ft.Text(
                            "Recuperação futura",
                            weight=ft.FontWeight.BOLD,
                        ),
                    ]
                ),
                ft.Text(
                    "Modo clássico: repita a mesma palavra original.\n\n"
                    "Modo inteligente: repita exatamente o serviço, usuário, "
                    "palavra mestra, tamanho, perfil, versão, variação e tipos "
                    "de caracteres.\n\n"
                    "Nenhuma dessas informações é armazenada.",
                    size=13,
                ),
            ],
            spacing=8,
        ),
    )

    def show_status(message: str, error: bool = False) -> None:
        status.value = message
        status.color = COLORS.ERROR if error else COLORS.PRIMARY

    def update_strength() -> None:
        password = result.value or ""
        strength = evaluate_strength(password)

        strength_bar.value = strength.score / 8

        if password:
            strength_label.value = f"Força: {strength.label}"
        else:
            strength_label.value = "Força: não avaliada"

        if not password:
            requirements.value = ""
            return

        checks = [
            ("Maiúscula", any(char.isupper() for char in password)),
            ("Minúscula", any(char.islower() for char in password)),
            ("Número", any(char.isdigit() for char in password)),
            ("Símbolo", any(not char.isalnum() for char in password)),
            (f"{len(password)} caracteres", True),
        ]

        requirements.value = "  •  ".join(
            f"{'✓' if passed else '✗'} {name}"
            for name, passed in checks
        )

    intelligent_controls = ft.Column(
        controls=[
            service,
            username,
            master_word,
            length_label,
            length_slider,
            ft.ResponsiveRow(
                controls=[
                    ft.Container(
                        content=profile,
                        col={"sm": 12, "md": 6},
                    ),
                    ft.Container(
                        content=version,
                        col={"sm": 12, "md": 4},
                    ),
                    ft.Container(
                        content=variation,
                        col={"sm": 12, "md": 2},
                    ),
                ],
                spacing=10,
                run_spacing=10,
            ),
            profile_description,
            ft.Text(
                "Tipos obrigatórios",
                weight=ft.FontWeight.BOLD,
            ),
            ft.Row(
                controls=[
                    use_uppercase,
                    use_lowercase,
                    use_digits,
                    use_symbols,
                ],
                wrap=True,
            ),
        ],
        spacing=12,
        visible=True,
    )

    def update_mode(event: ft.ControlEvent | None = None) -> None:
        intelligent_mode = mode.value == "intelligent"
        original_word.visible = not intelligent_mode
        intelligent_controls.visible = intelligent_mode
        result.value = ""
        status.value = ""
        update_strength()
        page.update()

    def update_length(event: ft.ControlEvent) -> None:
        selected_length = int(float(event.control.value))
        length_label.value = f"Tamanho: {selected_length} caracteres"
        page.update()

    def update_profile(event: ft.ControlEvent | None = None) -> None:
        selected_profile = profile.value or "Universal"
        profile_description.value = PROFILE_DESCRIPTIONS[selected_profile]

        if selected_profile == "Sem símbolos":
            use_symbols.value = False
            use_symbols.disabled = True
        else:
            use_symbols.disabled = False

        page.update()

    def generate_password(event: ft.ControlEvent | None = None) -> None:
        try:
            if mode.value == "classic":
                generated_password = generate_original_password(
                    original_word.value or ""
                )
            else:
                try:
                    counter = int(variation.value or "1")
                except ValueError as error:
                    raise ValueError(
                        "A variação deve ser um número entre 1 e 99."
                    ) from error

                if not 1 <= counter <= 99:
                    raise ValueError(
                        "A variação deve ser um número entre 1 e 99."
                    )

                generated_password = generate_intelligent_password(
                    service=service.value or "",
                    username=username.value or "",
                    master_word=master_word.value or "",
                    length=int(length_slider.value or 20),
                    profile=profile.value or "Universal",
                    version=version.value or CURRENT_VERSION,
                    counter=counter,
                    policy=PasswordPolicy(
                        uppercase=bool(use_uppercase.value),
                        lowercase=bool(use_lowercase.value),
                        digits=bool(use_digits.value),
                        symbols=bool(use_symbols.value),
                    ),
                )

            result.value = generated_password
            show_status("Senha gerada com sucesso.")
            update_strength()

        except ValueError as error:
            result.value = ""
            show_status(str(error), error=True)
            update_strength()

        page.update()

    async def copy_password(
        event: ft.ControlEvent | None = None,
    ) -> None:
        if not result.value:
            show_status("Gere uma senha antes de copiar.", error=True)
            page.update()
            return

        try:
            # API mais antiga.
            if hasattr(page, "set_clipboard"):
                clipboard_result = page.set_clipboard(result.value)
                if inspect.isawaitable(clipboard_result):
                    await clipboard_result
            # API mais recente.
            elif hasattr(ft, "Clipboard"):
                clipboard = ft.Clipboard()
                clipboard_result = clipboard.set(result.value)
                if inspect.isawaitable(clipboard_result):
                    await clipboard_result
            else:
                raise RuntimeError(
                    "A API de área de transferência não está disponível."
                )

            show_status("Senha copiada para a área de transferência.")

        except Exception as error:
            show_status(
                f"Não foi possível copiar a senha: {error}",
                error=True,
            )

        page.update()

    def clear_fields(event: ft.ControlEvent | None = None) -> None:
        original_word.value = ""
        service.value = ""
        username.value = ""
        master_word.value = ""
        variation.value = "1"
        result.value = ""
        status.value = ""

        length_slider.value = 20
        length_label.value = "Tamanho: 20 caracteres"

        profile.value = "Universal"
        profile_description.value = PROFILE_DESCRIPTIONS["Universal"]

        version.value = CURRENT_VERSION

        use_uppercase.value = True
        use_lowercase.value = True
        use_digits.value = True
        use_symbols.value = True
        use_symbols.disabled = False

        update_strength()
        page.update()

    def toggle_password_visibility(
        event: ft.ControlEvent | None = None,
    ) -> None:
        nonlocal password_is_visible

        password_is_visible = not password_is_visible
        result.password = not password_is_visible

        show_button.icon = (
            ICONS.VISIBILITY_OFF
            if password_is_visible
            else ICONS.VISIBILITY
        )

        show_button.tooltip = (
            "Ocultar senha"
            if password_is_visible
            else "Mostrar senha"
        )

        page.update()

    def exit_app(event: ft.ControlEvent | None = None) -> None:
        if hasattr(page, "window"):
            close_result = page.window.close()
            return

        if hasattr(page, "window_close"):
            page.window_close()

    mode_content = ft.Row(
        controls=[
            ft.Radio(
                value="classic",
                label="Modo clássico",
            ),
            ft.Radio(
                value="intelligent",
                label="Modo inteligente",
            ),
        ],
        wrap=True,
    )

    # RadioGroup exige content em algumas versões.
    try:
        mode = ft.RadioGroup(
            content=mode_content,
            value="intelligent",
            on_change=update_mode,
        )
    except TypeError:
        mode = ft.RadioGroup(
            mode_content,
            value="intelligent",
            on_change=update_mode,
        )

    length_slider.on_change = update_length

    # on_change é compatível com mais versões do Dropdown.
    profile.on_change = update_profile

    original_word.on_submit = generate_password
    master_word.on_submit = generate_password

    generate_button = make_button(
        ft.FilledButton,
        "Gerar senha",
        icon=ICONS.AUTO_AWESOME,
        on_click=generate_password,
        height=48,
    )

    copy_button = make_button(
        ft.OutlinedButton,
        "Copiar",
        icon=ICONS.CONTENT_COPY,
        on_click=copy_password,
    )

    clear_button = make_button(
        ft.OutlinedButton,
        "Limpar",
        icon=ICONS.CLEAR,
        on_click=clear_fields,
    )

    exit_button = make_button(
        ft.TextButton,
        "Sair",
        icon=ICONS.LOGOUT,
        on_click=exit_app,
    )

    show_button = ft.IconButton(
        icon=ICONS.VISIBILITY,
        tooltip="Mostrar senha",
        on_click=toggle_password_visibility,
    )

    card = ft.Container(
        width=680,
        padding=24,
        border_radius=22,
        bgcolor=COLORS.SURFACE_CONTAINER,
        content=ft.Column(
            controls=[
                title,
                subtitle,
                ft.Divider(height=20),
                ft.Text(
                    "Escolha o tipo de geração",
                    weight=ft.FontWeight.BOLD,
                ),
                mode,
                original_word,
                intelligent_controls,
                generate_button,
                ft.Row(
                    controls=[
                        result,
                        show_button,
                    ],
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                ),
                ft.Row(
                    controls=[
                        copy_button,
                        clear_button,
                        exit_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    wrap=True,
                ),
                status,
                strength_label,
                strength_bar,
                requirements,
                recovery_note,
                ft.Text(
                    "Os perfis utilizam conjuntos conservadores de "
                    "caracteres. Cada serviço pode alterar suas próprias "
                    "regras de senha.",
                    size=11,
                    color=COLORS.ON_SURFACE_VARIANT,
                    text_align=ft.TextAlign.CENTER,
                ),
            ],
            spacing=14,
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
        ),
    )

    page.add(
        ft.SafeArea(
            content=ft.Container(
                alignment=ft.Alignment(0, 0),
                content=card,
            )
        )
    )


if __name__ == "__main__":
    if hasattr(ft, "run"):
        ft.run(main)
    else:
        ft.app(target=main)

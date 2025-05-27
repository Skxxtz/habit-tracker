ESC = "\033["
END = f"{ESC}0m"

colors = {
    "red": "31",
    "green": "32",
    "yellow": "33",
    "underline": "4",
    "bold": "1",
}


def text_format(decorations: list[str], string: str) -> str:
    codes = ";".join(colors[d] for d in decorations if d in colors)
    return f"{ESC}{codes}m{string}{END}"


def red(string: str) -> str:
    return text_format(["red"], string)


def green(string: str) -> str:
    return text_format(["green"], string)


def yellow(string: str) -> str:
    return text_format(["yellow"], string)


def underline(string: str) -> str:
    return text_format(["underline"], string)


def bold_underline(string: str) -> str:
    return text_format(["bold", "underline"], string)


def bold(string: str) -> str:
    return text_format(["bold"], string)


def percentage_gradient(f32: float) -> str:
    """
    This function evaluates a percentage into three colorized areas: (1) greeen, when x > 80%, (2) yellow, when 80 > x > 30, and (3) red, when x < 30

    Args:
        f32 (float): The percentage to be evaulated

    Returns:
        string (str): The formatted strin appended with a '%'
    """
    if f32 < 80:
        color = "yellow"
    elif f32 < 30:
        color = "red"
    else:
        color = "green"

    return text_format([color], f"{f32:.2f}%")

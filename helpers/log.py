def log(lines: list[str]) -> None:
    with open("logfile.txt", "w+") as file:
        file.writelines(lines)

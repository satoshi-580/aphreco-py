def _const_for_length(var: str, lines: str):
    length = lines.count("\n")
    return f"const LEN_{var}: usize = {length};\n"

def set_option(options, key, value):
    if key in options.keys():
        check_option_type(options[key], value)
        options[key] = value
    else:
        raise KeyError(f"invalid option key: {key}")
    return options


def check_option_type(old_value, new_value):
    if type(old_value) != type(new_value):
        raise TypeError(
            f"invalid option value: {new_value}\nexpected {type(old_value)}"
        )

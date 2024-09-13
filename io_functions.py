default_interval = 5        # seconds
max_interval = 600          # seconds
max_timeout = 300           # seconds
max_ttl = 500
max_16b = 65535


def get_input(val_type: type, def_val: str | int | None = None, *, minmax: (int, int) = None) -> str | int | None:
    """
    Takes user input and validates its type.

    :param val_type:    Expected type of user input
    :param def_val:     Default value of input if not None
    :param minmax:      Tuple (min, max) for range of accepted values

    :returns:           String or integer cast of input, otherwise None if input invalid

    :details:           If def_val is not None, this value will be returned in case that 
                        user enters a blank string, i.e. presses enter.
    """
    while True:
        val = input()
        print("\n")

        # User presses enter
        if def_val is not None and val == "":
            return def_val

        else:
            try:
                # Validate type
                val = val_type(val)
                # Validate range if specified
                if minmax is None or validate_range(val, minmax[0], minmax[1]):
                    return val

            # Invalid type
            except ValueError:
                type_str = "a string" if val_type is str else "an integer"
                print(f"Input value must be {type_str}!")


def validate_range(val: int, min: int, max: int) -> bool:
    """
    Validates that integer is in specified range.

    :param val:         integer to validate
    :param min:         lower bound
    :param max:         upper bound

    :returns:           True if valid; False if invalid
    """
    if not min <= val <= max:
        print(f"Input must be between {min} and {max}!")
        return False
    return True


def get_input_interval() -> int:
    """
    Helper function for get_input().
    Accepts and returns an interval value from user.
    """
    print("At what interval (seconds) should I check this service?")
    print(f"Press enter to leave at default value ({default_interval}s).")
    return get_input(int, default_interval, minmax=(1, max_interval))


def get_input_timeout(default: int = 5) -> int:
    """
    Helper function for get_input().
    Accepts and returns a timeout value from user.
    """
    print("Input check timeout (in seconds).")
    print(f"Press enter to leave at default value ({default}s).")
    return get_input(int, default, minmax=(1, max_timeout))


def get_input_ttl(default: int = 64) -> int:
    """
    Helper function for get_input().
    Accepts and returns a TTL value from user.
    """
    print("Input check TLL.")
    print(f"Press enter to leave at default value ({default}).")
    return get_input(int, default, minmax=(1, max_ttl))


def get_input_sequeunce_number(default: int = 1) -> int:
    """
    Helper function for get_input().
    Accepts and returns a sequence number from user.
    """
    print("Input check sequence number.")
    print(f"Press enter to leave at default value.")
    return get_input(int, default, minmax=(1, max_16b))


def get_input_port_number() -> int:
    """
    Helper function for get_input().
    Accepts and returns a port number from user.
    """
    print("Input port number.")
    while True:
        port = get_input(int, minmax=(1, max_16b))
        if get_input_confirmation(f"You've input {port}. Is that correct?"):
            return port
        print("Please enter the correct port number")


def get_input_confirmation(choice: str | int) -> bool:
    """
    Confirms choice with user.

    :param choice:  Chosen input to confirm
    :returns:       True if confirmed, else False
    """
    print(choice)
    print("1. Yes")
    print("2. No")
    user_input = get_input(int, 1, minmax=(1,2))
    return True if user_input == 1 else False


def select_from_list(options: list) -> int:
    """
    Prints numbered list and take user input selection.

    :param options:     list of options to pick from
    :returns:           list index of selection (e.g. printed item 1 will be returned as 0!)
    """
    list_options(options)
    length = len(options)
    return get_input(int, 0, minmax=(1,length))-1


def get_input_manual(term: str, *, back: bool = False) -> str | None:
    """
    Take user input value.

    :param term:    name of value to input
    :param back:    if True, gives user ability to undo their selection

    :returns:       Input value; None if user chose to go back
    """
    if back:
        print(f"Input {term}, or press Enter to go back")
    else:
        print(f"Input {term}")
    while True:
        val = get_input(str, "back")
        if back and val == "back":
            return None
        if get_input_confirmation(f"You've input {val}. Is that correct?"):
            return val
        print(f"Please re-enter the correct {term}")


def list_options(options: list) -> None:
    """
    Prints numbered list of options

    :param options:     list of options to print
    """
    print("Please enter the number of your selection.")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")
    print("")


def print_config(config: dict) -> None:
    print("Current configuration:")
    for m_name, services in config.items():
        print(
            "\n",
            m_name, "--",
            services["socket"]["ip"], ":",
            services["socket"]["port"]
        )

        for s_name in services["checks"]:
            print("\n    ", s_name, "checks")

            if (checks := services["checks"][s_name]) is not None:
                for n, check in enumerate(checks):
                    print("\n        --------------------")
                    print("        Check ", n+1)
                    for attr, val in check.items():
                        print("         ", attr, ": ", val)
                print("\n")


def main():
    pass


if __name__ == '__main__':
    main()

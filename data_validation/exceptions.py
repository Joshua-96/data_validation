class CastException(Exception):
    def __init__(self, input_type: type, output_type: type, message: str, *args: object) -> None:
        message = "Casting from " + \
            f"{input_type} to {output_type} failed details: \n {message}"
        super().__init__(message, *args)


class UnexpectedCastException(Exception):
    def __init__(self, input_type: type, output_type: type, message: str, *args: object) -> None:
        message = "Unexcepted Exception was raised during Casting: " + \
            f"{input_type.__name__} to {output_type.__name__} details: \n {message}"
        super().__init__(message, *args)
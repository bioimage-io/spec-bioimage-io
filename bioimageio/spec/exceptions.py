from marshmallow import ValidationError


class UnconvertibleError(ValidationError):
    """raised by <version submodule>.converters.maybe_convert()"""

    pass

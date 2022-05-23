import typing

from marshmallow.validate import (
    ContainsNoneOf,
    Equal,
    Length,
    OneOf,
    Predicate as MarshmallowPredicate,
    Range,
    URL as MarshmallowURL,
    ValidationError,
    Validator,
)

ContainsNoneOf = ContainsNoneOf
Equal = Equal
Length = Length
OneOf = OneOf
Range = Range


class Attribute(Validator):

    default_message = "Invalid input."

    def __init__(
        self,
        attribute: str,
        validate: typing.Union[
            typing.Callable[[typing.Any], typing.Any], typing.Iterable[typing.Callable[[typing.Any], typing.Any]]
        ],
        is_getter_method: bool = False,
    ):
        self.attribute = attribute
        self.is_getter_method = is_getter_method
        self.validate = [validate] if callable(validate) else validate

    def _repr_args(self) -> str:
        return "attribute={!r}, is_getter_method={!r}, validate={!r}".format(
            self.attribute, self.is_getter_method, self.validate
        )

    def __call__(self, value: typing.Any) -> typing.Any:
        try:
            attr = getattr(value, self.attribute)
            if self.is_getter_method:
                attr = attr()
        except Exception as e:
            raise ValidationError(str(e)) from e

        try:
            return all(validator(attr) for validator in self.validate)
        except Exception as e:
            raise ValidationError(f"Invalid {self.attribute} ({value}): {str(e)}") from e


class Predicate(MarshmallowPredicate):
    """extends marshmallow.Predicate by accepting *args and 'invert_output' .
    Call the specified ``method`` of the ``value`` object. The
    validator succeeds if the invoked method returns an object that
    evaluates to True in a Boolean context. Any additional arguments
    and keyword arguments will be passed to the method.

    :param method: The name of the method to invoke.
    :param args: Additional arguments to pass to the method.
    :param invert_output: Flag to succeed if method returns an object that evaluates to False instead of True.
    :param error: Error message to raise in case of a validation error.
        Can be interpolated with `{input}` and `{method}`.
    :param kwargs: Additional keyword arguments to pass to the method.
    """

    default_message = "Invalid input."

    def __init__(self, method: str, *args, invert_output: bool = False, error: typing.Optional[str] = None, **kwargs):
        super().__init__(method, error=error, **kwargs)
        self.args = args
        self.invert_output = invert_output

    def _format_error(self, value: typing.Any) -> str:
        return self.error.format(input=value, method=self.method, args=self.args, invert_output=self.invert_output)

    def _repr_args(self) -> str:
        return "method={!r}, invert_output={!r}, args={!r}, kwargs={!r}".format(
            self.method, self.invert_output, self.args, self.kwargs
        )

    def __call__(self, value: typing.Any) -> typing.Any:
        method = getattr(value, self.method)

        ret = method(*self.args, **self.kwargs)
        if self.invert_output:
            ret = not ret

        if not ret:
            raise ValidationError(self._format_error(value))

        return value


class URL(MarshmallowURL):
    def __call__(self, value: typing.Any):
        return super().__call__(str(value))  # cast value which might be a raw_nodes.URI to string

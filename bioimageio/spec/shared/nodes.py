import pydantic


if pydantic.VERSION == "2.0b2":

    class Node(  # type: ignore
        pydantic.BaseModel,
    ):
        model_config = dict(
            extra=pydantic.Extra.forbid,
            allow_mutation=False,  # removed in V2!
            # underscore_attrs_are_private=True,  # removed; always True in V2
            validate_assignment=True,
        )

else:

    class Node(
        pydantic.BaseModel,
        extra=pydantic.Extra.forbid,
        allow_mutation=False,
        underscore_attrs_are_private=True,
        validate_assignment=True,
    ):
        pass

from typing import Any, Callable, Dict, List, Optional, Union

import pydantic


# slimmed down version of pydantic.Field with explicit extras
def Field(  # noqa C901  NOSONAR: S1542
    default: Any = ...,
    *,
    default_factory: Optional[Callable[[], Any]] = None,
    alias: Optional[str] = None,
    validation_alias: Union[str, pydantic.AliasPath, pydantic.AliasChoices, None] = None,
    description: Optional[str] = None,
    examples: Optional[List[Any]] = None,
    exclude: Optional[bool] = None,
    discriminator: Optional[str] = None,
    kw_only: Optional[bool] = None,
    pattern: Optional[str] = None,
    strict: Optional[bool] = None,
    gt: Optional[float] = None,
    ge: Optional[float] = None,
    lt: Optional[float] = None,
    le: Optional[float] = None,
    multiple_of: Optional[float] = None,
    allow_inf_nan: Optional[bool] = None,
    max_digits: Optional[int] = None,
    decimal_places: Optional[int] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    # explicit extra fields (fixed here, but 'extra' for pydantic)
    in_package: bool = False,
) -> Any:
    """wrap pydantic.Field"""
    extra: Dict[str, Any] = dict(in_package=in_package)
    return pydantic.Field(
        default,
        default_factory=default_factory,
        alias=alias,
        validation_alias=validation_alias,
        description=description,
        examples=examples,
        exclude=exclude,
        discriminator=discriminator,
        kw_only=kw_only,
        pattern=pattern,
        strict=strict,
        gt=gt,
        ge=ge,
        lt=lt,
        le=le,
        multiple_of=multiple_of,
        allow_inf_nan=allow_inf_nan,
        max_digits=max_digits,
        decimal_places=decimal_places,
        min_length=min_length,
        max_length=max_length,
        **extra,
    )

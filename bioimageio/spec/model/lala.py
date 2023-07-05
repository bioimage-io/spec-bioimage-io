from typing import Annotated, Literal, Union
from pydantic import BaseModel, Field


class A(BaseModel):
    type: Literal["a"]
    a: int


class A2(BaseModel):
    type: Literal["a"]
    a: tuple[int, int]


class B(BaseModel):
    type: Literal["b"]


class Parent(BaseModel):
    child: Annotated[Union[A, A2, B], Field(discriminator="type")]


# class Parent(BaseModel):
#     child: Annotated[Union[Union[A, A2], B], Field(discriminator="type")]


print(Parent.model_validate(dict(type="a", a="2")))

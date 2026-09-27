from pydantic import BaseModel, ValidationError

from errors import HttpError


class RegisterUser(BaseModel):
    username: str
    email: str
    password: str


class LoginUser(BaseModel):
    username: str
    password: str

class CreateAds(BaseModel):
    title: str


class UpdateAds(BaseModel):
    title: str


def validate(json_data: dict, schema_cls: type[RegisterUser | CreateAds | UpdateAds | LoginUser]) -> dict:
    try:
        return schema_cls(**json_data).model_dump()
    except ValidationError as err:
        errors = err.errors()
        for e in errors:
            e.pop("ctx", None)
        raise HttpError(errors, 400)

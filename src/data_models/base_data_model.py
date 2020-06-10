from typing import List, Union

from pydantic import BaseModel


class APIBaseModelExtend(BaseModel):
    msg: Union[str, dict]
    type: str


class APIBaseModel(BaseModel):
    detail: List[APIBaseModelExtend]

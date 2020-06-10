from pydantic import BaseModel


class CreateWallet(BaseModel):
    name: str
    passphrase: str


class DeleteWallet(BaseModel):
    name: str


class CreateDID(BaseModel):
    name: str
    passphrase: str
    seed: str = None

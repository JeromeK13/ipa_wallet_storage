from typing import Union

import sbca_wrapper.error as indy_error
from fastapi import APIRouter, HTTPException

from src.data_models.base_data_model import APIBaseModel
from src.data_models.indy_data_model import CreateWallet, DeleteWallet, \
    CreateDID
from src.services.azure_storage import delete_wallet
from src.services.custom_errors import WalletAlreadyExists, WalletDoesNotExists
from src.services.indy import create_wallet, query_wallet, create_did

# Init APIRouter
router = APIRouter()


def _return_response_model(message_detail: Union[str, dict],
                           message_type: str) -> dict:
    """HelperFunction to return correct ResponseModel on Success

    :param message_detail: str or dict - Message that will be in msg
    :param message_type: str - Message type defined like:
    "interaction_'success/error etc'_(status code if available)"
    :return: dict - Dictionary with the expected Response format
    of the defined response_model
    """
    return {'detail': [{'msg': message_detail, 'type': message_type}]}


def _return_exception_model(message_detail: str, message_type: str) -> list:
    """HelperFunction to return correct ResponseModel on Exception

    :param message_detail: str - Message that will be in msg
    :param message_type: str - Message type defined like:
    "interaction_'success/error etc'_(status code if available)"
    :return: list - List with the expected Response format
    of the defined response_model
    """
    return [{'msg': message_detail, 'type': message_type}]


@router.post('/{account_id}/wallet', response_model=APIBaseModel)
async def create_wallet_for_account_id(account_id: str,
                                       req_body: CreateWallet) -> dict:
    """Endpoint to create a Wallet for a AccountID in the Azure-Cloud-Storage

    :param account_id: str - AccountID of the caller
    :param req_body: dict - Request Body of the POST-Request with keys:
    [name, passphrase]
    :except WalletAlreadyExistsError: str - Wallet already exists
    in local Storage
    :except UnknownWalletTypeError: str - Unknown wallet type got used
    to try to create a wallet
    :except WalletStorageError: str - Wallet storage experience some
    problems during the creation
    :except LibIndyError: str - This exception handles all LibindyErrors
    :return: dict - APIBaseModel
    """
    try:
        message = await create_wallet(account_id=account_id,
                                      wallet_name=req_body.name,
                                      passphrase=req_body.passphrase)
        return _return_response_model(message_detail=message,
                                      message_type='request_success')
    except WalletAlreadyExists:
        raise HTTPException(status_code=409, detail=_return_exception_model(
            message_detail=f'AccountID already has a Wallet called: '
                           f'{req_body.name}',
            message_type=f'azure_error.409'))
    except indy_error.WalletAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=_return_exception_model(
            message_detail=e.message,
            message_type=f'indy_error.{e.indy_code}'))
    except indy_error.LibindyError as e:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail=e.message,
            message_type=f'indy_error.{e.indy_code}'))
    except Exception:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail='Internal Server Error',
            message_type=f'server_error_500'))


@router.delete('/{account_id}/wallet', response_model=APIBaseModel)
def delete_wallet_for_account_id(account_id: str,
                                 req_body: DeleteWallet) -> dict:
    """Endpoint to delete a Wallet for the AccountID of the Azure-Cloud-Storage

    :param account_id: str - AccountID of the caller
    :param req_body: dict - Request Body of the DELETE-Request with keys:[name]
    :except WalletDoesNotExists: Exception when Wallet can't be found in the
    Azure Cloud Storage
    :except Exception: Broad Exception to handle all of them
    :return: dict - APIBaseModel
    """
    try:
        message = delete_wallet(account_id=account_id,
                                wallet_name=req_body.name)
        return _return_response_model(message_detail=message,
                                      message_type='request_success')
    except WalletDoesNotExists:
        raise HTTPException(status_code=404, detail=_return_exception_model(
            message_detail='Wallet does not exists under this AccountID',
            message_type=f'azure_error.404'))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail=str(e),
            message_type=f'azure_error'))


@router.get('/{account_id}/{wallet_name}', response_model=APIBaseModel)
async def get_wallet_info(account_id: str, wallet_name: str,
                          wallet_passphrase: str):
    """Endpoint to get information about the stored Data in the Wallet from
    the Azure-Cloud-Storage

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - The name of the folder how its stored in
    the Azure-Cloud
    :param wallet_passphrase: str - Wallet passphrase which will be used to
    unlock (open) the wallet
    :except WalletDoesNotExists: Exception when Wallet can't be found in the
    Azure Cloud Storage
    :except LibIndyError: str - This exception handles all LibindyErrors
    :return: dict - APIBaseModel
    """
    try:
        message = await query_wallet(account_id=account_id,
                                     wallet_name=wallet_name,
                                     wallet_passphrase=wallet_passphrase)
        return _return_response_model(message_detail=message,
                                      message_type='request_success')
    except WalletDoesNotExists:
        raise HTTPException(status_code=404, detail=_return_exception_model(
            message_detail='Wallet does not exists under this AccountID',
            message_type=f'azure_error.404'))
    except indy_error.LibindyError as e:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail=e.message,
            message_type=f'indy_error.{e.indy_code}'))
    except Exception:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail='Internal Server Error',
            message_type=f'server_error_500'))


@router.post('/{account_id}/did', response_model=APIBaseModel)
async def create_did_in_wallet(account_id: str, req_body: CreateDID):
    """Endpoint to create a Decentralized Identifiers inside the callers Wallet

    :param account_id: str - AccountID of the caller
    :param req_body: dict - Request Body of the DELETE-Request with keys:
    [name, passphrase, (seed)]
    :except WalletDoesNotExists: Exception when Wallet can't be found in the
    Azure Cloud Storage
    :except LibIndyError: str - This exception handles all LibindyErrors
    :return: dict - APIBaseModel
    """
    try:
        message = await create_did(account_id, wallet_name=req_body.name,
                                   wallet_passphrase=req_body.passphrase,
                                   seed=req_body.seed)
        return _return_response_model(message_detail=message,
                                      message_type='request_success')
    except WalletDoesNotExists:
        raise HTTPException(status_code=404, detail=_return_exception_model(
            message_detail='Wallet does not exists under this AccountID',
            message_type=f'azure_error.404'))
    except indy_error.LibindyError as e:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail=e.message,
            message_type=f'indy_error.{e.indy_code}'))
    except Exception:
        raise HTTPException(status_code=500, detail=_return_exception_model(
            message_detail='Internal Server Error',
            message_type=f'server_error_500'))

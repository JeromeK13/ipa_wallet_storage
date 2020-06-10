import shutil
from pathlib import Path

from sbca_wrapper import Wallet, DID, Anoncreds, Pairwise

from src.services.azure_storage import download_wallet, upload_wallet, \
    user_has_wallet
from src.services.custom_errors import WalletAlreadyExists
from src.services.logger import get_logger

_logger = get_logger()


async def create_wallet(account_id: str, wallet_name: str,
                        passphrase: str) -> str:
    """Function to create a Wallet through our SBC-Python-Wrapper and upload
    it to the Azure-Cloud-Storage

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - WalletName(Foldername) where the wallet is stored
    :param passphrase: str - Passphrase which will be used to open the Wallet
    :raises WalletAlreadyExistsError: Raised if a wallet with the given id
        already exists in the specified wallet storage.
    :raises UnknownWalletTypeError: Raised if the specified wallet storage
        type is not registered.
    :return: str - Success Message with the needed information
    """
    if user_has_wallet(account_id=account_id, wallet_name=wallet_name):
        raise WalletAlreadyExists
    _logger.info(
        msg=f'Creating wallet for account: {account_id} with name: '
            f'{wallet_name}')
    local_wallet_name = f'{account_id}_{wallet_name}'
    wallet_config = {'id': local_wallet_name}
    wallet_credential = {'key': passphrase}
    await Wallet.create_wallet(wallet_config=wallet_config,
                               wallet_credentials=wallet_credential)
    _logger.info(msg=f'Upload wallet to Azure Cloud Storage')
    upload_wallet(account_id=account_id, wallet_name=wallet_name)
    # Delete Local Instance
    _logger.info(msg=f'Delete local folder for wallet')
    shutil.rmtree(
        Path.home() / '.indy_client' / 'wallet' /
        f'{account_id}_{wallet_name}')
    return f'Successfully create Wallet: {wallet_name} for AccountID: ' \
           f'{account_id}'


async def open_wallet(wallet_name: str, passphrase: str) -> int:
    """ Opens the Wallet with the given passphrase (Wallet has to be locally
    available)

    :param wallet_name: str - Wallet name (Foldername)
    :param passphrase: str - Wallet passphrase which will be used to unlock
    (open) the wallet
    :return: int - Wallet handle which is a local identifier to operate with
    the open wallet
    """
    _logger.info(msg=f'Open wallet: {wallet_name}')
    wallet_config = {'id': wallet_name}
    wallet_credentials = {'key': passphrase}
    return await Wallet.open_wallet(wallet_config=wallet_config,
                                    wallet_credentials=wallet_credentials)


async def close_wallet(wallet_handle: int) -> None:
    """ Closes the Wallet of the given handle

    :param wallet_handle: int - Wallet handle which was created by calling open
    _wallet()
    :return: None
    """
    _logger.info(msg=f'Close wallet for handle: {wallet_handle}')
    await Wallet.close_wallet(wallet_handle=wallet_handle)


async def query_wallet(account_id: str, wallet_name: str,
                       wallet_passphrase: str) -> dict:
    """ Query the Wallet to get the stored Data and return it as dict

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - Wallet name of the caller (download wallet and
    read the data of it)
    :param wallet_passphrase: str - Wallet passphrase which will be used to
    "unlock" (open) the wallet
    :return: dict - Dictionary with the following keys [credentials, dids,
    pairwise]
    """
    # Downloads Wallet
    download_wallet(account_id=account_id, wallet_name=wallet_name)
    _logger.info(
        msg=f'Download wallet: {wallet_name} for account: {account_id}')
    # Open Wallet and store handle (identifier of for the Wallet locally)
    wallet_handle = await open_wallet(
        wallet_name=f'{account_id}_{wallet_name}',
        passphrase=wallet_passphrase)
    _logger.info(
        msg=f'Wallet: {wallet_name} opened with handle: {wallet_handle}')
    # Get DID, Creds and Pairwise connections
    _logger.info(msg=f'Read wallet for DIDs, Credentials and Pairwise')
    did_list = await DID.get_dids_with_metadata(wallet_handle=wallet_handle)
    cred_list = await Anoncreds.get_credentials(wallet_handle=wallet_handle,
                                                credential_filter={})
    pairwise_list = await Pairwise.list_pairwise(wallet_handle=wallet_handle)
    return_object = {
        'credentials': cred_list,
        'dids': did_list,
        'pairwise': pairwise_list
    }
    # Close Wallet
    _logger.info(msg=f'Close wallet of handle: {wallet_handle}')
    await close_wallet(wallet_handle=wallet_handle)
    shutil.rmtree(
        Path.home() / '.indy_client' / 'wallet' /
        f'{account_id}_{wallet_name}')
    return return_object


async def create_did(account_id: str, wallet_name: str, wallet_passphrase: str,
                     seed: str) -> dict:
    """ Creates a new DID and Verkey in the callers Wallet

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - Wallet name of the caller (download wallet and
    read the data of it)
    :param wallet_passphrase: str - Wallet passphrase which will be used to
    "unlock" (open) the wallet
    :param seed: str - Seed that can be used to generate a DID, if no seed is
    present a random one will be taken
    :return: dict - Dictionary with the following keys [did, verkey]
    """
    download_wallet(account_id=account_id, wallet_name=wallet_name)
    _logger.info(
        msg=f'Download wallet: {wallet_name} for account: {account_id}')
    # Open Wallet and store handle (identifier of for the Wallet locally)
    wallet_handle = await open_wallet(
        wallet_name=f'{account_id}_{wallet_name}',
        passphrase=wallet_passphrase)
    _logger.info(
        msg=f'Wallet: {wallet_name} opened with handle: {wallet_handle}')
    # Create and store a new DID for the given Wallet handle
    did, verkey = await DID.create_and_store_did(wallet_handle=wallet_handle,
                                                 did_json={'seed': seed})
    _logger.info(msg=f'Created did: {did} for wallet: {wallet_name}')
    _logger.info(msg=f'Close wallet of handle: {wallet_handle}')
    await close_wallet(wallet_handle=wallet_handle)
    """The Wallet needs to be uploaded after an operation has been done
    (else it could be that different microservices
    override them self with different operations"""
    _logger.info(
        msg=f'Upload wallet: {wallet_name} of account_id: {account_id}')
    upload_wallet(account_id=account_id, wallet_name=wallet_name)
    shutil.rmtree(
        Path.home() / '.indy_client' / 'wallet' /
        f'{account_id}_{wallet_name}')
    return {
        'did': did,
        'verkey': verkey
    }

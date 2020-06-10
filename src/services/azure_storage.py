import os
import shutil
from pathlib import Path
from typing import Optional

from azure.storage.file import FileService
from dotenv import load_dotenv

from src.services.custom_errors import WalletDoesNotExists

LOCAL_STORAGE: Path = Path.home() / '.indy_client' / 'wallet'
# Load the .env file to get all needed connection strings etc.
load_dotenv()
# Init FileService instance
STORAGE = FileService(account_name=os.environ.get('AZURE_ACCOUNT_NAME'),
                      account_key=os.environ.get('AZURE_STORAGE_KEY'))


def user_has_wallet(account_id: str, wallet_name: str) -> bool:
    """ Checks if the AccountID has already an existing Wallet under that name

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - Wallet name when AccountID
    could have multiple wallets
    :return: boolean
    """
    az_directory = Path() / account_id / wallet_name
    return STORAGE.exists(share_name=os.environ.get('AZURE_WALLETS_SHARE'),
                          directory_name=az_directory,
                          file_name='sqlite.db')


def upload_wallet(account_id: str, wallet_file_path: Optional[str] = None,
                  wallet_name: Optional[str] = 'default',
                  file_name: Optional[str] = 'sqlite.db') -> None:
    """ Uploads a Wallet file to the Azure Cloud Storage

    :param account_id: str - AccountID of the caller
    :param wallet_file_path: Optional[str] - Wallet file path when wallet
    is not in default directory
    :param wallet_name: Optional[str] - Wallet name when AccountID
    could have multiple wallets
    :param file_name: Optional[str] - File name when File is renamed
    :return: None
    """
    # Check which Filepath to use
    if not wallet_file_path:
        wallet_file_path = LOCAL_STORAGE / f'{account_id}_{wallet_name}' \
                           / 'sqlite.db'

    az_directory = Path() / account_id / wallet_name
    parent_directory_list = [account_id, f'{account_id}', az_directory]
    # Since you can not recursive create Folders in AZ-Cloud
    # we need to loop it (when it does not exist)
    if not STORAGE.exists(share_name=os.environ.get('AZURE_WALLETS_SHARE'),
                          directory_name=az_directory):
        for d in parent_directory_list:
            STORAGE.create_directory(
                share_name=os.environ.get('AZURE_WALLETS_SHARE'),
                directory_name=d)
    # Upload the File to the given Path
    STORAGE.create_file_from_path(
        share_name=os.environ.get('AZURE_WALLETS_SHARE'),
        directory_name=az_directory,
        file_name=file_name,
        local_file_path=str(wallet_file_path))


def delete_wallet(account_id: str, wallet_name: str) -> str:
    """ Deletes a Wallet directory from the Azure Cloud Storage

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - Wallet name which should get deleted
    :return: str - Successful response message
    """
    az_directory = Path() / account_id / wallet_name
    if STORAGE.exists(share_name=os.environ.get('AZURE_WALLETS_SHARE'),
                      directory_name=az_directory):
        # The directory has to be empty so we delete the file first
        STORAGE.delete_file(share_name=os.environ.get('AZURE_WALLETS_SHARE'),
                            directory_name=az_directory,
                            file_name='sqlite.db')
        # Delete Empty directory from AZ-Cloud
        STORAGE.delete_directory(
            share_name=os.environ.get('AZURE_WALLETS_SHARE'),
            directory_name=az_directory)
        return f'Wallet: {wallet_name} ' \
               f'successfully deleted from the Azure Cloud Storage'
    raise WalletDoesNotExists


def download_wallet(account_id: str, wallet_name: str) -> None:
    """ Downloads the Wallet file to the standard Indy-Folder

    :param account_id: str - AccountID of the caller
    :param wallet_name: str - Wallet name which should be downloaded

    :return: None
    """
    if not user_has_wallet(account_id=account_id, wallet_name=wallet_name):
        raise WalletDoesNotExists

    shutil.rmtree(
        Path.home() / '.indy_client' / 'wallet'
        / f'{account_id}_{wallet_name}', ignore_errors=True)
    wallet_folder_path = LOCAL_STORAGE / f'{account_id}_{wallet_name}'
    wallet_file_path = \
        LOCAL_STORAGE / f'{account_id}_{wallet_name}' / 'sqlite.db'
    az_directory = Path() / account_id / wallet_name
    wallet_folder_path.mkdir(parents=True)
    STORAGE.get_file_to_path(share_name=os.environ.get('AZURE_WALLETS_SHARE'),
                             directory_name=az_directory,
                             file_name='sqlite.db',
                             file_path=str(wallet_file_path))

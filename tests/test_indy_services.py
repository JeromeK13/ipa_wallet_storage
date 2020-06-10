import asyncio
import unittest
from pathlib import Path

from src.services.azure_storage import delete_wallet
from src.services.indy import create_wallet, query_wallet, create_did

loop = asyncio.get_event_loop()

# Configurations Variables for the Unittest
ACCOUNT_ID = 'testAccount123'
WALLET_NAME = 'testWalletName123'
WALLET_PASSPHRASE = 'testWalletPassphrase123'
FOLDER_PATH = Path.home() / '.indy_client' / 'wallet' / ACCOUNT_ID
SEED = '12312312312312312312312312312312'


class TestIndyMethods(unittest.TestCase):

    def test_wallet_creation(self):
        res = loop.run_until_complete(
            create_wallet(account_id=ACCOUNT_ID, wallet_name=WALLET_NAME,
                          passphrase=WALLET_PASSPHRASE))
        self.assertEqual(res,
                         f'Successfully create Wallet: '
                         f'{WALLET_NAME} for AccountID: {ACCOUNT_ID}')

    def test_wallet_query(self):
        res = loop.run_until_complete(
            query_wallet(account_id=ACCOUNT_ID, wallet_name=WALLET_NAME,
                         wallet_passphrase=WALLET_PASSPHRASE))
        self.assertEqual(res, {'credentials': [], 'dids': [], 'pairwise': []})

    def test_did_creation(self):
        res = loop.run_until_complete(
            create_did(account_id=ACCOUNT_ID, wallet_name=WALLET_NAME,
                       wallet_passphrase=WALLET_PASSPHRASE, seed=SEED)
        )
        self.assertEqual(res,
                         {'did': 'JyLVbQi9J4u5zSXpwLyC68',
                          'verkey':
                              'Ao7JKEtCikMoWqgzt44EAuJy9A52oWNMYZfuGiJLJMPR'})

    def test_wallet_cloud_storage_deletion(self):
        res = delete_wallet(account_id=ACCOUNT_ID, wallet_name=WALLET_NAME)
        self.assertEqual(res,
                         f'Wallet: {WALLET_NAME} '
                         f'successfully deleted from the Azure Cloud Storage')

from src.services.logger import get_logger

_logger = get_logger()


class WalletAlreadyExists(Exception):
    _logger.error('Wallet already exists')
    pass


class WalletDoesNotExists(Exception):
    _logger.error('Wallet does not exist')
    pass

from myapp.exceptions.custom_exception import CustomException


class NotEnoughMoneyException(CustomException):
    pass


class NotEnoughStocksException(CustomException):
    pass


class InvalidNumberOfStocksExceptions(CustomException):
    pass

# standard library imports
from abc import ABC, abstractmethod


# abstract class for logger here
class Logger(ABC):

    @abstractmethod
    def debug(self, message: str) -> None:
        pass

    @abstractmethod
    def info(self, message: str) -> None:
        pass

    @abstractmethod
    def warning(self, message: str) -> None:
        pass

    @abstractmethod
    def error(self, message: str) -> None:
        pass

    @abstractmethod
    def exception(self, message: str) -> None:
        pass

    @abstractmethod
    def custom_debug_log(self, message: str) -> None:
        pass

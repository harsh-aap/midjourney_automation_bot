# Standard library imports
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Optional


class DailyFactors(ABC):
    @abstractmethod
    def get_factors(self, date: Optional[datetime] = None) -> Dict:
        """
        Return daily factors based on the provided date.
        If no date is provided,
        the implementation should default to the current date.
        """
        pass

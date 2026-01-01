from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

class Connector(ABC):
    @abstractmethod
    def parse(self) -> Tuple[List[Dict], List[Dict]]:
        pass

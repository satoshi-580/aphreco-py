from collections import OrderedDict, deque
from typing import Dict, List, Optional, Union

from .base import BaseComponent


class Model(BaseComponent):
    def __init__(
        self,
        name: str,
        components: Optional[Union["BaseComponent", List["BaseComponent"]]] = None,
    ):
        self._name = name
        self.components: Dict[str, "BaseComponent"] = OrderedDict()

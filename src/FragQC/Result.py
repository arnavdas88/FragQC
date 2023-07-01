from typing import Any, Mapping
from dataclasses import dataclass, field

@dataclass
class Result:
    min_cost: float
    partition: Mapping[str, int] = field()

    time: float = 0.0
    raw_results: Any = field(default=None)




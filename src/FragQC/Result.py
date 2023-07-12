from typing import Any, Mapping, List
from dataclasses import dataclass, field

@dataclass
class Result:
    min_cost: float
    partition: Mapping[str, int] = field()

    time: float = 0.0
    raw_results: Any = field(default=None)

    subcircuits: List = field(init=False, repr=False, default_factory=list)

    base_mapping: Any = field(init=False, repr=False, default=None)
    history: List = field(init=False, repr=False, default_factory=list)

    def buckets(self, ):
        bucket = {}
        for index, part in enumerate(self.partition):
            if part not in bucket:
                bucket[part] = []
            if self.base_mapping:
                bucket[part].append(self.base_mapping[index])
            else:
                bucket[part].append(index)
        return bucket

    def subcircuit_partition(self, ):
        return list(zip(self.subcircuits, list(self.buckets().values())))



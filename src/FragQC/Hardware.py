from abc import ABC
from typing import Any

class GateValue(ABC):
    id: float

    u1: float
    u2: float
    u3: float

    cx: float

    __GATE_MAPPING__ = {
        "h": "u2",
        "rx": "u2",
        "ry": "u2",
        "rz": "u2",
        "cy": "cx",
        "cz": "cx",
    }

    def __init__(self) -> None:
        super().__init__()

    def __getattribute__(self, __name: str) -> Any:
        if __name == "__GATE_MAPPING__":
            return super().__getattribute__(__name)

        if __name in self.__GATE_MAPPING__:
            __name = self.__GATE_MAPPING__[__name]

        return super().__getattribute__(__name)

    def get(self, name: str) -> Any:
        return self.__getattribute__(name)

class GateError(GateValue):
    id: float = 0.0024623157380400853

    u1: float = 0.0
    u2: float = 0.0024623157380400853
    u3: float = 0.004924631476080171

    cx: float = 0.03130722830688227

class GateLatency(GateValue):
    SINGLE_GATE_CONST_LATENCY : float  = 0.0355
    CX_GATE_CONST_LATENCY     : float  = 0.46

    __GATE_MAPPING__ = {
        'cx': "CX_GATE_CONST_LATENCY",
        'cy': "CX_GATE_CONST_LATENCY",
        'cz': "CX_GATE_CONST_LATENCY",
        'h' : "SINGLE_GATE_CONST_LATENCY",
        'id': "SINGLE_GATE_CONST_LATENCY",
        'rx': "SINGLE_GATE_CONST_LATENCY",
        'ry': "SINGLE_GATE_CONST_LATENCY",
        'rz': "SINGLE_GATE_CONST_LATENCY",
        'u1': "SINGLE_GATE_CONST_LATENCY",
        'u2': "SINGLE_GATE_CONST_LATENCY",
        'u3': "SINGLE_GATE_CONST_LATENCY"
    }


class Hardware:
    def __init__(self, error_model: GateError, latency_model: GateLatency, coherence_time: float, relaxation_time: float) -> None:
        self.error_model     : float = error_model
        self.latency_model   : float = latency_model
        self.coherence_time  : float = coherence_time
        self.relaxation_time : float = relaxation_time


DummyHardware = Hardware(
        error_model = GateError(),
        latency_model = GateLatency(),
        coherence_time = 122.22,
        relaxation_time = 187.75
    )



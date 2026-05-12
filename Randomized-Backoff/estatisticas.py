from dataclasses import dataclass, field


@dataclass
class EstatisticasFilosofo:
    tempo_tranquilo: float = 0.0
    tempo_com_sede: float = 0.0
    tempo_bebendo: float = 0.0
    vezes_bebeu: int = 0
    esperas: list[float] = field(default_factory=list)
    tentativas_falhas: int = 0
import random
import threading
import time

from estatisticas import EstatisticasFilosofo


class Filosofo(threading.Thread):
    def __init__(
        self,
        filosofo_id,
        bar,
        bebidas_necessarias,
        backoff_min=0.05,
        backoff_max=0.50,
        mostrar_log=True,
    ):
        super().__init__()

        self.filosofo_id = filosofo_id
        self.bar = bar
        self.bebidas_necessarias = bebidas_necessarias
        self.backoff_min = backoff_min
        self.backoff_max = backoff_max
        self.mostrar_log = mostrar_log

        self.estado = "tranquilo"
        self.estatisticas = EstatisticasFilosofo()

        self.garrafas_adjacentes = self.bar.garrafas_adjacentes(filosofo_id)
        self.grau = len(self.garrafas_adjacentes)

        if self.grau < 2:
            raise ValueError(
                f"Filósofo {filosofo_id + 1} possui grau {self.grau}. "
                "Ele precisa ter pelo menos 2 garrafas adjacentes."
            )

    def log(self, mensagem):
        if self.mostrar_log:
            self.bar.log(mensagem)

    def escolher_garrafas(self):
        quantidade = random.randint(2, self.grau)
        return random.sample(self.garrafas_adjacentes, quantidade)

    def tentar_pegar_garrafas(self, garrafas_necessarias):
        garrafas_obtidas = []

        ordem_tentativa = garrafas_necessarias[:]
        random.shuffle(ordem_tentativa)

        for garrafa in ordem_tentativa:
            conseguiu = self.bar.garrafas[garrafa].acquire(blocking=False)

            if conseguiu:
                garrafas_obtidas.append(garrafa)
            else:
                for g in garrafas_obtidas:
                    self.bar.garrafas[g].release()

                return False, []

        return True, garrafas_obtidas

    def soltar_garrafas(self, garrafas):
        for garrafa in garrafas:
            self.bar.garrafas[garrafa].release()

    def esperar_backoff(self, numero_falhas):
        limite = min(
            self.backoff_max,
            self.backoff_min * (2 ** numero_falhas)
        )

        tempo = random.uniform(self.backoff_min, limite)
        time.sleep(tempo)

    def run(self):
        while self.estatisticas.vezes_bebeu < self.bebidas_necessarias:
            self.estado = "tranquilo"

            tempo_tranquilo = random.uniform(0, self.grau)

            self.log(
                f"Filósofo {self.filosofo_id + 1} está tranquilo "
                f"por {tempo_tranquilo:.2f}s."
            )

            inicio = time.perf_counter()
            time.sleep(tempo_tranquilo)
            fim = time.perf_counter()

            self.estatisticas.tempo_tranquilo += fim - inicio

            self.estado = "com sede"

            garrafas_necessarias = self.escolher_garrafas()

            self.log(
                f"Filósofo {self.filosofo_id + 1} ficou com sede e precisa "
                f"das garrafas {[(a + 1, b + 1) for a, b in garrafas_necessarias]}."
            )

            inicio_sede = time.perf_counter()
            falhas_seguidas = 0

            while True:
                conseguiu, garrafas_obtidas = self.tentar_pegar_garrafas(
                    garrafas_necessarias
                )

                if conseguiu:
                    break

                self.estatisticas.tentativas_falhas += 1
                falhas_seguidas += 1

                self.log(
                    f"Filósofo {self.filosofo_id + 1} não conseguiu todas as garrafas. "
                    "Soltou as obtidas e fará backoff."
                )

                self.esperar_backoff(falhas_seguidas)

            fim_sede = time.perf_counter()
            tempo_sede = fim_sede - inicio_sede

            self.estatisticas.tempo_com_sede += tempo_sede
            self.estatisticas.esperas.append(tempo_sede)

            self.estado = "bebendo"

            self.log(
                f"Filósofo {self.filosofo_id + 1} está bebendo "
                f"com as garrafas {[(a + 1, b + 1) for a, b in garrafas_obtidas]}."
            )

            inicio_bebendo = time.perf_counter()
            time.sleep(1.0)
            fim_bebendo = time.perf_counter()

            self.estatisticas.tempo_bebendo += fim_bebendo - inicio_bebendo
            self.estatisticas.vezes_bebeu += 1

            self.soltar_garrafas(garrafas_obtidas)

            self.log(
                f"Filósofo {self.filosofo_id + 1} terminou de beber "
                f"({self.estatisticas.vezes_bebeu}/{self.bebidas_necessarias})."
            )
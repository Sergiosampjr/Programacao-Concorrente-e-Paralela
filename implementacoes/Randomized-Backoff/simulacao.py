import time

from matriz import ler_matriz_adjacencia
from bar import Bar
from filosofo import Filosofo
from resultados import montar_linhas_resultado, salvar_resultados


def executar_simulacao(
    caminho_matriz,
    bebidas_por_filosofo,
    mostrar_log=True,
    solucao="Randomized Backoff",
    caso="caso_desconhecido",
    execucao=1,
    caminho_saida=None,
):
    matriz = ler_matriz_adjacencia(caminho_matriz)
    bar = Bar(matriz)

    filosofos = [
        Filosofo(
            filosofo_id=i,
            bar=bar,
            bebidas_necessarias=bebidas_por_filosofo,
            mostrar_log=mostrar_log,
        )
        for i in range(bar.n)
    ]

    inicio_total = time.perf_counter()

    for filosofo in filosofos:
        filosofo.start()

    for filosofo in filosofos:
        filosofo.join()

    fim_total = time.perf_counter()
    tempo_total = fim_total - inicio_total

    if mostrar_log:
        imprimir_resultado(filosofos, tempo_total)

    linhas = montar_linhas_resultado(
        filosofos=filosofos,
        tempo_total=tempo_total,
        solucao=solucao,
        caso=caso,
        execucao=execucao,
    )

    if caminho_saida is not None:
        salvar_resultados(caminho_saida, linhas)

    return linhas


def imprimir_resultado(filosofos, tempo_total):
    print("\n==============================")
    print("RESULTADO FINAL")
    print("==============================")
    print(f"Tempo total da execução: {tempo_total:.2f}s\n")

    for filosofo in filosofos:
        estatisticas = filosofo.estatisticas

        if estatisticas.esperas:
            espera_media = sum(estatisticas.esperas) / len(estatisticas.esperas)
        else:
            espera_media = 0.0

        print(f"Filósofo {filosofo.filosofo_id + 1}")
        print(f"  Grau do vértice: {filosofo.grau}")
        print(f"  Bebeu: {estatisticas.vezes_bebeu} vezes")
        print(f"  Tempo tranquilo: {estatisticas.tempo_tranquilo:.2f}s")
        print(f"  Tempo com sede: {estatisticas.tempo_com_sede:.2f}s")
        print(f"  Tempo bebendo: {estatisticas.tempo_bebendo:.2f}s")
        print(f"  Espera média com sede: {espera_media:.2f}s")
        print(f"  Tentativas falhas: {estatisticas.tentativas_falhas}")
        print()
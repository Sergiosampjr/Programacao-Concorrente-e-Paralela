import csv
import os
from datetime import datetime


COLUNAS_RESULTADO = [
    "timestamp",
    "solucao",
    "caso",
    "execucao",
    "filosofo",
    "grau",
    "bebeu",
    "tempo_total_execucao",
    "tempo_tranquilo",
    "tempo_com_sede",
    "tempo_bebendo",
    "espera_media_sede",
    "tentativas_falhas",
]


def salvar_resultados(caminho_saida, linhas):
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)

    arquivo_existe = os.path.exists(caminho_saida)

    with open(caminho_saida, "a", newline="", encoding="utf-8") as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=COLUNAS_RESULTADO,
            delimiter=";"
        )

        if not arquivo_existe:
            writer.writeheader()

        for linha in linhas:
            writer.writerow(linha)


def montar_linhas_resultado(
    filosofos,
    tempo_total,
    solucao,
    caso,
    execucao
):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linhas = []

    for filosofo in filosofos:
        estatisticas = filosofo.estatisticas

        if estatisticas.esperas:
            espera_media = sum(estatisticas.esperas) / len(estatisticas.esperas)
        else:
            espera_media = 0.0

        linhas.append({
            "timestamp": timestamp,
            "solucao": solucao,
            "caso": caso,
            "execucao": execucao,
            "filosofo": filosofo.filosofo_id + 1,
            "grau": filosofo.grau,
            "bebeu": estatisticas.vezes_bebeu,
            "tempo_total_execucao": tempo_total,
            "tempo_tranquilo": estatisticas.tempo_tranquilo,
            "tempo_com_sede": estatisticas.tempo_com_sede,
            "tempo_bebendo": estatisticas.tempo_bebendo,
            "espera_media_sede": espera_media,
            "tentativas_falhas": estatisticas.tentativas_falhas,
        })

    return linhas
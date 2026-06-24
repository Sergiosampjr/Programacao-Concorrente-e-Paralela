import argparse
from simulacao import executar_simulacao


def main():
    parser = argparse.ArgumentParser(
        description="Problema do Bar dos Filósofos com Randomized Backoff."
    )

    parser.add_argument(
        "arquivo",
        nargs="?",
        default="casos/caso1.txt",
        help="Arquivo .txt contendo a matriz de adjacência.",
    )

    parser.add_argument(
        "--case",
        default="caso1",
        help="Nome do caso executado. Exemplo: caso1, caso2 ou caso3.",
    )

    parser.add_argument(
        "--drinks",
        type=int,
        default=6,
        help="Quantidade de vezes que cada filósofo deve beber.",
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Quantidade de execuções independentes.",
    )

    parser.add_argument(
        "--output",
        default="resultados/resultados_randomized_backoff.txt",
        help="Arquivo onde os resultados serão salvos.",
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Desativa os logs durante a simulação.",
    )

    args = parser.parse_args()

    for execucao in range(1, args.runs + 1):
        print(f"\n======= EXECUÇÃO {execucao}/{args.runs} =======")

        executar_simulacao(
            caminho_matriz=args.arquivo,
            bebidas_por_filosofo=args.drinks,
            mostrar_log=not args.quiet,
            solucao="Randomized Backoff",
            caso=args.case,
            execucao=execucao,
            caminho_saida=args.output,
        )


if __name__ == "__main__":
    main()
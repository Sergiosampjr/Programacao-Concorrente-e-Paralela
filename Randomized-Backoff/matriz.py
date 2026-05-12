def ler_matriz_adjacencia(caminho):
    matriz = []

    with open(caminho, "r", encoding="utf-8") as arquivo:
        for linha in arquivo:
            linha = linha.strip()

            if not linha:
                continue

            linha = linha.replace(",", " ")
            partes = linha.split()

            if len(partes) == 1 and all(c in "01" for c in partes[0]):
                valores = [int(c) for c in partes[0]]
            else:
                valores = [int(x) for x in partes]

            matriz.append(valores)

    if not matriz:
        raise ValueError(
            f"O arquivo '{caminho}' está vazio. "
            "Preencha com a matriz de adjacência."
        )

    n = len(matriz)

    if any(len(linha) != n for linha in matriz):
        raise ValueError("A matriz precisa ser quadrada.")

    for i in range(n):
        if matriz[i][i] != 0:
            raise ValueError("A diagonal principal deve ser zero.")

        for j in range(n):
            if matriz[i][j] != matriz[j][i]:
                raise ValueError("A matriz deve ser simétrica.")

    return matriz
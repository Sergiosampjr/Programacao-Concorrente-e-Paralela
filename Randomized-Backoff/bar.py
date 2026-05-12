import threading


class Bar:
    def __init__(self, matriz):
        self.matriz = matriz
        self.n = len(matriz)
        self.garrafas = {}
        self.print_lock = threading.Lock()

        for i in range(self.n):
            for j in range(i + 1, self.n):
                if matriz[i][j] == 1:
                    self.garrafas[(i, j)] = threading.Lock()

    def garrafas_adjacentes(self, filosofo_id):
        adjacentes = []

        for j in range(self.n):
            if self.matriz[filosofo_id][j] == 1:
                aresta = tuple(sorted((filosofo_id, j)))
                adjacentes.append(aresta)

        return adjacentes

    def log(self, mensagem):
        with self.print_lock:
            print(mensagem, flush=True)
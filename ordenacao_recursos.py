"""
=============================================================
  Problema do Bar dos Filósofos — 2026.1
  Solução: Ordenação de Recursos (Resource Ordering)
=============================================================
 
Como funciona:
  - Cada aresta (garrafa) recebe um ID único e global.
  - Todo filósofo adquire as garrafas SEMPRE em ordem
    crescente de ID, quebrando a espera circular e
    eliminando deadlock sem precisar de árbitro central.
 
Uso:
  python bar_filosofos.py <arquivo_grafo.txt> [n_bebidas]
 
Exemplos:
  python bar_filosofos.py caso1.txt 6
  python bar_filosofos.py caso2.txt 6
  python bar_filosofos.py caso3.txt 3
 
Arquivos de grafo incluídos:
  caso1.txt  — Jantar dos Filósofos clássico (5 nós)
  caso2.txt  — Bar dos Filósofos, 6 nós, baixa conectividade
  caso3.txt  — Bar dos Filósofos, 12 nós, alta conectividade
=============================================================
"""
 
import threading
import time
import random
import sys
import os
from collections import defaultdict
from datetime import datetime
 
 
# =============================================================
# SISTEMA DE LOG (terminal + arquivo simultaneamente)
# =============================================================
 
class Logger:
    """
    Escreve cada mensagem no terminal E em um arquivo .txt.
    Thread-safe: usa lock interno para evitar linhas misturadas.
    """
    def __init__(self, caminho_arquivo):
        self._lock = threading.Lock()
        self._arquivo = open(caminho_arquivo, "w", encoding="utf-8")
 
    def log(self, msg):
        with self._lock:
            print(msg)
            self._arquivo.write(msg + "\n")
            self._arquivo.flush()
 
    def fechar(self):
        self._arquivo.close()
 
 
# Instância global — será inicializada no main()
logger: "Logger | None" = None
 
 
def log(msg):
    """Atalho global para logger.log()."""
    if logger:
        logger.log(msg)
    else:
        print(msg)
 
 
# =============================================================
# MATRIZES DE ADJACÊNCIA (embutidas para referência)
# =============================================================
 
GRAFOS_PADRAO = {
    "caso1.txt": (
        "Jantar dos Filósofos Clássico (5 nós)",
        "0,1,0,0,1\n1,0,1,0,0\n0,1,0,1,0\n0,0,1,0,1\n1,0,0,1,0"
    ),
    "caso2.txt": (
        "Bar dos Filósofos — 6 nós, baixa conectividade",
        "0,1,0,0,0,1\n1,0,1,0,0,0\n0,1,0,1,0,1\n0,0,1,0,1,1\n0,0,0,1,0,1\n1,0,1,1,1,0"
    ),
    "caso3.txt": (
        "Bar dos Filósofos — 12 nós, alta conectividade",
        (
            "0,1,1,0,1,0,0,0,0,0,0,0\n"
            "1,0,1,1,0,0,0,0,0,0,0,0\n"
            "1,1,0,0,0,0,0,0,0,0,0,0\n"
            "0,1,0,0,1,1,1,0,0,0,0,0\n"
            "1,0,0,1,0,0,1,0,0,1,0,0\n"
            "0,0,0,1,0,0,1,1,0,0,0,0\n"
            "0,0,0,1,1,1,0,1,0,1,0,0\n"
            "0,0,0,0,0,1,1,0,1,1,0,0\n"
            "0,0,0,0,0,0,0,1,0,1,0,1\n"
            "0,0,0,0,1,0,1,1,1,0,1,1\n"
            "0,0,0,0,0,0,0,0,0,1,0,1\n"
            "0,0,0,0,0,0,0,0,1,1,1,0"
        )
    ),
}
 
 
# =============================================================
# LEITURA DO GRAFO
# =============================================================
 
def ler_grafo(caminho):
    """
    Lê matriz de adjacência de um .txt.
    Retorna:
      n_nos       — número de filósofos/vértices
      adjacencias — dict: vértice -> lista de vizinhos
      locks       — dict: (i,j) com i<j -> threading.Lock()
      ids_arestas — dict: (i,j) com i<j -> int (para ordenação)
    """
    matriz = []
 
    # Tenta ler o arquivo; se não existir, usa o padrão embutido
    import os
    if not os.path.exists(caminho):
        nome = os.path.basename(caminho)
        if nome in GRAFOS_PADRAO:
            log(f"[Aviso] '{caminho}' não encontrado. Usando grafo padrão embutido.")
            conteudo = GRAFOS_PADRAO[nome][1]
            linhas = conteudo.strip().split("\n")
        else:
            log(f"[Erro] Arquivo '{caminho}' não encontrado.")
            sys.exit(1)
    else:
        with open(caminho) as f:
            linhas = f.readlines()
 
    for linha in linhas:
        linha = linha.strip()
        if not linha:
            continue
        row = [int(x.strip()) for x in linha.split(",")]
        matriz.append(row)
 
    n = len(matriz)
    adjacencias = defaultdict(list)
    locks       = {}
    ids_arestas = {}
    edge_id     = 0
 
    for i in range(n):
        for j in range(i + 1, n):
            if matriz[i][j] == 1:
                chave = (i, j)
                locks[chave]       = threading.Lock()
                ids_arestas[chave] = edge_id
                edge_id += 1
                adjacencias[i].append(j)
                adjacencias[j].append(i)
 
    return n, adjacencias, locks, ids_arestas
 
 
# =============================================================
# CLASSE FILÓSOFO
# =============================================================
 
class Filosofo(threading.Thread):
    """
    Representa um filósofo como thread independente.
 
    Ciclo de estados (repetido n_bebidas vezes):
      TRANQUILO -> COM SEDE -> BEBENDO -> TRANQUILO -> ...
 
    Ordenação de recursos:
      As garrafas (locks) são sempre adquiridas em ordem
      crescente de ID, eliminando a possibilidade de deadlock.
    """
 
    def __init__(self, id_, adjacencias, locks, ids_arestas, n_bebidas):
        super().__init__(daemon=True, name=f"Filosofo-{id_}")
        self.id          = id_
        self.adjacencias = adjacencias
        self.locks       = locks
        self.ids_arestas = ids_arestas
        self.n_bebidas   = n_bebidas
 
        # Acumuladores de tempo por estado
        self.tempo_tranquilo = 0.0
        self.tempo_com_sede  = 0.0
        self.tempo_bebendo   = 0.0
 
    # ----------------------------------------------------------
    # Utilitários internos
    # ----------------------------------------------------------
 
    def _chave(self, vizinho):
        """Chave canônica da aresta entre self.id e vizinho."""
        return (min(self.id, vizinho), max(self.id, vizinho))
 
    def _sortear_garrafas(self):
        """
        Sorteia aleatoriamente quantas e quais garrafas o filósofo
        vai querer nesta rodada.
 
        Regra do PDF: mínimo 2, máximo n (todas as adjacentes).
        Caso o nó tenha menos de 2 vizinhos, pega todos.
        """
        vizinhos = self.adjacencias[self.id]
        n = len(vizinhos)
        if n < 2:
            return vizinhos[:]
        k = random.randint(2, n)
        return random.sample(vizinhos, k)
 
    def _ordenar_por_id(self, vizinhos):
        """
        Retorna as chaves de aresta ordenadas pelo ID global.
        Esta ordenação é o núcleo da solução: garante que
        dois filósofos que disputam as mesmas garrafas sempre
        as adquirem na mesma sequência, evitando ciclo de espera.
        """
        chaves = [self._chave(v) for v in vizinhos]
        chaves.sort(key=lambda c: self.ids_arestas[c])
        return chaves
 
    # ----------------------------------------------------------
    # Estados
    # ----------------------------------------------------------
 
    def _estado_tranquilo(self):
        n_viz = len(self.adjacencias[self.id])
        duracao = random.uniform(0, n_viz)
        self._log(f"TRANQUILO por {duracao:.1f}s")
        t0 = time.time()
        time.sleep(duracao)
        self.tempo_tranquilo += time.time() - t0
 
    def _estado_com_sede_e_bebendo(self):
        vizinhos  = self._sortear_garrafas()
        ordenadas = self._ordenar_por_id(vizinhos)
        nomes     = [str(c) for c in ordenadas]
 
        self._log(f"COM SEDE — quer {len(ordenadas)} garrafa(s): {nomes}")
        t0 = time.time()
 
        # Adquire locks em ordem crescente (sem deadlock)
        for chave in ordenadas:
            self.locks[chave].acquire()
 
        self.tempo_com_sede += time.time() - t0
 
        # --- BEBENDO ---
        self._log(f"BEBENDO  — segurando: {nomes}")
        t1 = time.time()
        time.sleep(1)                        # tempo fixo de 1 segundo
        self.tempo_bebendo += time.time() - t1
 
        # Libera todas as garrafas
        for chave in ordenadas:
            self.locks[chave].release()
 
        self._log("soltou as garrafas → voltando a TRANQUILO")
 
    # ----------------------------------------------------------
    # Loop principal
    # ----------------------------------------------------------
 
    def run(self):
        for rodada in range(1, self.n_bebidas + 1):
            self._log(f"=== Rodada {rodada}/{self.n_bebidas} ===")
            self._estado_tranquilo()
            self._estado_com_sede_e_bebendo()
        self._log("terminou todas as rodadas.")
 
    def _log(self, msg):
        log(f"[Filósofo {self.id:>2}] {msg}")
 
 
# =============================================================
# RELATÓRIO FINAL
# =============================================================
 
def exibir_relatorio(filosofos, tempo_total, descricao_grafo):
    SEP = "=" * 68
    sep = "-" * 68
 
    log(f"\n{SEP}")
    log(f"  RELATÓRIO FINAL — Ordenação de Recursos")
    log(f"  Grafo: {descricao_grafo}")
    log(SEP)
 
    # Cabeçalho
    log(f"  {'Filósofo':<10} {'Vizinhos':>9} {'Tranquilo(s)':>13} "
        f"{'Com Sede(s)':>12} {'Bebendo(s)':>11}")
    log(sep)
 
    total_espera = 0.0
    for f in filosofos:
        n_viz = len(f.adjacencias[f.id])
        log(f"  Fil. {f.id:<6}  {n_viz:>7}     "
            f"{f.tempo_tranquilo:>10.2f}     "
            f"{f.tempo_com_sede:>9.2f}    "
            f"{f.tempo_bebendo:>9.2f}")
        total_espera += f.tempo_com_sede
 
    media_espera = total_espera / len(filosofos)
 
    log(sep)
    log(f"  Tempo total de execução : {tempo_total:.2f}s")
    log(f"  Espera média (com sede) : {media_espera:.2f}s")
    log("")
    log("  Avaliação de starvation:")
    log("  (filósofos com mesmo nº de vizinhos devem ter espera similar)")
    log(sep)
 
    # Agrupa por número de vizinhos para facilitar avaliação de starvation
    grupos = defaultdict(list)
    for f in filosofos:
        grupos[len(f.adjacencias[f.id])].append(f)
 
    for grau, grupo in sorted(grupos.items()):
        esperas = [f.tempo_com_sede for f in grupo]
        media   = sum(esperas) / len(esperas)
        ids     = [f.id for f in grupo]
        log(f"  Grau {grau} — Filósofos {ids} — espera média: {media:.2f}s")
 
    log(SEP)
 
 
# =============================================================
# MAIN
# =============================================================
 
def main():
    global logger

    if len(sys.argv) < 2:
        print(__doc__)
        print("Uso: python bar_filosofos_ordenacao.py <arquivo_grafo.txt> [n_bebidas]")
        sys.exit(1)

    caminho   = sys.argv[1]
    n_bebidas = int(sys.argv[2]) if len(sys.argv) >= 3 else 6

    # Cria a pasta resultados caso não exista
    pasta_resultados = "resultados"
    os.makedirs(pasta_resultados, exist_ok=True)

    # Nome do arquivo de saída
    nome_base = os.path.splitext(os.path.basename(caminho))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    arq_saida = os.path.join(
        pasta_resultados,
        f"resultado_{nome_base}_{timestamp}.txt"
    )

    # Inicializa o logger (terminal + arquivo)
    logger = Logger(arq_saida)

    # Descrição amigável do grafo
    nome      = os.path.basename(caminho)
    descricao = GRAFOS_PADRAO.get(nome, ("Grafo personalizado",))[0]

    log(f"\n{'='*68}")
    log(f"  Bar dos Filósofos — Ordenação de Recursos")
    log(f"  Grafo  : {caminho} ({descricao})")
    log(f"  Bebidas: {n_bebidas} por filósofo")
    log(f"  Log    : {arq_saida}")
    log(f"{'='*68}\n")
 
    n_nos, adjacencias, locks, ids_arestas = ler_grafo(caminho)
    log(f"  {n_nos} filósofos | {len(locks)} garrafas (arestas)\n")
 
    filosofos = [
        Filosofo(i, adjacencias, locks, ids_arestas, n_bebidas)
        for i in range(n_nos)
    ]
 
    t_inicio = time.time()
    for f in filosofos:
        f.start()
    for f in filosofos:
        f.join()
    tempo_total = time.time() - t_inicio
 
    exibir_relatorio(filosofos, tempo_total, descricao)
 
    logger.fechar()
    print(f"\n  Resultados salvos em: {arq_saida}")
 
 
if __name__ == "__main__":
    main()
 
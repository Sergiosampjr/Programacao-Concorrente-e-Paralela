import threading
import time
import random
import sys

# Constantes de Estado
TRANQUILO = 'Tranquilo'
COM_SEDE = 'Com Sede'
BEBENDO = 'Bebendo'

# Controle global para evitar que filósofos "fujam" com as garrafas ao terminar
filosofos_concluidos = []
lock_concluidos = threading.Lock()

class Garrafa:
    def __init__(self, id_u, id_v):
        self.id_u = id_u
        self.id_v = id_v
        # Prevenção de Deadlock inicial: DAG apontando para o vértice de maior ID
        self.dono = max(id_u, id_v)
        self.estado = 'vazia' 
        self.fila_pedidos = []
        self.lock = threading.Lock()

    def solicitar(self, solicitante_id):
        with self.lock:
            if self.dono != solicitante_id and solicitante_id not in self.fila_pedidos:
                self.fila_pedidos.append(solicitante_id)

class Filosofo(threading.Thread):
    def __init__(self, id, num_ciclos, garrafas_adjacentes, total_filosofos):
        super().__init__()
        self.id = id
        self.num_ciclos = num_ciclos
        self.garrafas_adjacentes = garrafas_adjacentes
        self.total_filosofos = total_filosofos
        self.estado = TRANQUILO
        
        # Métricas
        self.tempo_tranquilo_total = 0
        self.tempo_sede_total = 0
        self.tempo_bebendo_total = 0

    def run(self):
        for ciclo in range(self.num_ciclos):
            # --- ESTADO: TRANQUILO ---
            self.estado = TRANQUILO
            num_arestas = len(self.garrafas_adjacentes)
            tempo_tranquilo = random.uniform(0, num_arestas) 
            
            print(f"🕒 Filósofo {self.id} está TRANQUILO (Ciclo {ciclo+1}/{self.num_ciclos})")
            
            inicio_tranquilo = time.time()
            while (time.time() - inicio_tranquilo) < tempo_tranquilo:
                time.sleep(0.01) 
                for garrafa in self.garrafas_adjacentes:
                    self.processar_mensagens(garrafa)
                    
            self.tempo_tranquilo_total += tempo_tranquilo

            # --- ESTADO: COM SEDE ---
            self.estado = COM_SEDE
            inicio_sede = time.time()
            
            qtd_requerida = random.randint(min(2, num_arestas), num_arestas) if num_arestas >= 2 else 1
            garrafas_escolhidas = random.sample(self.garrafas_adjacentes, qtd_requerida)

            print(f"🔥 Filósofo {self.id} está COM SEDE e pediu {qtd_requerida} garrafa(s).")

            while not all(g.dono == self.id for g in garrafas_escolhidas):
                for garrafa in garrafas_escolhidas:
                    if garrafa.dono != self.id:
                        garrafa.solicitar(self.id)
                        
                time.sleep(0.01)
                for garrafa in self.garrafas_adjacentes:
                    self.processar_mensagens(garrafa)

            fim_sede = time.time()
            self.tempo_sede_total += (fim_sede - inicio_sede)

            # --- ESTADO: BEBENDO ---
            self.estado = BEBENDO
            tempo_bebendo = 1.0 
            print(f"🍺 Filósofo {self.id} pegou o que precisava e está BEBENDO! (Ciclo {ciclo+1})")
            time.sleep(tempo_bebendo)
            self.tempo_bebendo_total += tempo_bebendo

            # Transição de volta para tranquilo ANTES de soltar as garrafas
            self.estado = TRANQUILO

            for garrafa in garrafas_escolhidas:
                with garrafa.lock:
                    if garrafa.dono == self.id:
                        garrafa.estado = 'vazia'
                    
            for garrafa in self.garrafas_adjacentes:
                self.processar_mensagens(garrafa)

        # Ao terminar os ciclos, o filósofo não pode morrer, senão leva as garrafas junto!
        with lock_concluidos:
            filosofos_concluidos.append(self.id)
            
        print(f"✅ Filósofo {self.id} concluiu! Atuando como garçom para os atrasados...")
        
        # Continua vivo processando pedidos até que o último filósofo termine
        while len(filosofos_concluidos) < self.total_filosofos:
            time.sleep(0.05)
            for garrafa in self.garrafas_adjacentes:
                self.processar_mensagens(garrafa)

    def processar_mensagens(self, garrafa):
        with garrafa.lock:
            if garrafa.dono == self.id and len(garrafa.fila_pedidos) > 0:
                # Regra: Se o filosofo não estiver bebendo e a garrafa estiver vazia, enche e entrega
                if self.estado != BEBENDO and garrafa.estado == 'vazia':
                    solicitante = garrafa.fila_pedidos.pop(0)
                    garrafa.estado = 'cheia'
                    garrafa.dono = solicitante

def ler_matriz_adjacencia(caminho_arquivo):
    matriz = []
    try:
        with open(caminho_arquivo, 'r') as f:
            for linha in f:
                linha_limpa = linha.replace(',', '').replace(' ', '').strip()
                if linha_limpa:
                    linha_inteiros = [int(char) for char in linha_limpa]
                    matriz.append(linha_inteiros)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{caminho_arquivo}' não encontrado.")
        sys.exit(1)
    return matriz

def main():
    if len(sys.argv) < 2:
        arquivo = "caso1.txt" 
    else:
        arquivo = sys.argv[1] 

    matriz = ler_matriz_adjacencia(arquivo)
    num_filosofos = len(matriz)
    
    num_ciclos = 3 if num_filosofos > 6 else 6

    print(f"\n🚀 Iniciando simulação com {num_filosofos} filósofos executando {num_ciclos} ciclos...")
    print("-" * 50)
    inicio_simulacao = time.time()

    garrafas_map = {}
    for i in range(num_filosofos):
        for j in range(i + 1, num_filosofos):
            if matriz[i][j] == 1:
                garrafas_map[(i, j)] = Garrafa(i, j)

    filosofos = []
    for i in range(num_filosofos):
        adjacentes = []
        for j in range(num_filosofos):
            if matriz[i][j] == 1:
                chave = (min(i, j), max(i, j))
                adjacentes.append(garrafas_map[chave])
        filosofos.append(Filosofo(i, num_ciclos, adjacentes, num_filosofos))

    for f in filosofos:
        f.start()

    for f in filosofos:
        f.join()

    fim_simulacao = time.time()

    # --- GERAÇÃO DO RELATÓRIO ---
    relatorio = []
    relatorio.append("\n" + "="*50)
    relatorio.append("🏆 RESULTADOS DA SIMULAÇÃO (Sem Ocorrência de Deadlock)")
    relatorio.append("="*50)
    relatorio.append(f"Tempo Total de Execução: {fim_simulacao - inicio_simulacao:.2f} segundos\n")
    
    for f in filosofos:
        num_arestas = len(f.garrafas_adjacentes)
        tempo_medio_espera = f.tempo_sede_total / num_ciclos
        
        relatorio.append(f"Filósofo [{f.id}] (Grau: {num_arestas} arestas):")
        relatorio.append(f"  - Tempo total Tranquilo: {f.tempo_tranquilo_total:.2f}s")
        relatorio.append(f"  - Tempo total Com Sede:  {f.tempo_sede_total:.2f}s")
        relatorio.append(f"  - Tempo total Bebendo:   {f.tempo_bebendo_total:.2f}s")
        relatorio.append(f"  - Espera MÉDIA por ciclo:{tempo_medio_espera:.2f}s")
        relatorio.append("-" * 50)

    texto_final = "\n".join(relatorio)
    
    # Imprime no terminal
    print(texto_final)

    # Salva no arquivo .txt
    # Pega o nome do arquivo de entrada (ex: "caso1.txt") e cria o nome de saída
    nome_base = arquivo.replace('.txt', '')
    arquivo_saida = f"resultado_{nome_base}.txt"
    
    with open(arquivo_saida, 'w', encoding='utf-8') as f_out:
        f_out.write(texto_final)
        
    print(f"\n📄 Resultados salvos com sucesso no arquivo: {arquivo_saida}")

if __name__ == "__main__":
    main()
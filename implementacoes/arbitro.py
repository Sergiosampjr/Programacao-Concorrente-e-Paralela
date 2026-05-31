import threading
import time
import random
import os
import matplotlib.pyplot as plt

class BarDosFilosofos:
    def __init__(self, matriz, num_beber_objetivo):
        self.matriz = matriz
        self.num_filosofos = len(matriz)
        self.num_beber_objetivo = num_beber_objetivo
        # Solução do Árbitro: Um garçom controla quem pode pegar as garrafas
        self.garcom_lock = threading.Lock() 
        self.garrafas = {} 
        self.vizinhos = {i: [] for i in range(self.num_filosofos)}
        
        # As arestas representam as garrafas (recursos compartilhados)
        for i in range(self.num_filosofos):
            for j in range(i + 1, self.num_filosofos):
                if self.matriz[i][j] == 1:
                    garrafa_id = tuple(sorted((i, j)))
                    self.garrafas[garrafa_id] = threading.Lock()
                    self.vizinhos[i].append(garrafa_id)
                    self.vizinhos[j].append(garrafa_id)

    def pedir_permissao(self, garrafas_escolhidas):
        # O filósofo pede permissão ao garçom antes de pegar qualquer garrafa
        while True:
            with self.garcom_lock:
                # Verifica se todas as garrafas necessárias estão disponíveis
                disponivel = all(not self.garrafas[g].locked() for g in garrafas_escolhidas)
                if disponivel:
                    for g in garrafas_escolhidas:
                        self.garrafas[g].acquire()
                    return True
            time.sleep(0.01)

    def liberar_garrafas(self, garrafas_escolhidas):
        with self.garcom_lock:
            for g in garrafas_escolhidas:
                self.garrafas[g].release()

class Filosofo(threading.Thread):
    def __init__(self, id, bar):
        super().__init__()
        self.id = id
        self.bar = bar
        self.num_arestas = len(bar.vizinhos[id])
        self.tempo_tranquilo = 0.0
        self.tempo_sede = 0.0
        self.tempo_bebendo = 0.0

    def run(self):
        for _ in range(self.bar.num_beber_objetivo):
            # Estado: Tranquilo (0 a n segundos)
            t_tranquilo = random.uniform(0, self.num_arestas)
            self.tempo_tranquilo += t_tranquilo
            time.sleep(t_tranquilo)

            # Estado: Com Sede (Sorteia de 2 até n garrafas)
            num_garrafas = random.randint(2, self.num_arestas)
            escolhidas = random.sample(self.bar.vizinhos[self.id], num_garrafas)
            
            inicio_sede = time.time()
            self.bar.pedir_permissao(escolhidas)
            self.tempo_sede += (time.time() - inicio_sede)

            # Estado: Bebendo (1 segundo)
            time.sleep(1)
            self.tempo_bebendo += 1
            self.bar.liberar_garrafas(escolhidas)

def ler_matriz(arquivo):
    matriz = []
    with open(arquivo, 'r', encoding='utf-8') as f:
        for linha in f:
            # Remove vírgulas, espaços e caracteres especiais invisíveis
            linha_limpa = linha.replace(',', ' ').strip()
            if linha_limpa:
                # Converte apenas o que for número, ignorando o que não for dígito
                valores = []
                for x in linha_limpa.split():
                    try:
                        valores.append(int(x))
                    except ValueError:
                        continue
                if valores:
                    matriz.append(valores)
    return matriz

def executar_simulacao(caminho_arquivo, num_beber):
    print(f"\n--- Iniciando Simulação: {os.path.basename(caminho_arquivo)} ---")
    try:
        matriz = ler_matriz(caminho_arquivo)
        
        # Verifica se a matriz foi lida corretamente para evitar divisão por zero
        if not matriz or len(matriz) == 0:
            print("Erro: A matriz está vazia ou o formato do arquivo .txt está incorreto.")
            return

        bar = BarDosFilosofos(matriz, num_beber)
        filosofos = [Filosofo(i, bar) for i in range(bar.num_filosofos)]
        
        inicio = time.time()
        for f in filosofos: f.start()
        for f in filosofos: f.join()
        total_time = time.time() - inicio

        
        
        # Gera o gráfico logo após a sincronização final das threads
        nome_limpo_caso = os.path.basename(caminho_arquivo).replace(".txt", "")
        gerar_grafico_analise(filosofos, nome_limpo_caso) 

        print(f"\n{'ID':<4} | {'Tranquilo':<10} | {'Sede (Espera)':<15} | {'Bebendo':<10}")
        espera_total = 0
        for f in filosofos:
            print(f"{f.id:<4} | {f.tempo_tranquilo:>9.2f}s | {f.tempo_sede:>14.2f}s | {f.tempo_bebendo:>9.2f}s")
            espera_total += f.tempo_sede
        
        print(f"\nTempo Total de Execução: {total_time:.2f}s")
        print(f"Espera Média (Starvation): {espera_total/len(filosofos):.2f}s")
        
    except Exception as e:
        print(f"Erro ao processar: {e}")

def gerar_grafico_analise(filosofos, nome_caso):
    """Generates a stacked bar chart to analyze the states of the philosophers."""
    ids = [f"F{f.id}" for f in filosofos]
    tranquilo = [f.tempo_tranquilo for f in filosofos]
    sede = [f.tempo_sede for f in filosofos]
    bebendo = [f.tempo_bebendo for f in filosofos]

    plt.figure(figsize=(10, 6))

    # Construção das barras empilhadas (Stacked Bar Chart)
    b1 = plt.bar(ids, tranquilo, color='#4f81bd', label='Tranquilo')
    b2 = plt.bar(ids, sede, bottom=tranquilo, color='#c0504d', label='Com Sede (Espera)')
    
    # Calcula a base para a terceira barra somando as duas anteriores
    bottom_bebendo = [t + s for t, s in zip(tranquilo, sede)]
    b3 = plt.bar(ids, bebendo, bottom=bottom_bebendo, color='#9bbb59', label='Bebendo')

    # Configurações estéticas do gráfico
    plt.title(f'Análise de Estados e Tempos - {nome_caso}', fontsize=14, fontweight='bold')
    plt.xlabel('Filósofos (IDs)', fontsize=12)
    plt.ylabel('Tempo Acumulado (segundos)', fontsize=12)
    plt.legend(loc='upper right')
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Ajusta o layout e salva o gráfico como imagem PNG na mesma pasta do script
    plt.tight_layout()
    nome_arquivo_grafico = f"grafico_{nome_caso.lower().replace(' ', '_')}.png"
    plt.savefig(nome_arquivo_grafico, dpi=300)
    plt.close()
    print(f"--> Gráfico salvo com sucesso: {nome_arquivo_grafico}")




if __name__ == "__main__":
    # 1. Descobrir onde o script (arbitro.py) está
    caminho_script = os.path.dirname(os.path.abspath(__file__))
    
    # 2. Subir uma pasta para chegar em "Trabalho - Programação Concorrente e Paralela"
    pasta_pai = os.path.dirname(caminho_script)
    
    # 3. Definir o arquivo alvo (mude para 'caso2.txt' ou 'caso3.txt' conforme o teste)
    target = "caso3.txt"
    caminho_final = os.path.join(pasta_pai, target)
    
    print(f"Buscando arquivo em: {caminho_final}")

    if os.path.exists(caminho_final):
        # Caso 1 e 2: beber 6 vezes. Caso 3: beber 3 vezes 
        vezes = 3 if "caso3" in target else 6
        executar_simulacao(caminho_final, vezes)
    else:
        print(f"ERRO: O arquivo {target} não foi encontrado na pasta pai.")
        print(f"Conteúdo da pasta pai: {os.listdir(pasta_pai)}")

    



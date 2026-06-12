# O Problema do Bar dos Filósofos — Programação Concorrente e Paralela

Este repositório contém a solução e a análise computacional para o **Problema do Bar dos Filósofos**, uma extensão do clássico problema do *Jantar dos Filósofos* (Dijkstra, 1971) proposta por Chandy e Misra (1984) para estruturas de grafos arbitrários e demandas dinâmicas de recursos.

O projeto foi desenvolvido como trabalho prático para a disciplina de Programação Concorrente e Paralela da Universidade Estadual do Ceará (UECE), modelando filósofos como processos (*threads*) e garrafas compartilhadas como arestas com travas de exclusão mútua (*locks*).

---

## 🛠️ Solução Implementada: Chandy-Misra (Tokens Distribuídos)

A arquitetura deste módulo baseia-se na troca de mensagens e posse de recursos (tokens) entre nós vizinhos, descentralizando o controle e eliminando as condições necessárias para a ocorrência de *deadlocks* e *starvation*.

### Mecanismo de Sincronização
* **Exclusão Mútua de Recursos:** Cada aresta da matriz de adjacência (garrafa) possui um trinco exclusivo (`threading.Lock()`). Vizinhos diretos no grafo jamais utilizam a mesma garrafa simultaneamente.
* **Prevenção de Deadlock (Grafo Direcionado Acíclico - DAG):** Para evitar a condição de *espera circular*, as arestas são inicializadas com direções. O vértice de maior ID começa com a posse da garrafa. Dessa forma, é matematicamente impossível formar um ciclo de bloqueio no estado inicial.
* **Prevenção de Starvation (Fila FIFO):** Cada garrafa gerencia uma fila de requisições por ordem de chegada. Quando um filósofo termina de beber, a garrafa transita para o estado "vazia" e é cedida imediatamente ao próximo solicitante da fila.

### Ciclo de Estados e Parâmetros Temporais
* **Tranquilo:** Tempo aleatório variando uniformemente de 0 a n segundos (onde n é o grau do vértice/número de vizinhos).
* **Com Sede:** Sorteio dinâmico de um subconjunto de garrafas desejadas (variando de 2 até n). O processo envia pedidos aos vizinhos e aguarda até possuir todos os recursos escolhidos.
* **Bebendo:** Tempo fixo de exatamente 1 segundo por ciclo de consumo.

---

## 📊 Resultados Experimentais e Análise Gráfica

Abaixo estão consolidados os dados coletados diretamente da execução dos casos de teste obrigatórios, acompanhados de suas respectivas análises de estados.

### Caso 1: Jantar dos Filósofos Clássico (5 nós, 6 ciclos)
*Grafo circular regular simétrico (todos os nós com grau n=2).*

* **Tempo Total de Execução:** 16.77s
* **Espera Média (Starvation):** 4.48s

| ID | Tempo Tranquilo | Tempo Sede (Espera) | Tempo Bebendo |
| :---: | :---: | :---: | :---: |
| **F0** | 5.76s | 4.05s | 6.00s |
| **F1** | 5.83s | 2.89s | 6.00s |
| **F2** | 4.00s | 5.72s | 6.00s |
| **F3** | 7.08s | 3.65s | 6.00s |
| **F4** | 2.69s | 6.13s | 6.00s |

* **Análise:** O tempo fixo e universal de 6.00s na coluna "Tempo Bebendo" comprova matematicamente a ausência de *starvation*, garantindo que todos os processos acessaram sua seção crítica as 6 vezes exigidas. As flutuações no tempo de espera decorrem naturalmente da variação aleatória do tempo "Tranquilo" e da mecânica de propagação de tokens do algoritmo de Chandy-Misra.

### Caso 2: Bar dos Filósofos (6 nós, 6 ciclos)
*Grafo genérico assimétrico com variação na conectividade dos nós (máximo de 4 arestas).*

* **Tempo Total de Execução:** 22.05s
* **Espera Média (Starvation):** 4.03s

| ID | Tempo Tranquilo | Tempo Sede (Espera) | Tempo Bebendo |
| :---: | :---: | :---: | :---: |
| **F0** | 5.67s | 5.11s | 6.00s |
| **F1** | 6.41s | 5.37s | 6.00s |
| **F2** | 5.68s | 4.95s | 6.00s |
| **F3** | 9.00s | 3.54s | 6.00s |
| **F4** | 5.96s | 1.57s | 6.00s |
| **F5** | 12.36s | 3.63s | 6.00s |

* **Análise:** A assimetria topológica do grafo reflete-se claramente no tempo "Tranquilo". O filósofo F5, por possuir maior conectividade (grau n=4), sorteou intervalos maiores de descanso, acumulando 12.36s. Apesar da alta disputa local por recursos gerada pelos nós mais conectados (como F2, F3 e F5), a fila FIFO descentralizada do algoritmo de Chandy-Misra absorveu a carga com sucesso, garantindo que todos os nós bebessem as 6 vezes regulamentares sem sofrer inanição.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
O programa foi desenvolvido em Python puro utilizando as bibliotecas padrão da linguagem para manipulação de *threads* e sincronização. Não é necessária a instalação de pacotes de terceiros.

Para executar no terminal:
```bash
python ChandyMisra.py matriz_do_caso.txt
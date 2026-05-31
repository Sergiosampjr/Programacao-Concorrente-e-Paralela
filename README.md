Projeto - Bar dos filósofos


# O Problema do Bar dos Filósofos — Programação Concorrente e Paralela

Este repositório contém a solução e a análise computacional para o **Problema do Bar dos Filósofos**, uma extensão do clássico problema do *Jantar dos Filósofos* (Dijkstra, 1971) proposta por Chandy e Misra (1984) para estruturas de grafos arbitrários e demandas dinâmicas de recursos.

O projeto foi desenvolvido como trabalho prático para a disciplina de Programação Concorrente e Paralela, modelando filósofos como processos (*threads*) e garrafas compartilhadas como arestas com travas de exclusão mútua (*locks*).

---

## 🛠️ Solução Implementada: O Árbitro (Garçom)

A arquitetura deste módulo baseia-se em um controle centralizado para a alocação de recursos, eliminando as condições necessárias para a ocorrência de *deadlocks* e mitigando o *starvation*.

### Mecanismo de Sincronização
* **Exclusão Mútua de Recursos:** Cada aresta da matriz de adjacência (garrafa) possui um trinco exclusivo (`threading.Lock()`). Vizinhos diretos no grafo jamais utilizam a mesma garrafa simultaneamente.
* **Prevenção de Deadlock (Abordagem "Tudo ou Nada"):** Um lock centralizador (`garcom_lock`) atua como o Árbitro do bar. O filósofo só adquire o subconjunto de garrafas sorteadas se **todas** estiverem disponíveis ao mesmo tempo. Caso contrário, ele libera o Árbitro e aguarda, quebrando a condição de *espera circular*.

### Ciclo de Estados e Parâmetros Temporais
1. **Tranquilo:** Tempo aleatório variando uniformemente de $0$ a $n$ segundos (onde $n$ é o grau do vértice/número de vizinhos).
2. **Com Sede:** Sorteio dinâmico de um subconjunto de garrafas desejadas (variando de 2 até $n$). O processo aguarda a validação do Árbitro.
3. **Bebendo:** Tempo fixo de exatamente 1 segundo por ciclo de consumo.

---

## 📊 Resultados Experimentais e Análise Gráfica

Abaixo estão consolidados os dados coletados diretamente da execução dos três casos de teste obrigatórios, acompanhados de seus respectivos gráficos de análise de estados.

### Caso 1: Jantar dos Filósofos Clássico (5 nós, 6 ciclos)
*Grafo circular regular simétrico (todos os nós com grau $n=2$).*

* **Tempo Total de Execução:** 16.18s
* **Espera Média (Starvation):** 2.96s

| ID | Tempo Tranquilo | Tempo Sede (Espera) | Tempo Bebendo |
| :---: | :---: | :---: | :---: |
| **F0** | 6.32s | 1.46s | 6.00s |
| **F1** | 3.75s | 5.37s | 6.00s |
| **F2** | 7.27s | 2.86s | 6.00s |
| **F3** | 7.03s | 1.55s | 6.00s |
| **F4** | 6.02s | 3.56s | 6.00s |

![Gráfico Caso 1](implementacoes/grafico_caso1.png)
* **Análise:** O equilíbrio visual nas barras vermelhas (Espera) e o tempo fixo em verde (6s) provam a equidade e justiça do Árbitro na distribuição dos recursos em uma topologia simétrica, sem indícios de *starvation*.

### Caso 2: Bar dos Filósofos (6 nós, 6 ciclos)
*Grafo genérico assimétrico com variação na conectividade dos nós.*

* **Tempo Total de Execução:** 22.53s
* **Espera Média (Starvation):** 2.39s

| ID | Tempo Tranquilo | Tempo Sede (Espera) | Tempo Bebendo |
| :---: | :---: | :---: | :---: |
| **F0** | 6.67s | 2.55s | 6.00s |
| **F1** | 5.84s | 1.72s | 6.00s |
| **F2** | 10.81s | 2.79s | 6.00s |
| **F3** | 6.12s | 2.23s | 6.00s |
| **F4** | 4.41s | 2.50s | 6.00s |
| **F5** | 13.94s | 2.59s | 6.00s |

![Gráfico Caso 2](implementacoes/grafico_caso2.png)
* **Análise:** A assimetria do grafo reflete-se na base azul (Tranquilo). O nó $F_4$ possui menor grau ($n=2$), resultando em sorteios menores e requisições mais frequentes. O Árbitro absorveu essa carga extra sem penalizar os demais nós (esperas controladas na faixa vermelha).

### Caso 3: Alta Conectividade (12 nós, 3 ciclos)
*Grafo complexo e denso de larga escala (nós com até grau $n=6$).*

* **Tempo Total de Execução:** 13.26s
* **Espera Média (Starvation):** 1.44s

| ID | Tempo Tranquilo | Tempo Sede (Espera) | Tempo Bebendo |
| :---: | :---: | :---: | :---: |
| **F0** | 3.98s | 1.68s | 3.00s |
| **F1** | 2.41s | 2.08s | 3.00s |
| **F2** | 3.76s | 0.76s | 3.00s |
| **F3** | 4.62s | 0.00s | 3.00s |
| **F4** | 3.82s | 0.71s | 3.00s |
| **F5** | 2.87s | 3.23s | 3.00s |
| **F6** | 6.76s | 0.00s | 3.00s |
| **F7** | 4.01s | 1.09s | 3.00s |
| **F8** | 5.54s | 1.89s | 3.00s |
| **F9** | 4.98s | 3.46s | 3.00s |
| **F10**| 3.15s | 0.29s | 3.00s |
| **F11**| 8.12s | 2.12s | 3.00s |

![Gráfico Caso 3](implementacoes/grafico_caso3.png)
* **Análise:** Revela um alto nível de concorrência paralela. Por possuir uma malha ampla, o Árbitro conseguiu liberar filósofos não adjacentes simultaneamente. Processos como $F_3$ e $F_6$ obtiveram tempo de espera zero ($0.00\text{s}$), otimizando a vazão geral do sistema.

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
Certifique-se de possuir o Python 3 e a biblioteca `matplotlib` instalados no seu ambiente:
```bash
pip install matplotlib
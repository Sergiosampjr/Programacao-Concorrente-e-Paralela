# Problema do Bar dos Filósofos (Drinking Philosophers)
Aluno: Francisco Leonardo Marcos Leitão

## Sobre o Projeto
Este projeto traz uma simulação multithread em Python para o Problema do Bar dos Filósofos, uma generalização do clássico Jantar dos Filósofos. 

Para resolver o controle de acesso sem causar travamentos, optei por implementar o algoritmo de Chandy-Misra (1984), que funciona na base de troca de mensagens (tokens) entre os vizinhos. A lógica foi pensada para resolver os dois maiores gargalos desse problema:

* Prevenção de Deadlock: Resolvido logo na inicialização. As garrafas (arestas) formam um grafo direcionado, e o vértice com o maior ID começa com a posse do recurso para evitar dependências circulares.
* Prevenção de Starvation (Inanição): Resolvido com uma fila de requisições por ordem de chegada. Quando um filósofo termina de beber, a garrafa fica no estado "vazia" e ele a repassa imediatamente para o próximo da fila, sem segurar o recurso.

## Como rodar a simulação
O código usa apenas as bibliotecas nativas do Python (`threading`, `time`, etc.), então não tem complicação com instalação de pacotes externos.

Para executar, basta abrir o terminal na pasta do projeto e passar o arquivo `.txt` contendo a matriz de adjacência como argumento:

> python ChandyMisra.py caso1.txt

O programa vai exibir os logs de execução em tempo real no console e, ao finalizar, vai gerar automaticamente um arquivo (ex: `resultado_caso1.txt`) com as métricas da rodada.

## Resultados - Caso 1 (Jantar Clássico)
Rodando o cenário com 5 nós, onde cada filósofo tem grau de conectividade 2 e precisa beber 6 vezes, o programa rodou liso, sem deadlocks.

Tempo total de execução: 16.77 segundos.

Métricas por filósofo:
- Filósofo [0]: Tranquilo (5.76s) | Esperando (4.05s) | Bebendo (6.00s) | Espera média: 0.68s
- Filósofo [1]: Tranquilo (5.83s) | Esperando (2.89s) | Bebendo (6.00s) | Espera média: 0.48s
- Filósofo [2]: Tranquilo (4.00s) | Esperando (5.72s) | Bebendo (6.00s) | Espera média: 0.95s
- Filósofo [3]: Tranquilo (7.08s) | Esperando (3.65s) | Bebendo (6.00s) | Espera média: 0.61s
- Filósofo [4]: Tranquilo (2.69s) | Esperando (6.13s) | Bebendo (6.00s) | Espera média: 1.02s

Como todos cravaram exatos 6.00s no tempo "Bebendo", fica comprovado que nenhum filósofo sofreu inanição e todos conseguiram acessar os recursos as 6 vezes necessárias. O tempo médio de espera também se manteve bem equilibrado.
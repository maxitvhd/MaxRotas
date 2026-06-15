# Documentação de Alterações - 14/06/2026

Implementação do relatório de rotas otimizadas em PDF com layout profissional e otimização no balanceamento automático de clientes nos turnos.

## O que foi feito

### 1. Novo Sistema de Balanceamento de Turnos
- O algoritmo original de atribuição de turnos foi reformulado. Agora, em vez de atribuir um turno inteiro para um cluster geográfico completo (o que gerava dias sem determinados turnos e sobrecarga em outros), o sistema distribui os clientes de cada dia de forma totalmente equilibrada e sequencial entre os turnos selecionados (ex: Manhã, Tarde e Noite).
- A distribuição segue a ordem da rota otimizada pelo algoritmo vizinho mais próximo (*Nearest Neighbor*), garantindo que os clientes de cada turno fiquem agrupados geograficamente, evitando deslocamentos ineficientes.
- A divisão calcula as sobras e distribui de forma matemática perfeita (ex: 10 clientes divididos em 3 turnos resulta em 4 de manhã, 3 de tarde e 3 de noite).

### 2. Exportação de Relatório PDF Profissional
- Criado o método `exportar_pdf` em `main.py` utilizando recursos nativos da biblioteca `PyQt6` (`QPdfWriter` e `QTextDocument`). Isso atende às restrições do projeto de não instalar novas bibliotecas adicionais sem permissão expressa.
- Desenvolvido um template de relatório em HTML e estilizado com CSS embutido moderno e elegante para impressão (light-theme profissional):
  - Cabeçalho corporativo com metadados e contagem total de clientes.
  - Quebra de página automática a cada início de dia de semana (`page-break-before: always`).
  - Tabelas de rotas com listras alternadas (*zebra striping*) para fácil leitura, cabeçalho de tabela contrastante e bordas limpas.
  - Tipografia limpa e moderna.

### 3. Interface Gráfica (UI)
- Adicionado o botão **"Exportar Rota para PDF (.pdf)"** ao lado do botão de exportação para Excel.
- O botão do PDF permanece desabilitado inicialmente e é ativado automaticamente assim que a otimização de rotas é concluída com sucesso.

### 4. Controle de Logs e Variável de Ambiente (`.env`)
- Implementada a função `carregar_config_logs` para buscar a variável `MAXROTAS_LOGS` no arquivo `.env`. Se a variável estiver definida como `false`, `0` ou `off`, os logs do sistema serão completamente desativados, tanto na interface gráfica quanto no terminal.
- Toda a execução de roteirização foi numerada e padronizada nos logs conforme solicitado.

---
-- git commit -m "feat: adiciona exportacao para PDF estilizado e balanceamento equilibrado de turnos"

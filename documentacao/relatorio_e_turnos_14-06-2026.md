# Documentação de Alterações - 14/06/2026

Implementação do relatório de rotas otimizadas em PDF com layout profissional, agrupamento de rotas de capacidade limitada (ex: grupos de 10), correções de cores na interface escura e configuração do workflow do GitHub Actions para compilação do executável Windows.

## O que foi feito

### 1. Sistema de Agrupamento por Rota
- Criada a coluna **"Rota"** (`rota`) para representar individualmente cada grupo geográfico limitado pela capacidade de clientes escolhida (ex: grupos de 10).
- Exibição de tabelas e rotas separadas por "Rota" no programa e no PDF. A numeração de visitas (`Seq` / `ordem_visita`) agora reinicia a partir de 1 em cada rota, em vez de se misturar de forma desordenada por dia.
- Exportação da coluna "Rota" também integrada ao relatório em planilha do Excel.

### 2. Correção de Cores na Interface Escura (UI)
- Corrigida a legibilidade do painel esquerdo de configurações e caixas de seleção. Sob sistemas operacionais com temas claros ativos, as caixas de seleção, rótulos e caixas de grupo estavam herdando cores inadequadas do sistema, tornando o texto invisível (branco sobre fundo cinza-claro/branco).
- Aplicados estilos específicos no CSS da interface em `main.py`:
  - Fundo do painel de configuração definido explicitamente como `#121212`.
  - Fundo das GroupBoxes (`QGroupBox`) definido como `#1a1a1a`.
  - Fundo transparente forçado em `QLabel` e `QCheckBox` para evitar a interferência do tema nativo do sistema.

### 3. Geração de PDF Estilizado e Correção de Layout
- Corrigido o bug onde as tabelas de páginas seguintes a quebras de página colapsavam (ficavam verticais e ilegíveis).
- Configuração do `QPdfWriter` em 96 DPI para compatibilidade 1:1 com as medidas do motor de renderização do `QTextDocument`.
- Fim da compressão e colapso de tabelas utilizando a propriedade nativa `<table width="100%">` e dimensionamento em pontos vetoriais (`pt`) para as fontes do CSS embutido.

### 4. Workflow do GitHub Actions para Executável Windows (`.exe`)
- Adicionada configuração do pipeline CI/CD no arquivo `.github/workflows/build-windows.yml` para compilar o programa usando o `PyInstaller` em ambiente Windows Server virtualizado.
- O executável de distribuição única e limpo (`MaxRotas.exe`) é gerado automaticamente a cada push na branch `main` ou publicação de tag, ficando disponível para download imediato na aba **Actions** do repositório no GitHub.

---
-- git commit -m "ci: adiciona workflow do GitHub Actions e ajusta interface e agrupamento de rotas"

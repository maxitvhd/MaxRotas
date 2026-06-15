# MaxRotas - Roteirizador Inteligente 🚀

O **MaxRotas** é um aplicativo desktop robusto e de alto desempenho projetado para planejar, organizar e otimizar rotas de entrega ou visitas técnicas. Ele realiza georreferenciamento de endereços, agrupamento inteligente (clustering) por capacidade e cálculo da rota mais eficiente por aproximação geográfica.

Interface gráfica construída com **PyQt6** com visual premium dark mode e suporte a relatórios completos em **Excel** e **PDF**.

---

## 🌟 Recursos Principais

*   **Ingestão de Dados Flexível**: Suporte a planilhas Excel (`.xlsx`, `.xls`), arquivos estruturados em CSV (`.csv`), arquivos de texto (`.txt`) e documentos PDF (`.pdf`).
*   **Geocodificação Inteligente com Cache**: Converte endereços em coordenadas geográficas (latitude/longitude) via API pública do Nominatim (Geopy), com cache local em arquivo JSON para evitar chamadas de rede repetidas e otimizar o tempo de processamento.
*   **Agrupamento por Capacidade (K-Means)**: Utiliza inteligência artificial (Machine Learning) com o algoritmo K-Means da biblioteca `scikit-learn` para segmentar os clientes em grupos geográficos conforme a capacidade máxima de atendimento diário selecionada.
*   **Roteamento Eficiente (Nearest Neighbor)**: Ordena as visitas dentro de cada grupo usando o algoritmo do vizinho mais próximo, reduzindo drasticamente o tempo total e a distância percorrida no dia a dia.
*   **Priorização Inteligente de Grupos**: Permite definir palavras-chave prioritárias (ex: padarias, urgente, mercados) para que esses estabelecimentos sejam posicionados primeiro no roteiro.
*   **Divisão Balanceada de Turnos**: Distribui os clientes de forma equilibrada e sequencial entre os turnos selecionados (Manhã, Tarde, Noite), reiniciando o controle numérico a cada rota.
*   **Links de Navegação do Google Maps**: Gera links automáticos com rotas dinâmicas do Google Maps integrando até 10 paradas prontas para uso no celular do motorista.
*   **Relatório Excel e PDF Profissional**:
    *   Exportação de planilha completa contendo todas as coordenadas e informações.
    *   Exportação em PDF estilizado nativo (A4, 96 DPI, tipografia moderna e tabelas esticadas) agrupado de forma limpa por dia, turno e rotas individuais.
*   **Controle de Logs via `.env`**: Configuração centralizada para ligar/desligar logs de console e tela.

---

## 🛠️ Tecnologias Utilizadas

*   **Linguagem**: Python 3.11+
*   **Interface Gráfica (GUI)**: PyQt6 (QSS para design de tema escuro refinado)
*   **Manipulação de Dados**: Pandas & Numpy
*   **Inteligência & Clustering**: Scikit-Learn (KMeans)
*   **Geolocalização**: Geopy
*   **Leitura de Arquivos**: openpyxl, xlrd, pdfplumber

---

## 🚀 Como Executar Localmente

### Pré-requisitos
Certifique-se de ter o Python 3 instalado no seu computador.

### Passo a Passo

1.  **Clonar o Repositório**:
    ```bash
    git clone <url-do-seu-repositorio>
    cd MaxRotas
    ```

2.  **Configurar o Ambiente Virtual**:
    No Linux/macOS:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    No Windows (CMD):
    ```cmd
    python -m venv venv
    venv\Scripts\activate.bat
    ```

3.  **Instalar Dependências**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Caso não possua o arquivo requirements.txt, utilize o comando abaixo para instalar as bibliotecas necessárias)*:
    ```bash
    pip install PyQt6 pandas numpy openpyxl geopy scikit-learn scipy pdfplumber pyinstaller
    ```

4.  **Iniciar a Aplicação**:
    ```bash
    python main.py
    ```

---

## ⚙️ Configuração do Sistema (`.env`)

Você pode ativar ou desativar os logs de depuração criando ou editando um arquivo `.env` na raiz do projeto:

```env
# Ativar ou desativar logs de execução (true / false)
MAXROTAS_LOGS=true
```

---

## 📦 Compilação Automática no Windows (CI/CD GitHub Actions)

Este repositório possui uma integração contínua configurada via **GitHub Actions** em `.github/workflows/build-windows.yml`.

A cada atualização enviada para a branch `main` ou publicação de uma tag (`v*`), o GitHub criará automaticamente o executável nativo **`MaxRotas.exe`** para Windows utilizando o `PyInstaller`.
*   Para baixar o executável compilado, acesse a aba **Actions** no seu repositório no GitHub, clique na última execução com sucesso e baixe o arquivo comprimido na seção **Artifacts**.

---

## ⚙️ Como Gerar o Executável Manualmente (PyInstaller)

Se preferir compilar o aplicativo para um executável único no seu próprio computador, execute:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name=MaxRotas main.py
```
O arquivo gerado ficará disponível dentro do diretório `dist/`.

---

## 📝 Licença
Este projeto é de uso interno e confidencial. Consulte a equipe administrativa para mais informações.

---
-- git commit -m "docs: adiciona arquivo README em portugues com instruções de instalação e CI/CD"

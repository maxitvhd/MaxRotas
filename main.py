#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import re
import webbrowser
import pandas as pd
import numpy as np

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QSpinBox, QCheckBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QTabWidget, QTextEdit, QMessageBox,
    QListWidget, QListWidgetItem, QHeaderView, QLineEdit, QScrollArea
)
from PyQt6.QtCore import Qt, QSize, QSizeF
from PyQt6.QtGui import QFont, QIcon, QTextDocument, QPdfWriter, QPageSize
from datetime import datetime

# Importações de geocodificação e clustering com fallback
try:
    from geopy.geocoders import Nominatim
    HAS_GEOPY = True
except ImportError:
    HAS_GEOPY = False

try:
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False


class OtimizadorRotasApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MaxRotas - Roteirizador Inteligente")
        self.resize(1100, 750)
        
        self.caminho_arquivo = ""
        self.df_carregado = None
        self.df_processado = None
        self.geolocator = Nominatim(user_agent="max_rotas_gui_agent") if HAS_GEOPY else None
        
        # Ativa ou desativa logs conforme o arquivo .env
        self.logs_ativos = self.carregar_config_logs()

        self.init_ui()
        self.aplicar_tema_escuro()

    def carregar_config_logs(self):
        # Carrega configuracao do arquivo .env para logs
        logs_ativos = True
        caminho_env = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        if os.path.exists(caminho_env):
            try:
                with open(caminho_env, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#"):
                            parts = line.split("=", 1)
                            if len(parts) == 2:
                                key = parts[0].strip()
                                val = parts[1].strip()
                                if key == "MAXROTAS_LOGS":
                                    logs_ativos = val.lower() in ["true", "1", "yes", "on"]
            except Exception:
                pass
        return logs_ativos

    def init_ui(self):
        # Widget principal
        widget_central = QWidget()
        self.setCentralWidget(widget_central)
        layout_principal = QHBoxLayout(widget_central)
        layout_principal.setSpacing(15)
        layout_principal.setContentsMargins(15, 15, 15, 15)

        # QScrollArea para tornar o painel esquerdo responsivo e rolável
        scroll_config = QScrollArea()
        scroll_config.setWidgetResizable(True)
        scroll_config.setFixedWidth(340)
        scroll_config.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")

        # ================= PAINEL LATERAL ESQUERDO (CONFIGURAÇÕES) =================
        painel_config = QWidget()
        layout_config = QVBoxLayout(painel_config)
        layout_config.setContentsMargins(5, 5, 5, 5)
        layout_config.setSpacing(12)

        # Título
        lbl_titulo = QLabel("Configurações da Rota")
        lbl_titulo.setFont(QFont("Outfit", 16, QFont.Weight.Bold))
        lbl_titulo.setStyleSheet("color: #e0e0e0; margin-bottom: 5px;")
        layout_config.addWidget(lbl_titulo)

        # Grupo: Seleção de Arquivo
        grp_arquivo = QGroupBox("1. Ingestão de Dados")
        lyt_arquivo = QVBoxLayout(grp_arquivo)
        self.btn_carregar = QPushButton("Selecionar Lista (.xlsx, .csv, .txt, .pdf)")
        self.btn_carregar.clicked.connect(self.abrir_seletor_arquivo)
        self.lbl_nome_arquivo = QLabel("Nenhum arquivo selecionado")
        self.lbl_nome_arquivo.setWordWrap(True)
        self.lbl_nome_arquivo.setStyleSheet("color: #9e9e9e; font-style: italic;")
        
        self.lbl_skip_linhas = QLabel("Ignorar linhas do cabeçalho:")
        self.spin_skip_linhas = QSpinBox()
        self.spin_skip_linhas.setRange(0, 100)
        self.spin_skip_linhas.setValue(0)
        
        lyt_arquivo.addWidget(self.btn_carregar)
        lyt_arquivo.addWidget(self.lbl_nome_arquivo)
        lyt_arquivo.addWidget(self.lbl_skip_linhas)
        lyt_arquivo.addWidget(self.spin_skip_linhas)
        layout_config.addWidget(grp_arquivo)

        # Grupo: Turnos e Dias
        grp_operacao = QGroupBox("2. Turnos e Agenda")
        lyt_operacao = QVBoxLayout(grp_operacao)
        
        # Turnos
        lyt_operacao.addWidget(QLabel("<b>Turnos Operacionais:</b>"))
        self.chk_manha = QCheckBox("Manhã")
        self.chk_manha.setChecked(True)
        self.chk_tarde = QCheckBox("Tarde")
        self.chk_tarde.setChecked(True)
        self.chk_noite = QCheckBox("Noite")
        lyt_operacao.addWidget(self.chk_manha)
        lyt_operacao.addWidget(self.chk_tarde)
        lyt_operacao.addWidget(self.chk_noite)

        # Dias da Semana
        lyt_operacao.addWidget(QLabel("<b>Dias da Semana:</b>"))
        self.dias_chks = []
        dias = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado"]
        for dia in dias:
            chk = QCheckBox(dia)
            chk.setChecked(dia not in ["Sábado"])
            self.dias_chks.append(chk)
            lyt_operacao.addWidget(chk)

        layout_config.addWidget(grp_operacao)

        # Grupo: Parâmetros Rota
        grp_parametros = QGroupBox("3. Capacidade e Filtros")
        lyt_parametros = QVBoxLayout(grp_parametros)
        
        # Capacidade
        lyt_parametros.addWidget(QLabel("<b>Capacidade Diária (Clientes/Dia):</b>"))
        self.spin_capacidade = QSpinBox()
        self.spin_capacidade.setRange(1, 100)
        self.spin_capacidade.setValue(10)
        lyt_parametros.addWidget(self.spin_capacidade)

        # Exclusão inteligente
        self.chk_excluir_bloqueados = QCheckBox("Excluir clientes bloqueados")
        self.chk_excluir_bloqueados.setChecked(True)
        lyt_parametros.addWidget(self.chk_excluir_bloqueados)

        # Priorização de Grupo
        lyt_parametros.addWidget(QLabel("<b>Priorizar Grupos (ex: padarias, urgente):</b>"))
        self.txt_prioridade = QLineEdit()
        self.txt_prioridade.setPlaceholderText("padarias, mercados, urgente")
        lyt_parametros.addWidget(self.txt_prioridade)

        layout_config.addWidget(grp_parametros)

        # Botão Roteirizar
        self.btn_roteirizar = QPushButton("OTIMIZAR ROTAS")
        self.btn_roteirizar.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; height: 40px;")
        self.btn_roteirizar.clicked.connect(self.processar_roteirizacao)
        layout_config.addWidget(self.btn_roteirizar)

        scroll_config.setWidget(painel_config)
        layout_principal.addWidget(scroll_config)

        # ================= PAINEL PRINCIPAL DIREITO (TABELAS E LOGS) =================
        self.tabs = QTabWidget()
        
        # Aba 1: Clientes Carregados
        self.tab_clientes = QWidget()
        lyt_tab_clientes = QVBoxLayout(self.tab_clientes)
        self.lbl_total_clientes = QLabel("Nenhum cliente carregado")
        self.table_clientes = QTableWidget()
        self.table_clientes.setColumnCount(6)
        self.table_clientes.setHorizontalHeaderLabels(["Nome", "Endereço", "Número", "CEP", "Grupo", "Status"])
        self.table_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lyt_tab_clientes.addWidget(self.lbl_total_clientes)
        lyt_tab_clientes.addWidget(self.table_clientes)
        self.tabs.addTab(self.tab_clientes, "Clientes Carregados")

        # Aba 2: Rotas Diárias
        self.tab_rotas = QWidget()
        lyt_tab_rotas = QVBoxLayout(self.tab_rotas)
        
        lyt_botoes_export = QHBoxLayout()
        
        self.btn_exportar = QPushButton("Exportar Rota para Excel (.xlsx)")
        self.btn_exportar.setEnabled(False)
        self.btn_exportar.clicked.connect(self.exportar_planilha)
        self.btn_exportar.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        
        self.btn_exportar_pdf = QPushButton("Exportar Rota para PDF (.pdf)")
        self.btn_exportar_pdf.setEnabled(False)
        self.btn_exportar_pdf.clicked.connect(self.exportar_pdf)
        self.btn_exportar_pdf.setStyleSheet("background-color: #e74c3c; color: white; font-weight: bold;")
        
        lyt_botoes_export.addWidget(self.btn_exportar)
        lyt_botoes_export.addWidget(self.btn_exportar_pdf)
        
        self.table_rotas = QTableWidget()
        self.table_rotas.setColumnCount(7)
        self.table_rotas.setHorizontalHeaderLabels(["Dia", "Turno", "Ordem", "Nome", "Endereço", "CEP", "Grupo"])
        self.table_rotas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        lyt_tab_rotas.addLayout(lyt_botoes_export)
        lyt_tab_rotas.addWidget(self.table_rotas)
        self.tabs.addTab(self.tab_rotas, "Rotas Otimizadas")

        # Aba 3: Mapas e Logs
        self.tab_logs = QWidget()
        lyt_tab_logs = QVBoxLayout(self.tab_logs)
        
        lyt_tab_logs.addWidget(QLabel("<b>Links de Navegação do Google Maps:</b>"))
        self.list_mapas = QListWidget()
        self.list_mapas.itemDoubleClicked.connect(self.abrir_link_mapa)
        lyt_tab_logs.addWidget(self.list_mapas)

        lyt_tab_logs.addWidget(QLabel("<b>Logs do Sistema:</b>"))
        self.txt_logs = QTextEdit()
        self.txt_logs.setReadOnly(True)
        lyt_tab_logs.addWidget(self.txt_logs)
        
        self.tabs.addTab(self.tab_logs, "Visualização e Logs")

        layout_principal.addWidget(self.tabs)

    def log(self, mensagem):
        if self.logs_ativos:
            self.txt_logs.append(mensagem)
            print(mensagem)

    def abrir_seletor_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self, "Selecionar Arquivo", "", "Arquivos de Dados (*.xlsx *.xls *.csv *.txt *.pdf)"
        )
        if caminho:
            self.caminho_arquivo = caminho
            self.lbl_nome_arquivo.setText(os.path.basename(caminho))
            self.carregar_dados()

    def _normalizar_texto(self, texto):
        if not isinstance(texto, str):
            return str(texto)
        texto = texto.strip().lower()
        substituicoes = {
            'á': 'a', 'à': 'a', 'â': 'a', 'ã': 'a',
            'é': 'e', 'ê': 'e',
            'í': 'i',
            'ó': 'o', 'ô': 'o', 'õ': 'o',
            'ú': 'u', 'ü': 'u',
            'ç': 'c',
        }
        for orig, sub in substituicoes.items():
            texto = texto.replace(orig, sub)
        return texto

    def _buscar_coluna(self, df, alternativas):
        for col in df.columns:
            if col in alternativas:
                return col
            for alt in alternativas:
                if alt in col:
                    return col
        return None

    def carregar_dados(self):
        try:
            ext = os.path.splitext(self.caminho_arquivo)[1].lower()
            skip = self.spin_skip_linhas.value()

            if ext == ".csv":
                self.df_carregado = pd.read_csv(self.caminho_arquivo, skiprows=skip)
            elif ext in [".xlsx", ".xls"]:
                self.df_carregado = pd.read_excel(self.caminho_arquivo, skiprows=skip)
            elif ext == ".txt":
                with open(self.caminho_arquivo, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[skip:]
                data = [line.strip().split(',') for line in lines if line.strip()]
                if data:
                    headers = data[0]
                    self.df_carregado = pd.DataFrame(data[1:], columns=headers)
            elif ext == ".pdf":
                self.df_carregado = self._ler_pdf(self.caminho_arquivo)
            else:
                raise ValueError("Extensão de arquivo não suportada.")

            if self.df_carregado is None or self.df_carregado.empty:
                raise ValueError("O arquivo lido está vazio ou mal-estruturado.")

            # Normaliza cabeçalhos
            self.df_carregado.columns = [self._normalizar_texto(c) for c in self.df_carregado.columns]

            # Detecta e normaliza colunas obrigatórias
            col_nome = self._buscar_coluna(self.df_carregado, ['nome', 'cliente', 'razao_social'])
            col_cep = self._buscar_coluna(self.df_carregado, ['cep', 'codigo_postal'])
            col_endereco = self._buscar_coluna(self.df_carregado, ['endereco', 'logradouro', 'rua'])
            col_numero = self._buscar_coluna(self.df_carregado, ['numero', 'num'])
            col_status = self._buscar_coluna(self.df_carregado, ['status', 'ativo', 'bloqueado'])
            col_grupo = self._buscar_coluna(self.df_carregado, ['grupo', 'pdv', 'tipo'])

            if not col_nome or not col_cep or not col_endereco:
                QMessageBox.warning(
                    self, "Aviso de Mapeamento",
                    "Certifique-se de que o cabeçalho contenha colunas com 'nome', 'cep' e 'endereco'!"
                )
                return

            # Padroniza dados
            self.df_carregado = self.df_carregado.rename(columns={
                col_nome: 'nome',
                col_cep: 'cep',
                col_endereco: 'endereco'
            })
            self.df_carregado['numero'] = self.df_carregado[col_numero] if col_numero else ''
            self.df_carregado['status'] = self.df_carregado[col_status] if col_status else 'Ativo'
            self.df_carregado['grupo'] = self.df_carregado[col_grupo] if col_grupo else 'geral'

            self.exibir_clientes_carregados()
            self.log(f"Arquivo carregado com sucesso. {len(self.df_carregado)} registros encontrados.")

        except Exception as e:
            QMessageBox.critical(self, "Erro de Leitura", f"Erro ao ler arquivo: {e}")

    def _ler_pdf(self, caminho):
        if not HAS_PDFPLUMBER:
            raise ImportError("Instale pdfplumber para ler PDFs. Rode: pip install pdfplumber")

        linhas = []
        with pdfplumber.open(caminho) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    return pd.DataFrame(table[1:], columns=table[0])
                else:
                    text = page.extract_text()
                    if text:
                        for line in text.split("\n"):
                            parts = re.split(r'\s{2,}', line.strip())
                            if len(parts) > 1:
                                linhas.append(parts)
        if linhas:
            return pd.DataFrame(linhas[1:], columns=linhas[0])
        return pd.DataFrame()

    def exibir_clientes_carregados(self):
        df = self.df_carregado
        self.table_clientes.setRowCount(len(df))
        self.lbl_total_clientes.setText(f"Total de clientes importados: {len(df)}")
        
        ceps_vazios = 0
        for i, row in df.iterrows():
            nome = str(row.get('nome', ''))
            end = str(row.get('endereco', ''))
            num = str(row.get('numero', ''))
            cep = str(row.get('cep', ''))
            grp = str(row.get('grupo', ''))
            status = str(row.get('status', ''))

            # Validação visual do CEP
            if not cep.strip() or cep.strip().lower() == 'nan':
                ceps_vazios += 1
                item_cep = QTableWidgetItem("SEM CEP!")
                item_cep.setBackground(Qt.GlobalColor.red)
            else:
                item_cep = QTableWidgetItem(cep)

            self.table_clientes.setItem(i, 0, QTableWidgetItem(nome))
            self.table_clientes.setItem(i, 1, QTableWidgetItem(end))
            self.table_clientes.setItem(i, 2, QTableWidgetItem(num))
            self.table_clientes.setItem(i, 3, item_cep)
            self.table_clientes.setItem(i, 4, QTableWidgetItem(grp))
            self.table_clientes.setItem(i, 5, QTableWidgetItem(status))

        if ceps_vazios > 0:
            self.log(f"[AVISO] Foram encontrados {ceps_vazios} clientes sem CEP na lista!")

    def processar_roteirizacao(self):
        if self.df_carregado is None or self.df_carregado.empty:
            QMessageBox.warning(self, "Aviso", "Por favor, carregue uma lista de clientes primeiro.")
            return

        self.txt_logs.clear()
        self.list_mapas.clear()
        self.log("LOG : 1 iniciando otimização de rotas - ")

        # Obter configurações da Interface
        turnos = []
        if self.chk_manha.isChecked(): turnos.append("Manhã")
        if self.chk_tarde.isChecked(): turnos.append("Tarde")
        if self.chk_noite.isChecked(): turnos.append("Noite")

        if not turnos:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um turno de operação.")
            return

        dias = [chk.text() for chk in self.dias_chks if chk.isChecked()]
        if not dias:
            QMessageBox.warning(self, "Aviso", "Selecione pelo menos um dia da semana para roteirização.")
            return

        capacidade = self.spin_capacidade.value()
        excluir_bloqueados = self.chk_excluir_bloqueados.isChecked()

        df_filt = self.df_carregado.copy()

        # Filtrar Bloqueados
        if excluir_bloqueados:
            df_filt['status_limpo'] = df_filt['status'].astype(str).str.strip().str.lower()
            bloqueados = df_filt['status_limpo'].isin(['bloqueado', 'inativo', 'n', 'nao', 'false', '0'])
            df_filt = df_filt[~bloqueados].copy()
            self.log(f"LOG : 2 filtrando inativos e validando CEPs ({bloqueados.sum()} inativos excluídos) - ")

        # Validação extra de CEPs
        df_filt['cep'] = df_filt['cep'].astype(str).str.strip()
        df_filt = df_filt[df_filt['cep'] != 'nan']
        df_filt = df_filt[df_filt['cep'] != '']

        if df_filt.empty:
            QMessageBox.warning(self, "Aviso", "Nenhum cliente ativo e com CEP válido restante para roteirização.")
            return

        # Carrega o cache de geocodificação
        import json
        import time
        from PyQt6.QtCore import QCoreApplication

        cache_file = "geocoding_cache.json"
        cache = {}
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache = json.load(f)
            except Exception:
                cache = {}

        # Geocodificação
        self.log(f"LOG : 3 consultando coordenadas e georreferenciando {len(df_filt)} clientes - ")
        latitudes = []
        longitudes = []
        total_passos = len(df_filt)
        
        for idx, (df_idx, row) in enumerate(df_filt.iterrows()):
            nome = row['nome']
            cep = row['cep'].replace("-", "").replace(".", "")
            end = row['endereco']
            num = str(row['numero'])

            query = f"{end}, {num}, Brasil" if num else f"{end}, Brasil"
            if len(cep) == 8:
                query += f", CEP {cep[:5]}-{cep[5:]}"

            # Tenta obter do cache
            if query in cache:
                lat = cache[query]["lat"]
                lon = cache[query]["lon"]
            else:
                self.log(f"[{idx+1}/{total_passos}] Consultando rede: {nome} ({query})")
                QCoreApplication.processEvents() # Mantém a interface ativa
                
                lat, lon = None, None
                if self.geolocator:
                    try:
                        loc = self.geolocator.geocode(query, timeout=4)
                        if loc:
                            lat, lon = loc.latitude, loc.longitude
                        elif len(cep) == 8:
                            loc_c = self.geolocator.geocode(f"CEP {cep[:5]}-{cep[5:]}, Brasil", timeout=4)
                            if loc_c:
                                lat, lon = loc_c.latitude, loc_c.longitude
                        # Pausa de 1s para respeitar as políticas de uso da API pública
                        time.sleep(1)
                    except Exception:
                        pass

                if lat is None or lon is None:
                    # Fallback baseado no CEP
                    cep_num = int(re.sub(r'\D', '', cep)) if re.sub(r'\D', '', cep) else 10000000
                    lat = -23.55 + ((cep_num % 1000) / 10000.0)
                    lon = -46.63 + ((cep_num % 137) / 10000.0)

                # Salva no cache
                cache[query] = {"lat": lat, "lon": lon}
                if idx % 10 == 0:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache, f, ensure_ascii=False, indent=4)

            latitudes.append(lat)
            longitudes.append(lon)

        # Salva cache final
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)

        df_filt['latitude'] = latitudes
        df_filt['longitude'] = longitudes

        # Clustering
        total_ativos = len(df_filt)
        n_clusters = int(np.ceil(total_ativos / capacidade))
        if n_clusters < 1: n_clusters = 1

        self.log(f"LOG : 4 agrupando clientes em {n_clusters} clusters com KMeans (max: {capacidade} por dia) - ")

        if HAS_SKLEARN and total_ativos >= n_clusters:
            coords = df_filt[['latitude', 'longitude']].values
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            df_filt['cluster'] = kmeans.fit_predict(coords)
        else:
            df_filt = df_filt.sort_values(by=['cep', 'numero']).copy()
            df_filt['cluster'] = [i // capacidade for i in range(len(df_filt))]

        # Roteamento e ordenamento fino
        self.log("LOG : 5 ordenando rotas por proximidade e priorização - ")
        df_saida_total = []
        clusters_list = sorted(df_filt['cluster'].unique())

        for idx_c, cluster_id in enumerate(clusters_list):
            df_c = df_filt[df_filt['cluster'] == cluster_id].copy()
            
            # Calendário
            dia_index = idx_c % len(dias)
            dia_atribuido = dias[dia_index]
            df_c['dia_semana'] = dia_atribuido

            # Priorização de grupos
            palavras_prioritarias = [x.strip().lower() for x in self.txt_prioridade.text().split(",") if x.strip()]
            if palavras_prioritarias:
                df_c['prioridade_grupo'] = df_c['grupo'].astype(str).str.lower().apply(
                    lambda g: 0 if any(p in g for p in palavras_prioritarias) else 1
                )
            else:
                df_c['prioridade_grupo'] = 0

            df_c = df_c.sort_values(by=['prioridade_grupo']).copy()

            # Nearest Neighbor
            coords_c = df_c[['latitude', 'longitude']].values
            indices_ordenados = []
            restantes = list(range(len(df_c)))
            atual = 0
            indices_ordenados.append(atual)
            restantes.remove(atual)

            while restantes:
                pt_atual = coords_c[atual]
                dists = np.sum((coords_c[restantes] - pt_atual) ** 2, axis=1)
                prox = restantes[np.argmin(dists)]
                indices_ordenados.append(prox)
                restantes.remove(prox)
                atual = prox

            df_c = df_c.iloc[indices_ordenados].copy()
            
            # Distribuindo clientes nos turnos de forma balanceada
            n_clientes = len(df_c)
            n_turnos = len(turnos)
            base_size = n_clientes // n_turnos
            remainder = n_clientes % n_turnos
            
            shift_assignments = []
            order_assignments = []
            
            for i, turno in enumerate(turnos):
                size = base_size + (1 if i < remainder else 0)
                for order in range(1, size + 1):
                    shift_assignments.append(turno)
                    order_assignments.append(order)
            
            df_c['turno'] = shift_assignments
            df_c['ordem_visita'] = order_assignments
            df_saida_total.append(df_c)

        self.df_processado = pd.concat(df_saida_total, ignore_index=True)

        # Ordena as rotas por dia da semana, turno e pela sequencia do vizinho mais proximo
        ordem_dias = {
            "Segunda": 0, "Terça": 1, "Quarta": 2, "Quinta": 3,
            "Sexta": 4, "Sábado": 5, "Domingo": 6
        }
        ordem_turnos = {
            "Manhã": 0, "Tarde": 1, "Noite": 2
        }
        self.df_processado['dia_num'] = self.df_processado['dia_semana'].map(ordem_dias).fillna(99)
        self.df_processado['turno_num'] = self.df_processado['turno'].map(ordem_turnos).fillna(99)
        
        self.df_processado = self.df_processado.sort_values(by=['dia_num', 'turno_num', 'ordem_visita']).copy()
        
        # Recalcula a ordem de visita para ser contínua dentro de cada dia/turno
        for (dia, turno), grupo in self.df_processado.groupby(['dia_semana', 'turno'], sort=False):
            self.df_processado.loc[grupo.index, 'ordem_visita'] = range(1, len(grupo) + 1)
            
        # Remove as colunas auxiliares de ordenacao
        self.df_processado = self.df_processado.drop(columns=['dia_num', 'turno_num'])

        self.exibir_rotas_otimizadas()
        self.gerar_links_maps_interface()

        self.log("LOG : 8 otimização concluída com sucesso - ")
        self.btn_exportar.setEnabled(True)
        self.btn_exportar_pdf.setEnabled(True)
        self.tabs.setCurrentIndex(1) # Muda para aba de rotas

    def exibir_rotas_otimizadas(self):
        df = self.df_processado
        self.table_rotas.setRowCount(len(df))
        
        for i, row in df.iterrows():
            self.table_rotas.setItem(i, 0, QTableWidgetItem(str(row['dia_semana'])))
            self.table_rotas.setItem(i, 1, QTableWidgetItem(str(row['turno'])))
            self.table_rotas.setItem(i, 2, QTableWidgetItem(str(row['ordem_visita'])))
            self.table_rotas.setItem(i, 3, QTableWidgetItem(str(row['nome'])))
            self.table_rotas.setItem(i, 4, QTableWidgetItem(str(row['endereco']) + ", " + str(row['numero'])))
            self.table_rotas.setItem(i, 5, QTableWidgetItem(str(row['cep'])))
            self.table_rotas.setItem(i, 6, QTableWidgetItem(str(row['grupo'])))

    def gerar_links_maps_interface(self):
        self.log("LOG : 7 gerando links de navegação para o Google Maps - ")
        for (dia, turno), grupo in self.df_processado.groupby(['dia_semana', 'turno']):
            coords_str = []
            for _, row in grupo.head(10).iterrows(): # Google Maps aceita idealmente 10 waypoints
                coords_str.append(f"{row['latitude']},{row['longitude']}")

            if len(coords_str) > 1:
                origem = coords_str[0]
                destino = coords_str[-1]
                waypoints = "|".join(coords_str[1:-1])
                if waypoints:
                    url = f"https://www.google.com/maps/dir/?api=1&origin={origem}&destination={destino}&waypoints={waypoints}&travelmode=driving"
                else:
                    url = f"https://www.google.com/maps/dir/?api=1&origin={origem}&destination={destino}&travelmode=driving"
            elif len(coords_str) == 1:
                url = f"https://www.google.com/maps/search/?api=1&query={coords_str[0]}"
            else:
                continue

            item = QListWidgetItem(f"Rota: {dia} ({turno}) - {len(grupo)} Clientes - [Clique Duplo para abrir no Google Maps]")
            item.setData(Qt.ItemDataRole.UserRole, url)
            self.list_mapas.addItem(item)
            self.log(f"Link Gerado - {dia} ({turno}): {url}")

    def abrir_link_mapa(self, item):
        url = item.data(Qt.ItemDataRole.UserRole)
        if url:
            webbrowser.open(url)

    def exportar_planilha(self):
        if self.df_processado is None or self.df_processado.empty:
            return

        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar Relatório", "rotas_otimizadas.xlsx", "Planilha Excel (*.xlsx)"
        )
        if caminho:
            try:
                colunas_exportar = [
                    'dia_semana', 'turno', 'ordem_visita', 'nome', 
                    'endereco', 'numero', 'cep', 'grupo', 'status', 'latitude', 'longitude'
                ]
                df_exp = self.df_processado[colunas_exportar].copy()
                df_exp.to_excel(caminho, index=False)
                QMessageBox.information(self, "Sucesso", f"Relatório exportado para:\n{caminho}")
            except Exception as e:
                QMessageBox.critical(self, "Erro ao Exportar", f"Não foi possível salvar o arquivo: {e}")

    def exportar_pdf(self):
        # verifica se possui dados para exportar
        if self.df_processado is None or self.df_processado.empty:
            return

        # exibe caixa de dialogo para o usuario salvar o pdf
        caminho, _ = QFileDialog.getSaveFileName(
            self, "Exportar Relatório PDF", "rotas_otimizadas.pdf", "Documento PDF (*.pdf)"
        )
        if not caminho:
            return

        try:
            self.log("LOG : 9 gerando relatório em PDF estilizado - ")

            # configura o escritor de pdf
            writer = QPdfWriter(caminho)
            writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
            writer.setResolution(96) # resolucao ideal para visualizacao e impressao de HTML 1:1

            # define a ordem dos dias e turnos para ordenacao correta
            ordem_dias = {
                "Segunda": 0, "Terça": 1, "Quarta": 2, "Quinta": 3,
                "Sexta": 4, "Sábado": 5, "Domingo": 6
            }
            ordem_turnos = {
                "Manhã": 0, "Tarde": 1, "Noite": 2
            }

            dias_unicos = sorted(
                self.df_processado['dia_semana'].unique(),
                key=lambda d: ordem_dias.get(d, 99)
            )

            html = []
            html.append("<html><head>")
            html.append("<style>")
            html.append("body { font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color: #2c3e50; margin: 0; }")
            html.append(".header { background-color: #2c3e50; color: #ffffff; padding: 15pt; border-radius: 6pt; margin-bottom: 25pt; }")
            html.append(".header h1 { margin: 0; font-size: 22pt; font-weight: bold; }")
            html.append(".header p { margin: 5pt 0 0 0; font-size: 13pt; color: #bdc3c7; }")
            html.append(".day-section { margin-top: 15pt; }")
            html.append(".day-title { color: #2c3e50; font-size: 16pt; border-bottom: 2pt solid #3498db; padding-bottom: 4pt; margin-bottom: 12pt; font-weight: bold; text-transform: uppercase; }")
            html.append(".shift-section { margin-bottom: 20pt; }")
            html.append(".shift-title { color: #2980b9; font-size: 13pt; font-weight: bold; margin-bottom: 6pt; }")
            html.append("th { background-color: #34495e; color: #ffffff; font-weight: bold; text-align: left; padding: 6pt; font-size: 11pt; border: 1px solid #34495e; }")
            html.append("td { padding: 6pt; font-size: 10pt; border: 1px solid #bdc3c7; }")
            html.append(".alt-row { background-color: #f8f9fa; }")
            html.append(".text-center { text-align: center; }")
            html.append(".page-break { page-break-before: always; }")
            html.append("</style></head><body>")

            # cabecalho do relatorio
            data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            html.append('<div class="header">')
            html.append('<h1>MaxRotas - Relatório de Rotas Otimizadas</h1>')
            html.append(f'<p>Gerado em: {data_atual} | Total de Clientes Roteirizados: {len(self.df_processado)}</p>')
            html.append('</div>')

            # helper para formatar os nomes dos dias da semana
            def formatar_dia(d):
                if d in ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]:
                    return f"{d}-feira"
                return d

            for idx_d, dia in enumerate(dias_unicos):
                df_dia = self.df_processado[self.df_processado['dia_semana'] == dia]
                if df_dia.empty:
                    continue

                # quebra de pagina para cada dia exceto o primeiro
                if idx_d > 0:
                    html.append('<div class="page-break"></div>')

                html.append('<div class="day-section">')
                html.append(f'<div class="day-title">{formatar_dia(dia)}</div>')

                turnos_unicos = sorted(
                    df_dia['turno'].unique(),
                    key=lambda t: ordem_turnos.get(t, 99)
                )

                for turno in turnos_unicos:
                    df_turno = df_dia[df_dia['turno'] == turno].sort_values(by='ordem_visita')
                    if df_turno.empty:
                        continue

                    html.append('<div class="shift-section">')
                    html.append(f'<div class="shift-title">Turno: {turno} ({len(df_turno)} Clientes)</div>')
                    # Usando width="100%" na tag da tabela para o PyQt esticar corretamente
                    html.append('<table width="100%">')
                    html.append('<thead><tr>')
                    html.append('<th width="8%" style="text-align: center;">Seq</th>')
                    html.append('<th width="25%">Cliente</th>')
                    html.append('<th width="45%">Endereço</th>')
                    html.append('<th width="12%">CEP</th>')
                    html.append('<th width="10%">Grupo</th>')
                    html.append('</tr></thead><tbody>')

                    for idx_row, (_, row) in enumerate(df_turno.iterrows()):
                        alt_class = ' class="alt-row"' if idx_row % 2 == 1 else ''
                        nome = str(row.get('nome', ''))
                        
                        # formata o endereco completo com o numero do local
                        end = str(row.get('endereco', ''))
                        num = str(row.get('numero', ''))
                        if num and num.lower() != 'nan':
                            end = f"{end}, {num}"
                            
                        cep = str(row.get('cep', ''))
                        grp = str(row.get('grupo', ''))
                        ordem = str(row.get('ordem_visita', ''))

                        html.append(f'<tr{alt_class}>')
                        html.append(f'<td class="text-center">{ordem}</td>')
                        html.append(f'<td>{nome}</td>')
                        html.append(f'<td>{end}</td>')
                        html.append(f'<td>{cep}</td>')
                        html.append(f'<td>{grp}</td>')
                        html.append('</tr>')

                    html.append('</tbody></table>')
                    html.append('</div>') # fecha shift-section

                html.append('</div>') # fecha day-section

            html.append('</body></html>')

            # renderiza e salva o PDF
            doc = QTextDocument()
            # Define o tamanho do documento com base na largura da página em pixels
            margem = 48 # margem de 0.5 polegadas (48 pixels a 96 DPI)
            doc.setTextWidth(writer.width() - 2 * margem)
            
            doc.setHtml("".join(html))
            doc.print(writer)
            
            self.log(f"LOG : 10 pdf exportado com sucesso para {caminho} - ")
            QMessageBox.information(self, "Sucesso", f"Relatório PDF exportado com sucesso em:\n{caminho}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Exportar PDF", f"Não foi possível salvar o arquivo PDF: {e}")

    def aplicar_tema_escuro(self):
        # Estilização moderna e refinada (Aesthetics)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QWidget {
                color: #e0e0e0;
                font-family: "Outfit", "Segoe UI", sans-serif;
                font-size: 13px;
            }
            QGroupBox {
                border: 1px solid #2d2d2d;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 15px;
                font-weight: bold;
                color: #3498db;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
            }
            QPushButton {
                background-color: #1e1e1e;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                padding: 8px 12px;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #2b2b2b;
                border-color: #3498db;
            }
            QPushButton:pressed {
                background-color: #1a1a1a;
            }
            QLineEdit, QSpinBox {
                background-color: #1e1e1e;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                padding: 6px;
                color: #ffffff;
            }
            QLineEdit:focus, QSpinBox:focus {
                border-color: #3498db;
            }
            QTableWidget {
                background-color: #1a1a1a;
                border: 1px solid #2d2d2d;
                gridline-color: #2b2b2b;
                border-radius: 6px;
                color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QHeaderView::section {
                background-color: #252525;
                color: #ffffff;
                padding: 8px;
                border: 1px solid #1a1a1a;
                font-weight: bold;
            }
            QTabWidget::pane {
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                background-color: #1a1a1a;
            }
            QTabBar::tab {
                background-color: #1e1e1e;
                border: 1px solid #2d2d2d;
                padding: 8px 16px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #1a1a1a;
                border-bottom-color: #1a1a1a;
                color: #3498db;
                font-weight: bold;
            }
            QTextEdit, QListWidget {
                background-color: #1a1a1a;
                border: 1px solid #2d2d2d;
                border-radius: 6px;
                color: #e0e0e0;
                padding: 8px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                background-color: #1e1e1e;
                border: 1px solid #2d2d2d;
                border-radius: 4px;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border-color: #3498db;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = OtimizadorRotasApp()
    window.show()
    sys.exit(app.exec())

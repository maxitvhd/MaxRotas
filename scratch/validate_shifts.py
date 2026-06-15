import sys
import os
import pandas as pd
from PyQt6.QtWidgets import QApplication

# Adiciona o diretório atual ao path para garantir que a importação funcione
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from main import OtimizadorRotasApp

def test_validation():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    win = OtimizadorRotasApp()
    
    # Define arquivo e carrega dados
    win.caminho_arquivo = os.path.abspath(os.path.dirname(__file__) + "/../clientes_exemplo.xlsx")
    win.carregar_dados()
    
    # Configura 3 turnos ativos
    win.chk_manha.setChecked(True)
    win.chk_tarde.setChecked(True)
    win.chk_noite.setChecked(True)
    
    # Configura dias ativos (apenas Segunda e Terça para simplificar)
    for chk in win.dias_chks:
        chk.setChecked(chk.text() in ["Segunda", "Terça"])
        
    # Capacidade de 10 clientes por dia
    win.spin_capacidade.setValue(10)
    
    # Executa otimização
    win.processar_roteirizacao()
    
    df = win.df_processado
    print("\nResultado da Distribuição:")
    for day, grp in df.groupby('dia_semana'):
        print(f"Dia: {day} (Total: {len(grp)} clientes)")
        for shift, sub in grp.groupby('turno'):
            print(f"  Turno {shift}: {len(sub)} clientes | Clientes: {sub['nome'].tolist()}")

if __name__ == "__main__":
    test_validation()

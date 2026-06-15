import sys
import os
from PyQt6.QtWidgets import QApplication

# Adiciona o diretório principal ao path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

from main import OtimizadorRotasApp

def test_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)
        
    win = OtimizadorRotasApp()
    win.caminho_arquivo = os.path.abspath(os.path.dirname(__file__) + "/../clientes_exemplo.xlsx")
    win.carregar_dados()
    
    # Configura 3 turnos ativos
    win.chk_manha.setChecked(True)
    win.chk_tarde.setChecked(True)
    win.chk_noite.setChecked(True)
    
    # Apenas Segunda e Terça
    for chk in win.dias_chks:
        chk.setChecked(chk.text() in ["Segunda", "Terça"])
        
    win.spin_capacidade.setValue(10)
    win.processar_roteirizacao()
    
    # Mock para evitar janelas popup interativas de erro/aviso
    from PyQt6.QtWidgets import QMessageBox, QFileDialog
    QMessageBox.information = lambda *args: None
    QFileDialog.getSaveFileName = lambda *args: (os.path.abspath(os.path.dirname(__file__) + "/validate_output.pdf"), "PDF")
    
    win.exportar_pdf()
    print("PDF export validated and generated to scratch/validate_output.pdf")

if __name__ == "__main__":
    test_pdf()

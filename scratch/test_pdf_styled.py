import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize

def generate_test_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    writer = QPdfWriter("test_styled.pdf")
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))

    doc = QTextDocument()
    
    html_content = """
    <html>
    <head>
        <style>
            body {
                font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
                color: #333333;
                margin: 20px;
            }
            .header {
                background-color: #2c3e50;
                color: #ffffff;
                padding: 15px;
                border-radius: 6px;
                margin-bottom: 25px;
            }
            .header h1 {
                margin: 0;
                font-size: 24px;
                font-weight: bold;
            }
            .header p {
                margin: 5px 0 0 0;
                font-size: 14px;
                color: #ecf0f1;
            }
            .day-section {
                margin-top: 20px;
            }
            .day-title {
                color: #2c3e50;
                font-size: 18px;
                border-bottom: 2px solid #3498db;
                padding-bottom: 5px;
                margin-bottom: 15px;
                text-transform: uppercase;
                font-weight: bold;
            }
            .shift-section {
                margin-bottom: 20px;
                padding-left: 10px;
            }
            .shift-title {
                color: #2980b9;
                font-size: 14px;
                font-weight: bold;
                margin-bottom: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-bottom: 15px;
            }
            th {
                background-color: #34495e;
                color: #ffffff;
                font-weight: bold;
                text-align: left;
                padding: 8px;
                font-size: 12px;
                border: 1px solid #34495e;
            }
            td {
                padding: 8px;
                font-size: 11px;
                border: 1px solid #bdc3c7;
            }
            .alt-row {
                background-color: #f8f9fa;
            }
            .text-center {
                text-align: center;
            }
            .page-break {
                page-break-before: always;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>MaxRotas - Relatório de Rotas</h1>
            <p>Gerado em: 15/06/2026 - Roteamento Inteligente</p>
        </div>

        <div class="day-section">
            <div class="day-title">Segunda-feira</div>
            <div class="shift-section">
                <div class="shift-title">Turno: Manhã</div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 10%;">Ordem</th>
                            <th style="width: 30%;">Cliente</th>
                            <th style="width: 45%;">Endereço</th>
                            <th style="width: 15%;">Grupo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-center">1</td>
                            <td>Padaria Santo Antônio</td>
                            <td>Rua das Flores, 123</td>
                            <td>Padaria</td>
                        </tr>
                        <tr class="alt-row">
                            <td class="text-center">2</td>
                            <td>Mercado Silva</td>
                            <td>Av. Principal, 456</td>
                            <td>Mercado</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>

        <div class="page-break"></div>

        <div class="day-section">
            <div class="day-title">Terça-feira</div>
            <div class="shift-section">
                <div class="shift-title">Turno: Tarde</div>
                <table>
                    <thead>
                        <tr>
                            <th style="width: 10%;">Ordem</th>
                            <th style="width: 30%;">Cliente</th>
                            <th style="width: 45%;">Endereço</th>
                            <th style="width: 15%;">Grupo</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="text-center">1</td>
                            <td>Açougue Prime</td>
                            <td>Rua do Comércio, 789</td>
                            <td>Geral</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    doc.setHtml(html_content)
    doc.print(writer)
    print("Styled PDF written successfully to test_styled.pdf")

if __name__ == "__main__":
    generate_test_pdf()

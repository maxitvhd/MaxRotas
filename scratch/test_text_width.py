import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize

def generate_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    writer = QPdfWriter("test_text_width.pdf")
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    # Vamos usar a resolucao padrao (alta qualidade) para ver se funciona bem
    writer.setResolution(300)

    doc = QTextDocument()
    
    # Define o textWidth com base na largura do dispositivo de impressao
    # O QPdfWriter em 300 DPI tem largura de ~2480 pixels
    # Vamos descontar as margens (ex: 200 pixels de cada lado)
    margem = 150
    doc.setTextWidth(writer.width() - 2 * margem)

    html_content = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #2c3e50;
            }
            h1 {
                font-size: 20pt;
                color: #2c3e50;
                border-bottom: 2pt solid #3498db;
                padding-bottom: 5pt;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15pt;
            }
            th {
                background-color: #34495e;
                color: white;
                font-size: 11pt;
                padding: 8pt;
                border: 1px solid #34495e;
                text-align: left;
            }
            td {
                font-size: 10pt;
                padding: 8pt;
                border: 1px solid #bdc3c7;
            }
        </style>
    </head>
    <body>
        <h1>Text Width Test: 300 DPI</h1>
        <p>This table should span the entire page width properly because we set doc.setTextWidth.</p>
        <table>
            <thead>
                <tr>
                    <th style="width: 20%;">Column 1</th>
                    <th style="width: 80%;">Column 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Key 1</td>
                    <td>Value 1 - this is a longer description that should wrap properly within the table.</td>
                </tr>
                <tr>
                    <td>Key 2</td>
                    <td>Value 2 - another description.</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    doc.setHtml(html_content)
    doc.print(writer)
    print("PDF written to test_text_width.pdf")

if __name__ == "__main__":
    generate_pdf()

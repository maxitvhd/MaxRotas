import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize
from PyQt6.QtCore import QSizeF

def generate_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    writer = QPdfWriter("test_order.pdf")
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setResolution(150)

    doc = QTextDocument()
    
    html_content = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #2c3e50;
                margin: 0;
            }
            h1 {
                font-size: 20pt;
                color: #2c3e50;
                border-bottom: 2pt solid #3498db;
                padding-bottom: 5pt;
                margin-bottom: 10pt;
            }
            table {
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
            .page-break {
                page-break-before: always;
            }
        </style>
    </head>
    <body>
        <h1>Page 1 Layout</h1>
        <table width="100%">
            <thead>
                <tr>
                    <th width="30%">Col 1</th>
                    <th width="70%">Col 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Key 1</td>
                    <td>Value 1</td>
                </tr>
            </tbody>
        </table>
        
        <div class="page-break"></div>
        
        <h1>Page 2 Layout</h1>
        <table width="100%">
            <thead>
                <tr>
                    <th width="30%">Col A</th>
                    <th width="70%">Col B</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Key A</td>
                    <td>Value B</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    
    # 1. Definir o HTML primeiro
    doc.setHtml(html_content)
    
    # 2. Definir o tamanho e largura do layout depois
    margem = 50
    doc.setTextWidth(writer.width() - 2 * margem)
    doc.setPageSize(QSizeF(writer.width(), writer.height()))
    
    doc.print(writer)
    print("PDF written to test_order.pdf")

if __name__ == "__main__":
    generate_pdf()

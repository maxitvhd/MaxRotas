import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize
from PyQt6.QtCore import QSizeF

def generate_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    writer = QPdfWriter("test_96dpi.pdf")
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    # 96 DPI faz 1 pixel da Qt bater com 1 pixel de CSS perfeitamente!
    writer.setResolution(96)

    doc = QTextDocument()
    
    # Margem de 0.5 polegadas (48 pixels a 96 DPI)
    margem = 48
    # Configura a largura do texto para preencher a pagina
    doc.setTextWidth(writer.width() - 2 * margem)

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
                font-size: 18pt;
                color: #2c3e50;
                border-bottom: 2pt solid #3498db;
                padding-bottom: 5pt;
                margin-bottom: 10pt;
            }
            p {
                font-size: 11pt;
                margin-bottom: 10pt;
            }
            th {
                background-color: #34495e;
                color: white;
                font-size: 11pt;
                padding: 6pt;
                border: 1px solid #34495e;
                text-align: left;
            }
            td {
                font-size: 10pt;
                padding: 6pt;
                border: 1px solid #bdc3c7;
            }
            .page-break {
                page-break-before: always;
            }
        </style>
    </head>
    <body>
        <h1>Page 1: 96 DPI Layout</h1>
        <p>This layout is designed at 96 DPI. The table below should span the entire page width.</p>
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
                    <td>Value 1 - this is a description that should wrap correctly and be easy to read.</td>
                </tr>
            </tbody>
        </table>
        
        <div class="page-break"></div>
        
        <h1>Page 2: 96 DPI Layout</h1>
        <p>This is the second page, which should also look wide and normal, without collapsing.</p>
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
                    <td>Value B - another description.</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    doc.setHtml(html_content)
    doc.print(writer)
    print("PDF written to test_96dpi.pdf")

if __name__ == "__main__":
    generate_pdf()

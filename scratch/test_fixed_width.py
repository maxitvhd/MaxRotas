import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize
from PyQt6.QtCore import QSizeF

def generate_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    writer = QPdfWriter("test_fixed_width.pdf")
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setResolution(150) # Use 150 DPI

    doc = QTextDocument()
    
    # Define o textWidth com base na largura da página em pixels do dispositivo
    # QPdfWriter em 150 DPI tem largura de ~1240 pixels (A4)
    margem = 50
    doc.setTextWidth(writer.width() - 2 * margem)
    doc.setPageSize(QSizeF(writer.width(), writer.height()))

    # Usando width="100%" diretamente na tag table, e pt para fontes!
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
            p {
                font-size: 11pt;
                margin-bottom: 10pt;
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
        <h1>Layout Test: Fixed width="100%"</h1>
        <p>This table should span the entire page width properly because we used width="100%" on the table tag.</p>
        <table width="100%">
            <thead>
                <tr>
                    <th width="20%">Column 1</th>
                    <th width="80%">Column 2</th>
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
    print("PDF written to test_fixed_width.pdf")

if __name__ == "__main__":
    generate_pdf()

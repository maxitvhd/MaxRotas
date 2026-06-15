import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize
from PyQt6.QtCore import QSizeF

def generate_pdf():
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    writer = QPdfWriter("test_layout.pdf")
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setResolution(150) # 150 DPI is great for document print layout

    doc = QTextDocument()
    
    # Configure document page size to match device size in pixels
    doc.setPageSize(QSizeF(writer.width(), writer.height()))

    html_content = """
    <html>
    <head>
        <style>
            body {
                font-family: Arial, sans-serif;
                color: #2c3e50;
                margin: 20pt;
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
        <h1>Layout Test: 150 DPI with setPageSize</h1>
        <p>This paragraph and the table below should span the entire page width properly.</p>
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
    print("PDF written to test_layout.pdf")

if __name__ == "__main__":
    generate_pdf()

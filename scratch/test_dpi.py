import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QTextDocument, QPdfWriter, QPageSize

def test_dpi(dpi):
    app = QApplication.instance()
    if not app:
        app = QApplication(sys.argv)

    filename = f"test_dpi_{dpi}.pdf"
    writer = QPdfWriter(filename)
    writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    writer.setResolution(dpi)

    doc = QTextDocument()
    # Definir tamanho do texto em pontos para ser independente de resolucao, ou usar CSS simples
    html_content = f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                color: #2c3e50;
                margin: 20px;
            }}
            h1 {{
                font-size: 20pt;
                color: #2c3e50;
            }}
            p {{
                font-size: 11pt;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
            }}
            th {{
                background-color: #34495e;
                color: white;
                font-size: 11pt;
                padding: 8px;
                border: 1px solid #34495e;
            }}
            td {{
                font-size: 10pt;
                padding: 8px;
                border: 1px solid #bdc3c7;
            }}
        </style>
    </head>
    <body>
        <h1>DPI Test: {dpi}</h1>
        <p>This is a paragraph at resolution {dpi} DPI.</p>
        <table>
            <thead>
                <tr>
                    <th>Col 1</th>
                    <th>Col 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Data 1</td>
                    <td>Data 2</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """
    doc.setHtml(html_content)
    doc.print(writer)
    print(f"PDF written for DPI {dpi} to {filename}")

if __name__ == "__main__":
    test_dpi(96)
    test_dpi(300)

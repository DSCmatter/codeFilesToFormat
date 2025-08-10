import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from bs4 import BeautifulSoup

# Get the script's own directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Register Calibri font
try:
    pdfmetrics.registerFont(TTFont("Calibri", "calibri.ttf"))
except:
    print("Warning: Calibri font not found. Using default font.")

# Extensions to include
EXTENSIONS = {".py", ".c", ".h", ".yaml", ".yml", ".cpp", ".java", ".txt"}

# Styles
styles = getSampleStyleSheet()
styles["Heading3"].fontName = "Calibri"
styles["Heading3"].fontSize = 12

code_style = ParagraphStyle(
    "Code",
    fontName="Calibri",
    fontSize=8,
    leading=10,
    spaceAfter=6,
)

def html_to_paragraphs(html_code):
    """Convert syntax-highlighted HTML into Paragraphs."""
    soup = BeautifulSoup(html_code, "html.parser")
    paragraphs = []
    for line in soup.get_text().split("\n"):
        line = line.replace(" ", "&nbsp;")
        paragraphs.append(Paragraph(line, code_style))
    return paragraphs

def process_file(file_path):
    try:
        code = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Skipping {file_path} (read error: {e})")
        return []

    try:
        lexer = guess_lexer_for_filename(file_path, code)
    except ClassNotFound:
        print(f"Skipping {file_path} (no lexer found)")
        return []

    formatter = HtmlFormatter(nowrap=True)
    highlighted_html = highlight(code, lexer, formatter)
    return html_to_paragraphs(highlighted_html)

def generate_pdfs(source_dir, mode):
    output_dir = os.path.join(SCRIPT_DIR, "pdf_output")
    os.makedirs(output_dir, exist_ok=True)

    if mode == "single":
        output_file = os.path.join(output_dir, "all_code_files.pdf")
        doc = SimpleDocTemplate(output_file, pagesize=A4)
        story = []
        for root, _, files in os.walk(source_dir):
            for file in sorted(files):
                if Path(file).suffix.lower() in EXTENSIONS:
                    file_path = os.path.join(root, file)
                    story.append(Paragraph(f"<b>{file_path}</b>", styles["Heading3"]))
                    story.append(Spacer(1, 0.2 * inch))
                    story.extend(process_file(file_path))
                    story.append(PageBreak())
        doc.build(story)
        messagebox.showinfo("Success", f"PDF created: {output_file}")

    else:  # separate PDFs
        for root, _, files in os.walk(source_dir):
            for file in sorted(files):
                if Path(file).suffix.lower() in EXTENSIONS:
                    file_path = os.path.join(root, file)
                    output_file = os.path.join(output_dir, Path(file).stem + ".pdf")
                    doc = SimpleDocTemplate(output_file, pagesize=A4)
                    story = [
                        Paragraph(f"<b>{file_path}</b>", styles["Heading3"]),
                        Spacer(1, 0.2 * inch),
                    ]
                    story.extend(process_file(file_path))
                    doc.build(story)
        messagebox.showinfo("Success", f"Separate PDFs created in: {output_dir}")

# GUI
def browse_folder():
    folder_selected = filedialog.askdirectory(title="Select folder containing code files")
    folder_path.set(folder_selected)

def start_conversion():
    folder = folder_path.get()
    mode = "single" if choice.get() == 1 else "separate"
    generate_pdfs(folder, mode)

root = tk.Tk()
root.title("Code to PDF Converter")

folder_path = tk.StringVar()
choice = tk.IntVar(value=1)

tk.Label(root, text="Select folder:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
tk.Entry(root, textvariable=folder_path, width=40).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_folder).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="PDF Output Mode:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
tk.Radiobutton(root, text="Single PDF", variable=choice, value=1).grid(row=1, column=1, sticky="w")
tk.Radiobutton(root, text="Separate PDFs", variable=choice, value=2).grid(row=2, column=1, sticky="w")

tk.Button(root, text="Convert to PDF", command=start_conversion, bg="lightblue").grid(row=3, column=0, columnspan=3, pady=10)

root.mainloop()

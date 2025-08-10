import os
import subprocess
from pathlib import Path
from tkinter import Tk, filedialog, ttk, Button, Label, StringVar, BooleanVar, Checkbutton
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from pygments import highlight
from pygments.lexers import guess_lexer_for_filename
from pygments.util import ClassNotFound
from bs4 import BeautifulSoup

# Register Calibri font for PDF (fallback if missing)
try:
    pdfmetrics.registerFont(TTFont("Calibri", "calibri.ttf"))
except:
    print("Calibri font file not found. Using default font.")

EXTENSIONS = {".py", ".c", ".h", ".yaml", ".yml", ".cpp", ".java", ".txt", ".json"}

styles = getSampleStyleSheet()
styles["Heading3"].fontName = "Calibri"
styles["Heading3"].fontSize = 12

code_style_pdf = ParagraphStyle(
    "Code",
    fontName="Calibri",
    fontSize=8,
    leading=10,
    spaceAfter=6,
)


# ---------- Code Formatting ----------
def format_code(file_path):
    ext = Path(file_path).suffix.lower()
    try:
        if ext == ".py":
            subprocess.run(["black", "--quiet", file_path], check=True)
        elif ext in {".c", ".h", ".cpp"}:
            subprocess.run(["clang-format", "-i", file_path], check=True)
        elif ext in {".yaml", ".yml", ".json"}:
            subprocess.run(["prettier", "--write", file_path], check=True)
    except FileNotFoundError:
        print(f"Formatter not installed for {file_path}. Skipping.")
    except Exception as e:
        print(f"Could not format {file_path}: {e}")


# ---------- File Reading ----------
def get_code(file_path):
    try:
        code = Path(file_path).read_text(encoding="utf-8")
    except Exception as e:
        print(f"Skipping {file_path} (read error: {e})")
        return None
    return code


# ---------- Export Functions ----------
def pdf_from_files(file_list, output_file):
    doc = SimpleDocTemplate(output_file, pagesize=A4)
    story = []
    for f in file_list:
        code = get_code(f)
        if code is None:
            continue
        story.append(Paragraph(f"<b>{f}</b>", styles["Heading3"]))
        story.append(Spacer(1, 0.2 * inch))
        for line in code.split("\n"):
            story.append(Paragraph(line.replace(" ", "&nbsp;"), code_style_pdf))
        story.append(PageBreak())
    doc.build(story)


def txt_from_files(file_list, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        for f in file_list:
            code = get_code(f)
            if code:
                out.write(f"## {f} ##\n")
                out.write(code + "\n\n")


# ---------- Main Process ----------
def process_folder(folder, mode, fmt, beautify):
    output_dir = Path(__file__).parent / f"{fmt.lower()}_output"
    output_dir.mkdir(exist_ok=True)

    file_list = []
    for root, _, files in os.walk(folder):
        for file in sorted(files):
            if Path(file).suffix.lower() in EXTENSIONS:
                full_path = os.path.join(root, file)
                if beautify:
                    format_code(full_path)
                file_list.append(full_path)

    if mode == "Single":
        out_file = output_dir / f"all_code.{fmt.lower()}"
        export_single(file_list, out_file, fmt)
    else:
        for f in file_list:
            out_file = output_dir / f"{Path(f).stem}.{fmt.lower()}"
            export_single([f], out_file, fmt)


def export_single(files, out_file, fmt):
    if fmt == "PDF":
        pdf_from_files(files, str(out_file))
    elif fmt == "TXT":
        txt_from_files(files, str(out_file))


# ---------- GUI ----------
def run_gui():
    root = Tk()
    root.title("Code Exporter")

    folder_var = StringVar()
    mode_var = StringVar(value="Single")
    fmt_var = StringVar(value="PDF")
    beautify_var = BooleanVar(value=True)  # default on

    def browse_folder():
        folder = filedialog.askdirectory(title="Select folder containing code files")
        if folder:
            folder_var.set(folder)

    def start_process():
        if not folder_var.get():
            print("No folder selected.")
            return
        process_folder(folder_var.get(), mode_var.get(), fmt_var.get(), beautify_var.get())
        print(f"Export complete: {fmt_var.get()} in {mode_var.get()} mode.")

    Label(root, text="Folder:").grid(row=0, column=0, sticky="w")
    Button(root, text="Browse", command=browse_folder).grid(row=0, column=1, sticky="ew")
    Label(root, textvariable=folder_var, wraplength=300).grid(row=1, column=0, columnspan=2, sticky="w")

    Label(root, text="Mode:").grid(row=2, column=0, sticky="w")
    mode_menu = ttk.Combobox(root, textvariable=mode_var, values=["Single", "Separate"], state="readonly")
    mode_menu.grid(row=2, column=1, sticky="ew")

    Label(root, text="Format:").grid(row=3, column=0, sticky="w")
    fmt_menu = ttk.Combobox(root, textvariable=fmt_var, values=["PDF", "TXT"], state="readonly")
    fmt_menu.grid(row=3, column=1, sticky="ew")

    Checkbutton(root, text="Beautify before export", variable=beautify_var).grid(row=4, column=0, columnspan=2, sticky="w")

    Button(root, text="Convert", command=start_process).grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()


if __name__ == "__main__":
    run_gui()

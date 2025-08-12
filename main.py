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
    root.geometry("450x320")
    root.resizable(False, False)
    
    # Center window on screen
    root.eval('tk::PlaceWindow . center')
    
    # Configure colors and theme
    bg_color = "#f0f0f0"
    accent_color = "#3498db"  # Blue
    text_color = "#2c3e50"    # Dark blue
    root.configure(bg=bg_color)
    
    # Variables
    folder_var = StringVar()
    mode_var = StringVar(value="Single")
    fmt_var = StringVar(value="PDF")
    beautify_var = BooleanVar(value=True)
    status_var = StringVar(value="Ready to start")
    
    # ttk Style
    style = ttk.Style()
    style.theme_use("clam")
    
    # Configure custom styles
    style.configure("TFrame", background=bg_color)
    style.configure("TButton", font=("Segoe UI", 10), background=accent_color, foreground="white")
    style.configure("AccentButton.TButton", font=("Segoe UI Bold", 11), background=accent_color)
    style.configure("TLabel", font=("Segoe UI", 10), background=bg_color, foreground=text_color)
    style.configure("Header.TLabel", font=("Segoe UI Bold", 14), background=bg_color, foreground=accent_color)
    style.configure("TCheckbutton", font=("Segoe UI", 10), background=bg_color, foreground=text_color)
    style.configure("TCombobox", font=("Segoe UI", 10))
    style.map("TButton", background=[('active', '#2980b9')])
    
    # Main frame with border and shadow
    main_frame = ttk.Frame(root, padding=20, style="TFrame")
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Functions
    def browse_folder():
        folder = filedialog.askdirectory(title="Select folder containing code files")
        if folder:
            folder_var.set(folder)
            status_var.set(f"Selected folder: {Path(folder).name}")
    
    def start_process():
        if not folder_var.get():
            status_var.set("⚠️ Error: No folder selected")
            return
        status_var.set("⏳ Processing files...")
        root.update()
        process_folder(folder_var.get(), mode_var.get(), fmt_var.get(), beautify_var.get())
        status_var.set(f"✅ Export complete: {fmt_var.get()} in {mode_var.get()} mode")
    
    # Title
    ttk.Label(main_frame, text="Code Exporter", style="Header.TLabel").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))
    
    # Widgets with better spacing and alignment
    ttk.Label(main_frame, text="Code folder:", style="TLabel").grid(row=1, column=0, sticky="w")
    ttk.Button(main_frame, text="Browse", command=browse_folder).grid(row=1, column=1, sticky="e", padx=(10, 0))
    
    folder_display = ttk.Label(main_frame, textvariable=folder_var, wraplength=380)
    folder_display.grid(row=2, column=0, columnspan=2, sticky="w", pady=(5, 15))
    
    ttk.Label(main_frame, text="Export mode:", style="TLabel").grid(row=3, column=0, sticky="w")
    mode_combo = ttk.Combobox(main_frame, textvariable=mode_var, values=["Single", "Separate"], state="readonly", width=15)
    mode_combo.grid(row=3, column=1, sticky="e", padx=(10, 0), pady=(5, 0))
    
    ttk.Label(main_frame, text="Output format:", style="TLabel").grid(row=4, column=0, sticky="w", pady=(15, 0))
    fmt_combo = ttk.Combobox(main_frame, textvariable=fmt_var, values=["PDF", "TXT"], state="readonly", width=15)
    fmt_combo.grid(row=4, column=1, sticky="e", padx=(10, 0), pady=(15, 0))
    
    beautify_check = ttk.Checkbutton(main_frame, text="Beautify code before export", variable=beautify_var)
    beautify_check.grid(row=5, column=0, columnspan=2, sticky="w", pady=(15, 0))
    
    # Main action button with accent style
    convert_button = ttk.Button(main_frame, text="Convert", command=start_process, style="AccentButton.TButton")
    convert_button.grid(row=6, column=0, columnspan=2, pady=(20, 10))
    
    # Status bar
    status_bar = ttk.Label(main_frame, textvariable=status_var, font=("Segoe UI", 9), foreground="#7f8c8d")
    status_bar.grid(row=7, column=0, columnspan=2, sticky="w", pady=(5, 0))
    
    root.mainloop()


if __name__ == "__main__":
    run_gui()

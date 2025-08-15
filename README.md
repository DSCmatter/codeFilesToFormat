# codeFilesToFormat

A simple Python GUI tool to export code files from a selected folder into a single PDF or TXT file, so you don't have to. Supports optional auto-formatting with **Black**, **clang-format**, and **Prettier** before exporting.

## Features

* Select any folder containing code files
* Supported extensions: `.py`, `.c`, `.h`, `.yaml`, `.yml`, `.cpp`, `.java`, `.txt`
* Choose between **Single File** (all code in one PDF/TXT) or **Separate Files** (each file exported individually)
* Output generated in a dedicated folder (`pdf_output` or `txt_output`)
* Optional code formatting before export

## Installation

Clone the repository:

```bash
git clone https://github.com/DSCmatter/codeFilesToFormatr.git
cd codeFilesToFormat
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

If you want code formatting:

* Install [Black](https://black.readthedocs.io/en/stable/) for Python formatting
* Install [clang-format](https://clang.llvm.org/docs/ClangFormat.html) for C/C++ formatting
* Install [Prettier](https://prettier.io/) for YAML/JSON formatting

## Usage

Run the script:

```bash
python main.py
```

1. Browse and select the folder containing your code
2. Choose **Mode**:

   * `Single` → all code in one file
   * `Separate` → each file exported separately
3. Choose **Format** (`PDF` or `TXT`)
4. Click **Convert**
5. Your files will be saved in `pdf_output` or `txt_output` next to the script

## Notes

* The script tries to use the `Calibri` font for PDF output. If missing, it falls back to default fonts.
* Large folders may take time to process depending on formatting and file sizes.

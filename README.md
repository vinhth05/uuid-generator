# UUID Generator Pro

A production-grade, highly performant Desktop Application for generating UUIDs.
Built with Python and CustomTkinter.

## Features
- Generate UUID v1, v3, v4, v5
- Bulk generate up to millions of UUIDs without freezing the UI (multithreading & queue)
- Virtualized Textbox for lazy rendering of massive datasets
- Export to TXT and CSV
- Beautiful Dark/Light mode theme
- Copy to clipboard
- Local History tracking

## Installation

1. Clone or download this repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Building the Executable

Run the build script to compile a single `.exe` file using PyInstaller:
```bash
python build_script.py
```
The executable will be located in the `dist/` folder.

## Testing

Run tests with `pytest`:
```bash
pytest tests/
```

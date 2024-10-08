# MATX Text Editor

A cross-platform text editor implemented in Python, supporting both Windows and Linux. This project is in early development, ideal for those who want to contribute and improve it!

## Features

- Create new files
- Open existing files
- Save files
- Native UI for Windows and Linux
- Syntax highlighting
- Multiple tabs support
- Undo and Redo functionality

## Requirements

### Common Requirements
- Python 3.8+
- Pygments

### Linux Requirements
- GTK 3.0
- PyGObject
- GtkSourceView 3.0

### Windows Requirements
- pywin32

## Installation

### Linux Installation
1. Clone the repository
2. Install the required packages:
- pip install -r requirements.txt
3. Install system dependencies:
   - For Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-gtksource-3.0
     ```
   - For Arch Linux:
     ```bash
     sudo pacman -S python-gobject gtk3 gtksourceview3
     ```
   - For other distributions, please refer to your package manager

## Windows Installation
1. Clone the repository
2. Install Python 3.8+ from the official Python website (https://www.python.org/downloads/)
3. Open a command prompt and navigate to the project directory
4. Install the required packages:
   ```bash
   pip install -r requirements.txt
5. pip install pywin32

## Usage
Run `python src/main.py` from the project root directory.

## Development
To contribute to the MATX Text Editor:
1. Fork the repository
2. Create a new branch for your feature
3. Implement your changes
4. Submit a pull request

## License
This project is licensed under the GPL-3.0 license. See the LICENSE file for details.

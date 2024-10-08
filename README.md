# MATX Text Editor

A cross-platform text editor implemented in Python, supporting both Windows and Linux.

## Features
- Create new files
- Open existing files
- Save files
- Native UI for Windows and Linux
- Syntax highlighting
- Multiple tabs support
- Undo and Redo functionality

## Requirements
- Python 3.8+
- GTK 3.0
- PyGObject
- Pygments
- GtkSourceView 3.0

## Linux Installation
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
Coming Soon

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

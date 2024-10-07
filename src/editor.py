import sys
import os
from pygments import highlight
from pygments.lexers import get_lexer_for_filename
from pygments.formatters import HtmlFormatter
from utils.file_operations import get_file_path, read_file, write_file
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GtkSource', '3.0')
from gi.repository import Gtk, GtkSource

if sys.platform.startswith('win'):
    from ui.windows_ui import WindowsUI
elif sys.platform.startswith('linux'):
    from ui.linux_ui import LinuxUI

class Editor:
    def __init__(self):
        self.content = ""
        if sys.platform.startswith('win'):
            self.ui = WindowsUI(self)
        elif sys.platform.startswith('linux'):
            self.ui = LinuxUI(self)
        else:
            raise NotImplementedError("Unsupported platform")

        # Open a new tab by default
        self.new_file()

    def new_file(self):
        self.content = ""
        self.ui.add_tab("Untitled", self.content)

    def open_file(self):
        file_path = get_file_path('open')
        if file_path:
            content = read_file(file_path)
            textbuffer, new_page_index = self.ui.add_tab(file_path, content)
            self.apply_syntax_highlighting(file_path, textbuffer)
            self.ui.notebook.set_current_page(new_page_index)

    def save_file(self):
        file_path = get_file_path('save')
        if file_path:
            current_page = self.ui.notebook.get_current_page()
            if current_page != -1:
                textview = self.ui.notebook.get_nth_page(current_page).get_child()
                textbuffer = textview.get_buffer()
                start_iter = textbuffer.get_start_iter()
                end_iter = textbuffer.get_end_iter()
                content = textbuffer.get_text(start_iter, end_iter, True)
                write_file(file_path, content)
                
                # Update the tab label with the new file name
                tab_label = Gtk.Label(label=os.path.basename(file_path))
                self.ui.notebook.set_tab_label(self.ui.notebook.get_nth_page(current_page), tab_label)

    def apply_syntax_highlighting(self, file_path, buffer):
        language_manager = GtkSource.LanguageManager()
        language = language_manager.guess_language(file_path, None)
        
        buffer.set_language(language)
        buffer.set_highlight_syntax(True)
        
        with open(file_path, 'r') as file:
            content = file.read()
            
        buffer.set_text(content)

    def exit(self):
        Gtk.main_quit()

    def run(self):
        self.ui.run()

if __name__ == "__main__":
    editor = Editor()
    editor.run()

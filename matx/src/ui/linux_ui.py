import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class LinuxUI(Gtk.Window):
    def __init__(self, editor):
        logger.debug("Initializing LinuxUI")
        Gtk.Window.__init__(self, title="Matx Editor")
        self.editor = editor
        self.set_default_size(500, 400)

        logger.debug("Setting up main layout")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        logger.debug("Adding buttons")
        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, False, False, 0)

        new_button = Gtk.Button(label="New")
        new_button.connect("clicked", self.on_new_clicked)
        hbox.pack_start(new_button, False, False, 0)

        open_button = Gtk.Button(label="Open")
        open_button.connect("clicked", self.on_open_clicked)
        hbox.pack_start(open_button, False, False, 0)

        save_button = Gtk.Button(label="Save")
        save_button.connect("clicked", self.on_save_clicked)
        hbox.pack_start(save_button, False, False, 0)

        undo_button = Gtk.Button(label="Undo")
        undo_button.connect("clicked", self.on_undo_clicked)
        hbox.pack_start(undo_button, False, False, 0)

        redo_button = Gtk.Button(label="Redo")
        redo_button.connect("clicked", self.on_redo_clicked)
        hbox.pack_start(redo_button, False, False, 0)

        exit_button = Gtk.Button(label="Exit")
        exit_button.connect("clicked", self.on_exit_clicked)
        hbox.pack_start(exit_button, False, False, 0)

        logger.debug("Setting up notebook")
        self.notebook = Gtk.Notebook()
        vbox.pack_start(self.notebook, True, True, 0)

    def add_tab(self, file_path, content=""):
        logger.debug(f"Adding new tab for {file_path}")
        scrolled_window = Gtk.ScrolledWindow()
        textview = Gtk.TextView()
        textview.set_editable(True)
        textview.set_cursor_visible(True)
        textbuffer = textview.get_buffer()
        textbuffer.set_text(content)
        scrolled_window.add(textview)
        
        tab_label = Gtk.Label(label=os.path.basename(file_path))
        new_page_index = self.notebook.append_page(scrolled_window, tab_label)
        self.notebook.set_current_page(new_page_index)
        self.show_all()
        
        return textbuffer, new_page_index



    def on_new_clicked(self, widget):
        logger.debug("New button clicked")
        self.editor.new_file()

    def on_open_clicked(self, widget):
        logger.debug("Open button clicked")
        self.editor.open_file()

    def on_save_clicked(self, widget):
        logger.debug("Save button clicked")
        self.editor.save_file()

    def on_undo_clicked(self, widget):
        logger.debug("Undo button clicked")
        current_page = self.notebook.get_current_page()
        if current_page != -1:
            textview = self.notebook.get_nth_page(current_page).get_child()
            textbuffer = textview.get_buffer()
            if textbuffer.can_undo():
                textbuffer.undo()

    def on_redo_clicked(self, widget):
        logger.debug("Redo button clicked")
        current_page = self.notebook.get_current_page()
        if current_page != -1:
            textview = self.notebook.get_nth_page(current_page).get_child()
            textbuffer = textview.get_buffer()
            if textbuffer.can_redo():
                textbuffer.redo()

    def on_exit_clicked(self, widget):
        logger.debug("Exit button clicked")
        self.quit()

    def update_content(self, content):
        logger.debug("Updating content")
        current_page = self.notebook.get_current_page()
        if current_page != -1:
            textview = self.notebook.get_nth_page(current_page).get_child()
            textbuffer = textview.get_buffer()
            textbuffer.set_text(content)

    def run(self):
        logger.debug("Running LinuxUI")
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    logger.debug("Starting application directly from linux_ui.py")
    ui = LinuxUI(None)
    ui.run()

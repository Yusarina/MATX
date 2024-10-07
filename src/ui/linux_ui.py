import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio, Pango
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class UndoRedoStack:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        self.current_text = ""
        self.change_count = 0
        self.max_stack_size = 64

    def push(self, text):
        if text != self.current_text:
            self.change_count += 1
            if self.change_count >= 5:
                logger.debug(f"Pushing text: {text[:20]}...")
                self.undo_stack.append(self.current_text)
                if len(self.undo_stack) > self.max_stack_size:
                    self.undo_stack.pop(0)
                self.current_text = text
                self.redo_stack.clear()
                self.change_count = 0
                logger.debug(f"Undo stack size: {len(self.undo_stack)}, Redo stack size: {len(self.redo_stack)}")

    def undo(self):
        if self.undo_stack:
            logger.debug("Performing undo")
            self.redo_stack.append(self.current_text)
            if len(self.redo_stack) > self.max_stack_size:
                self.redo_stack.pop(0)
            self.current_text = self.undo_stack.pop()
            self.change_count = 0
            logger.debug(f"Undo stack size: {len(self.undo_stack)}, Redo stack size: {len(self.redo_stack)}")
            return self.current_text
        logger.debug("No undo available")
        return None

    def redo(self):
        if self.redo_stack:
            logger.debug("Performing redo")
            self.undo_stack.append(self.current_text)
            if len(self.undo_stack) > self.max_stack_size:
                self.undo_stack.pop(0)
            self.current_text = self.redo_stack.pop()
            self.change_count = 0
            logger.debug(f"Undo stack size: {len(self.undo_stack)}, Redo stack size: {len(self.redo_stack)}")
            return self.current_text
        logger.debug("No redo available")
        return None

class LinuxUI(Gtk.Window):
    def __init__(self, editor):
        logger.debug("Initializing LinuxUI")
        Gtk.Window.__init__(self, title="Matx Editor")
        self.editor = editor
        self.set_default_size(500, 400)
        self.set_size_request(500, 400)
        self.ignore_text_change = False

        logger.debug("Setting up main layout")
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.add(vbox)

        logger.debug("Adding buttons")
        hbox = Gtk.Box(spacing=6)
        vbox.pack_start(hbox, False, False, 0)

        self.connect("delete-event", self.on_delete_event)

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
        self.notebook.set_scrollable(True)
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
        
        undo_redo_stack = UndoRedoStack()
        undo_redo_stack.push(content)
        textview.undo_redo_stack = undo_redo_stack

        textbuffer.connect("changed", self.on_text_changed, textview)
        
        tab_label = Gtk.Label(label=os.path.basename(file_path))
        tab_label.set_width_chars(15)
        tab_label.set_ellipsize(Pango.EllipsizeMode.END)
        
        new_page_index = self.notebook.append_page(scrolled_window, tab_label)
        self.notebook.set_current_page(new_page_index)
        
        self.notebook.set_tab_reorderable(scrolled_window, True)
        self.notebook.child_set_property(scrolled_window, "tab-expand", False)
        self.notebook.child_set_property(scrolled_window, "tab-fill", False)
        scrolled_window.file_path = file_path
        
        self.show_all()

        return textbuffer, new_page_index

    def on_text_changed(self, textbuffer, textview):
        if self.ignore_text_change:
            return
        start_iter = textbuffer.get_start_iter()
        end_iter = textbuffer.get_end_iter()
        text = textbuffer.get_text(start_iter, end_iter, True)
        logger.debug(f"Text changed: {text[:20]}...")
        textview.undo_redo_stack.push(text)

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
            text = textview.undo_redo_stack.undo()
            if text is not None:
                logger.debug(f"Undoing to: {text[:20]}...")
                self.ignore_text_change = True
                textbuffer.set_text(text)
                textbuffer.place_cursor(textbuffer.get_end_iter())
                self.ignore_text_change = False
            else:
                logger.debug("No undo performed")

    def on_redo_clicked(self, widget):
        logger.debug("Redo button clicked")
        current_page = self.notebook.get_current_page()
        if current_page != -1:
            textview = self.notebook.get_nth_page(current_page).get_child()
            textbuffer = textview.get_buffer()
            text = textview.undo_redo_stack.redo()
            if text is not None:
                logger.debug(f"Redoing to: {text[:20]}...")
                self.ignore_text_change = True
                textbuffer.set_text(text)
                textbuffer.place_cursor(textbuffer.get_end_iter())
                self.ignore_text_change = False
            else:
                logger.debug("No redo performed")

    def on_exit_clicked(self, widget):
        logger.debug("Exit button clicked")
        Gtk.main_quit()

    def update_content(self, content):
        logger.debug("Updating content")
        current_page = self.notebook.get_current_page()
        if current_page != -1:
            textview = self.notebook.get_nth_page(current_page).get_child()
            textbuffer = textview.get_buffer()
            textbuffer.set_text(content)

    def on_delete_event(self, widget, event):
        logger.debug("Window close button (X) clicked")
        Gtk.main_quit()
        return False

    def run(self):
        logger.debug("Running LinuxUI")
        self.show_all()
        Gtk.main()

if __name__ == "__main__":
    logger.debug("Starting application directly from linux_ui.py")
    ui = LinuxUI(None)
    ui.run()

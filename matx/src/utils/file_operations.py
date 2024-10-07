import os
import sys
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gio

def get_file_path(action, initial_dir=None):
    dialog = Gtk.FileChooserNative.new(
        "Open File" if action == 'open' else "Save File",
        None,
        Gtk.FileChooserAction.OPEN if action == 'open' else Gtk.FileChooserAction.SAVE,
        "_Open" if action == 'open' else "_Save",
        "_Cancel"
    )
    if initial_dir:
        dialog.set_current_folder(Gio.File.new_for_path(initial_dir))
    
    response = dialog.run()
    if response == Gtk.ResponseType.ACCEPT:
        file_path = dialog.get_file().get_path()
        dialog.destroy()
        return file_path
    dialog.destroy()
    return None

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def write_file(file_path, content):
    with open(file_path, 'w') as file:
        file.write(content)

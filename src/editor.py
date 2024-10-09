import wx
from utils.file_operations import get_file_path, read_file, write_file
from ui.wx_ui import WXUI

class Editor:
    def __init__(self):
        print("Initializing wx.App")
        self.app = wx.App()
        self.ui = WXUI(self)
        self.app.SetTopWindow(self.ui)
        print("wx.App initialized")

        # Add menu items for find and replace
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_FIND, "&Find\tCtrl+F")
        edit_menu.Append(wx.ID_REPLACE, "&Replace\tCtrl+H")
        
        menu_bar = wx.MenuBar()
        menu_bar.Append(edit_menu, "&Edit")
        self.ui.SetMenuBar(menu_bar)

    def new_file(self):
        print("Creating new file")
        wx.CallAfter(self.ui.add_tab, "Untitled", "")

    def open_file(self):
        print("Opening file")
        file_path = get_file_path('open')
        if file_path:
            content = read_file(file_path)
            self.ui.add_tab(file_path, content)

    def save_file(self):
        print("Saving file")
        file_path = get_file_path('save')
        if file_path:
            content = self.ui.get_current_content()
            write_file(file_path, content)
            wx.CallAfter(self.ui.update_current_tab_name, file_path)

    def undo(self):
        print("Undoing last action")
        self.ui.on_undo(None)

    def redo(self):
        print("Redoing last undone action")
        self.ui.on_redo(None)

    def find(self):
        print("Finding text")
        self.ui.on_find(None)

    def replace(self):
        print("Replacing text")
        self.ui.on_replace(None)

    def run(self):
        print("Running editor")
        self.ui.Show()
        self.app.MainLoop()

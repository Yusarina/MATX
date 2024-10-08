import wx
import wx.stc as stc
from utils.file_operations import get_file_path, read_file
import os

class WXUI(wx.Frame):
    UNDO_LIMIT = 64 
    UNDO_CHUNK_SIZE = 12

    def __init__(self, editor):
        super().__init__(parent=None, title="MATX Editor")
        self.editor = editor
        self.SetSize(800, 600)
        self.undo_stack = []
        self.redo_stack = []
        self.current_chunk = ""
        self.current_chunk_start = 0
        
        # Create main panel and sizer
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        # Create toolbar
        toolbar = wx.ToolBar(panel)
        new_tool = toolbar.AddTool(wx.ID_NEW, "New", wx.ArtProvider.GetBitmap(wx.ART_NEW))
        open_tool = toolbar.AddTool(wx.ID_OPEN, "Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN))
        save_tool = toolbar.AddTool(wx.ID_SAVE, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE))
        toolbar.AddSeparator()
        undo_tool = toolbar.AddTool(wx.ID_UNDO, "Undo", wx.ArtProvider.GetBitmap(wx.ART_UNDO))
        redo_tool = toolbar.AddTool(wx.ID_REDO, "Redo", wx.ArtProvider.GetBitmap(wx.ART_REDO))
        toolbar.Realize()
        sizer.Add(toolbar, 0, wx.EXPAND)

        # Create notebook for tabs
        self.notebook = wx.Notebook(panel)
        sizer.Add(self.notebook, 1, wx.EXPAND)

        panel.SetSizer(sizer)

        # Bind events
        self.Bind(wx.EVT_TOOL, self.on_new, new_tool)
        self.Bind(wx.EVT_TOOL, self.on_open, open_tool)
        self.Bind(wx.EVT_TOOL, self.on_save, save_tool)
        self.Bind(wx.EVT_TOOL, self.on_undo, undo_tool)
        self.Bind(wx.EVT_TOOL, self.on_redo, redo_tool)

    def add_tab(self, file_path, content):
        text_ctrl = stc.StyledTextCtrl(self.notebook)
        text_ctrl.SetText(content)
        
        # Set a darker background color
        text_ctrl.SetBackgroundColour(wx.Colour(30, 30, 30))  # Dark gray

        # Set the lexer and styles
        text_ctrl.SetLexer(stc.STC_LEX_PYTHON)
        text_ctrl.StyleSetSpec(stc.STC_STYLE_DEFAULT, "face:Courier New,size:10,back:#1E1E1E,fore:#FFFFFF")
        text_ctrl.StyleClearAll()
        
        # Set margin for line numbers
        text_ctrl.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        text_ctrl.SetMarginWidth(1, 30)

        # Enable undo functionality
        text_ctrl.SetUndoCollection(True)
        text_ctrl.EmptyUndoBuffer()

        # Bind Ctrl+Z and Ctrl+Y to custom undo/redo
        text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

        # Bind the text change event
        text_ctrl.Bind(wx.stc.EVT_STC_MODIFIED, self.on_text_modified)

        self.notebook.AddPage(text_ctrl, os.path.basename(file_path))
        self.notebook.SetSelection(self.notebook.GetPageCount() - 1)

    def get_current_content(self):
        current_page = self.notebook.GetSelection()
        if current_page != -1:
            return self.notebook.GetPage(current_page).GetText()
        return ""

    def update_current_tab_name(self, file_path):
        current_page = self.notebook.GetSelection()
        if current_page != -1:
            self.notebook.SetPageText(current_page, os.path.basename(file_path))

    def on_new(self, event):
        self.editor.new_file()

    def on_open(self, event):
        file_path = get_file_path('open')
        if file_path:
            content = read_file(file_path)
            wx.CallAfter(self.add_tab, file_path, content)

    def on_save(self, event):
        self.editor.save_file()

    def on_text_modified(self, event):
        if event.GetModificationType() & (wx.stc.STC_MOD_INSERTTEXT | wx.stc.STC_MOD_DELETETEXT):
            text_ctrl = event.GetEventObject()
            pos = event.GetPosition()
            length = event.GetLength()
            
            if event.GetModificationType() & wx.stc.STC_MOD_INSERTTEXT:
                text = text_ctrl.GetTextRange(pos, pos + length)
                action = ('insert', pos, text)
            else:  # Delete text
                text = text_ctrl.GetTextRange(pos, pos + length)
                action = ('delete', pos, text)
            
            self.undo_stack.append(action)
            if len(self.undo_stack) > self.UNDO_LIMIT:
                self.undo_stack.pop(0)
            self.redo_stack.clear()
            
            print(f"Debug: Modified at position {pos}, length {length}, action: {action}")

    def on_undo(self, event):
        if self.undo_stack:
            action = self.undo_stack.pop()
            text_ctrl = self.notebook.GetCurrentPage()
            
            if action[0] == 'insert':
                text_ctrl.SetTargetStart(action[1])
                text_ctrl.SetTargetEnd(action[1] + len(action[2]))
                text_ctrl.ReplaceTarget("")
            else:  # 'delete'
                text_ctrl.SetTargetStart(action[1])
                text_ctrl.SetTargetEnd(action[1])
                text_ctrl.ReplaceTarget(action[2])
            
            self.redo_stack.append(action)
            print(f"Debug: Undoing action: {action}")

    def on_redo(self, event):
        if self.redo_stack:
            action = self.redo_stack.pop()
            text_ctrl = self.notebook.GetCurrentPage()
            
            if action[0] == 'insert':
                text_ctrl.SetTargetStart(action[1])
                text_ctrl.SetTargetEnd(action[1])
                text_ctrl.ReplaceTarget(action[2])
            else:  # 'delete'
                text_ctrl.SetTargetStart(action[1])
                text_ctrl.SetTargetEnd(action[1] + len(action[2]))
                text_ctrl.ReplaceTarget("")
            
            self.undo_stack.append(action)
            print(f"Debug: Redoing action: {action}")


    def on_key_down(self, event):
        if event.GetKeyCode() == ord('Z') and event.ControlDown():
            self.on_undo(event)
        elif event.GetKeyCode() == ord('Y') and event.ControlDown():
            self.on_redo(event)
        else:
            event.Skip()

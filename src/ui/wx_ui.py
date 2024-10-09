import wx
import wx.stc as stc
from utils.file_operations import get_file_path, read_file
import os

class WXUI(wx.Frame):
    UNDO_LIMIT = 64 
    UNDO_CHUNK_SIZE = 12

    def __init__(self, editor):
        super().__init__(parent=None, title="MATX Editor", style=wx.DEFAULT_FRAME_STYLE)
        self.editor = editor
        self.SetSize(800, 600)
        self.undo_stack = []
        self.redo_stack = []
        self.current_chunk = ""
        self.current_chunk_start = 0
        
        panel = wx.Panel(self)
        sizer = wx.BoxSizer(wx.VERTICAL)

        toolbar = wx.ToolBar(panel, style=wx.TB_FLAT | wx.TB_HORIZONTAL)
        toolbar.SetBackgroundColour(wx.Colour(45, 45, 45))

        icon_path = os.path.join(os.path.dirname(__file__), "icons")
        icon_size = (24, 24)

        new_bmp = wx.Bitmap(os.path.join(icon_path, "new.png"))
        new_bmp = new_bmp.ConvertToImage().Scale(*icon_size).ConvertToBitmap()
        new_tool = toolbar.AddTool(wx.ID_NEW, "New", new_bmp)

        open_bmp = wx.Bitmap(os.path.join(icon_path, "open.png"))
        open_bmp = open_bmp.ConvertToImage().Scale(*icon_size).ConvertToBitmap()
        open_tool = toolbar.AddTool(wx.ID_OPEN, "Open", open_bmp)

        save_bmp = wx.Bitmap(os.path.join(icon_path, "save.png"))
        save_bmp = save_bmp.ConvertToImage().Scale(*icon_size).ConvertToBitmap()
        save_tool = toolbar.AddTool(wx.ID_SAVE, "Save", save_bmp)

        toolbar.AddSeparator()

        undo_bmp = wx.Bitmap(os.path.join(icon_path, "undo.png"))
        undo_bmp = undo_bmp.ConvertToImage().Scale(*icon_size).ConvertToBitmap()
        undo_tool = toolbar.AddTool(wx.ID_UNDO, "Undo", undo_bmp)

        redo_bmp = wx.Bitmap(os.path.join(icon_path, "redo.png"))
        redo_bmp = redo_bmp.ConvertToImage().Scale(*icon_size).ConvertToBitmap()
        redo_tool = toolbar.AddTool(wx.ID_REDO, "Redo", redo_bmp)

        toolbar.Realize()
        sizer.Add(toolbar, 0, wx.EXPAND)

        self.notebook = wx.Notebook(panel)
        sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 5)

        panel.SetSizer(sizer)

        self.Bind(wx.EVT_TOOL, self.on_new, new_tool)
        self.Bind(wx.EVT_TOOL, self.on_open, open_tool)
        self.Bind(wx.EVT_TOOL, self.on_save, save_tool)
        self.Bind(wx.EVT_TOOL, self.on_undo, undo_tool)
        self.Bind(wx.EVT_TOOL, self.on_redo, redo_tool)

        self.apply_dark_theme()

    def apply_dark_theme(self):
        dark_bg = wx.Colour(30, 30, 30)
        dark_fg = wx.Colour(200, 200, 200)
        
        self.SetBackgroundColour(dark_bg)
        self.SetForegroundColour(dark_fg)
        
        for child in self.GetChildren():
            child.SetBackgroundColour(dark_bg)
            child.SetForegroundColour(dark_fg)
        
        self.notebook.Bind(wx.EVT_PAINT, self.on_notebook_paint)

    def on_notebook_paint(self, event):
        dc = wx.PaintDC(self.notebook)
        dc.SetBackground(wx.Brush(wx.Colour(30, 30, 30)))
        dc.Clear()
        
        font = dc.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.SetTextForeground(wx.Colour(200, 200, 200))
        
        for i in range(self.notebook.GetPageCount()):
            rect = self.notebook.GetPageRect(i)
            if i == self.notebook.GetSelection():
                dc.SetBrush(wx.Brush(wx.Colour(60, 60, 60)))
            else:
                dc.SetBrush(wx.Brush(wx.Colour(45, 45, 45)))
            dc.SetPen(wx.Pen(wx.Colour(70, 70, 70)))
            dc.DrawRectangle(rect)
            dc.DrawText(self.notebook.GetPageText(i), rect.x + 5, rect.y + 5)
        
        event.Skip()

    def add_tab(self, file_path, content):
        text_ctrl = stc.StyledTextCtrl(self.notebook)
        text_ctrl.SetText(content)
        
        dark_bg = wx.Colour(30, 30, 30)
        light_text = wx.Colour(212, 212, 212)
        
        text_ctrl.StyleSetSpec(stc.STC_STYLE_DEFAULT, f"face:Consolas,size:10,back:{dark_bg.GetAsString(wx.C2S_HTML_SYNTAX)},fore:{light_text.GetAsString(wx.C2S_HTML_SYNTAX)}")
        text_ctrl.StyleClearAll()
        text_ctrl.SetLexer(stc.STC_LEX_PYTHON)
        
        text_ctrl.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        text_ctrl.SetMarginWidth(1, 30)
        text_ctrl.StyleSetSpec(stc.STC_STYLE_LINENUMBER, f"back:#252526,fore:#858585")

        text_ctrl.SetUndoCollection(True)
        text_ctrl.EmptyUndoBuffer()

        text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
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

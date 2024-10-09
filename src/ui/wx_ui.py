import wx
import wx.stc as stc
from utils.file_operations import get_file_path, read_file
import os
import re
import keyword

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
        self.create_status_bar()
        self.Bind(wx.EVT_MENU, self.on_find, id=wx.ID_FIND)
        self.Bind(wx.EVT_MENU, self.on_replace, id=wx.ID_REPLACE)
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.on_tab_change)

    def apply_dark_theme(self):
        dark_bg = wx.Colour(30, 30, 30)
        dark_fg = wx.Colour(200, 200, 200)
        
        self.SetBackgroundColour(dark_bg)
        self.SetForegroundColour(dark_fg)
        
        for child in self.GetChildren():
            if not isinstance(child, stc.StyledTextCtrl):
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
        text_ctrl.SetReadOnly(False)
        
        lexer = self.set_lexer(text_ctrl, file_path)
        self.set_style(text_ctrl, lexer)
        
        text_ctrl.SetText(content)
        text_ctrl.Colourise(0, -1)
        
        text_ctrl.lexer = lexer
        
        text_ctrl.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        text_ctrl.SetMarginWidth(1, 30)

        text_ctrl.SetUndoCollection(True)
        text_ctrl.EmptyUndoBuffer()

        text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        text_ctrl.Bind(wx.stc.EVT_STC_MODIFIED, self.on_text_modified)
        text_ctrl.Bind(wx.stc.EVT_STC_UPDATEUI, self.on_update_ui)

        self.notebook.AddPage(text_ctrl, os.path.basename(file_path))
        self.notebook.SetSelection(self.notebook.GetPageCount() - 1)
        
        print(f"Debug: Tab added for {file_path} with lexer {lexer}")

    def set_lexer(self, text_ctrl, file_path):
        file_extension = file_path.split('.')[-1].lower() if '.' in file_path else ''
        lexer = stc.STC_LEX_NULL  # Default to plain text

        if file_extension in ['py', 'pyw']:
            lexer = stc.STC_LEX_PYTHON
        elif file_extension in ['cpp', 'cxx', 'h', 'hpp']:
            lexer = stc.STC_LEX_CPP
        elif file_extension == 'html':
            lexer = stc.STC_LEX_HTML
        elif file_extension == 'css':
            lexer = stc.STC_LEX_CSS

        text_ctrl.SetLexer(lexer)
        print(f"Setting lexer for {file_path}: {lexer}")
        return lexer

    def add_tab(self, file_path, content):
        text_ctrl = stc.StyledTextCtrl(self.notebook)
        text_ctrl.SetReadOnly(False)  # Ensure it's not read-only
        
        lexer = self.set_lexer(text_ctrl, file_path)
        self.set_style(text_ctrl, lexer)
        
        text_ctrl.SetText(content)
        text_ctrl.Colourise(0, -1)
        
        text_ctrl.lexer = lexer
        
        dark_bg = wx.Colour(30, 30, 30)
        light_text = wx.Colour(212, 212, 212)
        
        text_ctrl.StyleSetSpec(stc.STC_STYLE_DEFAULT, f"face:Consolas,size:10,back:{dark_bg.GetAsString(wx.C2S_HTML_SYNTAX)},fore:{light_text.GetAsString(wx.C2S_HTML_SYNTAX)}")
        text_ctrl.StyleClearAll()
        
        text_ctrl.SetMarginType(1, stc.STC_MARGIN_NUMBER)
        text_ctrl.SetMarginWidth(1, 30)
        text_ctrl.StyleSetSpec(stc.STC_STYLE_LINENUMBER, f"back:#252526,fore:#858585")

        text_ctrl.SetUndoCollection(True)
        text_ctrl.EmptyUndoBuffer()

        text_ctrl.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        text_ctrl.Bind(wx.stc.EVT_STC_MODIFIED, self.on_text_modified)
        text_ctrl.Bind(wx.stc.EVT_STC_UPDATEUI, self.on_update_ui)

        self.notebook.AddPage(text_ctrl, os.path.basename(file_path))
        self.notebook.SetSelection(self.notebook.GetPageCount() - 1)
        
        print(f"Debug: Tab added for {file_path} with lexer {lexer}")
        text_ctrl.Colourise(0, -1) 

    def set_style(self, text_ctrl, lexer):
        print(f"Debug: Setting style for lexer {lexer}")
        default_bg = wx.Colour(30, 30, 30)
        default_fg = wx.Colour(212, 212, 212)
        text_ctrl.StyleSetForeground(stc.STC_STYLE_DEFAULT, default_fg)
        text_ctrl.StyleSetBackground(stc.STC_STYLE_DEFAULT, default_bg)
        text_ctrl.StyleClearAll()

        if lexer == stc.STC_LEX_PYTHON:
            print("Debug: Applying Python styles")
            text_ctrl.SetKeyWords(0, " ".join(keyword.kwlist))
            self.set_style_color(text_ctrl, stc.STC_P_DEFAULT, "#D4D4D4", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_COMMENTLINE, "#6A9955", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_NUMBER, "#B5CEA8", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_STRING, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_CHARACTER, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_WORD, "#569CD6", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_TRIPLE, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_TRIPLEDOUBLE, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_CLASSNAME, "#4EC9B0", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_DEFNAME, "#DCDCAA", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_OPERATOR, "#D4D4D4", default_bg)
            self.set_style_color(text_ctrl, stc.STC_P_IDENTIFIER, "#D4D4D4", default_bg)
        elif lexer == stc.STC_LEX_CPP:
            print("Debug: Applying C++ styles")
            self.set_style_color(text_ctrl, stc.STC_C_DEFAULT, "#D4D4D4", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_COMMENT, "#6A9955", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_COMMENTLINE, "#6A9955", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_NUMBER, "#B5CEA8", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_STRING, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_CHARACTER, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_WORD, "#569CD6", default_bg)
            self.set_style_color(text_ctrl, stc.STC_C_OPERATOR, "#D4D4D4", default_bg)
        elif lexer == stc.STC_LEX_HTML:
            print("Debug: Applying HTML styles")
            self.set_style_color(text_ctrl, stc.STC_H_DEFAULT, "#D4D4D4", default_bg)
            self.set_style_color(text_ctrl, stc.STC_H_TAG, "#569CD6", default_bg)
            self.set_style_color(text_ctrl, stc.STC_H_TAGUNKNOWN, "#569CD6", default_bg)
            self.set_style_color(text_ctrl, stc.STC_H_ATTRIBUTE, "#9CDCFE", default_bg)
            self.set_style_color(text_ctrl, stc.STC_H_ATTRIBUTEUNKNOWN, "#9CDCFE", default_bg)
            self.set_style_color(text_ctrl, stc.STC_H_DOUBLESTRING, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_H_SINGLESTRING, "#CE9178", default_bg)
        elif lexer == stc.STC_LEX_CSS:
            print("Debug: Applying CSS styles")
            self.set_style_color(text_ctrl, stc.STC_CSS_DEFAULT, "#D4D4D4", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_TAG, "#D7BA7D", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_CLASS, "#D7BA7D", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_PSEUDOCLASS, "#D7BA7D", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_UNKNOWN_PSEUDOCLASS, "#D7BA7D", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_OPERATOR, "#D4D4D4", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_IDENTIFIER, "#9CDCFE", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_UNKNOWN_IDENTIFIER, "#9CDCFE", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_VALUE, "#CE9178", default_bg)
            self.set_style_color(text_ctrl, stc.STC_CSS_COMMENT, "#6A9955", default_bg)
        else:
            print(f"Debug: No specific styles for lexer {lexer}")

        text_ctrl.Colourise(0, -1)
        print("Debug: Styles applied and text colourised")

    def set_style_color(self, text_ctrl, style, fg, bg):
        text_ctrl.StyleSetForeground(style, wx.Colour(fg))
        text_ctrl.StyleSetBackground(style, bg) 

    def create_status_bar(self):
        self.status_bar = self.CreateStatusBar(3)
        self.status_bar.SetStatusWidths([-2, -1, -1])

    def on_update_ui(self, event):
        current_page = self.notebook.GetSelection()
        text_ctrl = self.notebook.GetPage(current_page)
        
        pos = text_ctrl.GetCurrentPos()
        line = text_ctrl.LineFromPosition(pos)
        col = text_ctrl.GetColumn(pos)
        
        status_text = f"Ln {line + 1}, Col {col + 1}"
        self.status_bar.SetStatusText(status_text, 0)
        
        self.status_bar.SetStatusText("UTF-8", 1)
        
        lexer = text_ctrl.GetLexer()
        lexer_name = self.get_lexer_name(lexer)
        print(f"Current tab lexer: {lexer}, Lexer name: {lexer_name}")
        self.status_bar.SetStatusText(lexer_name, 2)

    def refresh_status_bar(self):
        current_page = self.notebook.GetSelection()
        if current_page != -1:
            text_ctrl = self.notebook.GetPage(current_page)
            lexer = text_ctrl.GetLexer()
            lexer_name = self.get_lexer_name(lexer)
            self.status_bar.SetStatusText(lexer_name, 2)
            print(f"Refreshed status bar: {lexer_name}")
            text_ctrl.Colourise(0, -1)  

    def on_tab_change(self, event):
        self.refresh_status_bar()
        event.Skip()

    def get_lexer_name(self, lexer):
        if lexer == stc.STC_LEX_PYTHON:
            return "Python"
        elif lexer == stc.STC_LEX_CPP:
            return "C++"
        elif lexer == stc.STC_LEX_HTML:
            return "HTML"
        elif lexer == stc.STC_LEX_CSS:
            return "CSS"
        else:
            return "Plain Text"

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

    def on_find(self, event):
        text_ctrl = self.notebook.GetCurrentPage()
        find_data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self, find_data, "Find")
        dlg.Bind(wx.EVT_FIND, lambda evt: self.do_find(evt, text_ctrl))
        dlg.Show(True)

    def on_replace(self, event):
        text_ctrl = self.notebook.GetCurrentPage()
        find_data = wx.FindReplaceData()
        dlg = wx.FindReplaceDialog(self, find_data, "Replace", wx.FR_REPLACEDIALOG)
        dlg.Bind(wx.EVT_FIND, lambda evt: self.do_find(evt, text_ctrl))
        dlg.Bind(wx.EVT_FIND_REPLACE, lambda evt: self.do_replace(evt, text_ctrl))
        dlg.Bind(wx.EVT_FIND_REPLACE_ALL, lambda evt: self.do_replace_all(evt, text_ctrl))
        dlg.Show(True)

    def do_find(self, event, text_ctrl):
        find_string = event.GetFindString()
        flags = event.GetFlags()
        start = text_ctrl.GetSelectionEnd()
        end = text_ctrl.GetLength()
        
        text = text_ctrl.GetTextRange(start, end)
        if not (flags & wx.FR_MATCHCASE):
            text = text.lower()
            find_string = find_string.lower()
        
        if flags & wx.FR_WHOLEWORD:
            pattern = r'\b' + re.escape(find_string) + r'\b'
        else:
            pattern = re.escape(find_string)
        
        match = re.search(pattern, text)
        if match:
            text_ctrl.SetSelection(start + match.start(), start + match.end())
        else:
            wx.MessageBox("Text not found", "Find Result", wx.OK | wx.ICON_INFORMATION)

    def do_replace(self, event, text_ctrl):
        find_string = event.GetFindString()
        replace_string = event.GetReplaceString()
        flags = event.GetFlags()
        
        if text_ctrl.GetSelectedText().lower() == find_string.lower() or not (flags & wx.FR_MATCHCASE):
            text_ctrl.ReplaceSelection(replace_string)
        
        self.do_find(event, text_ctrl)

    def do_replace_all(self, event, text_ctrl):
        find_string = event.GetFindString()
        replace_string = event.GetReplaceString()
        flags = event.GetFlags()
        
        text = text_ctrl.GetText()
        if flags & wx.FR_WHOLEWORD:
            pattern = r'\b' + re.escape(find_string) + r'\b'
        else:
            pattern = re.escape(find_string)
        
        if flags & wx.FR_MATCHCASE:
            new_text, count = re.subn(pattern, replace_string, text)
        else:
            new_text, count = re.subn(pattern, replace_string, text, flags=re.IGNORECASE)
        
        if count > 0:
            text_ctrl.SetText(new_text)
            wx.MessageBox(f"Replaced {count} occurrences", "Replace All Result", wx.OK | wx.ICON_INFORMATION)
        else:
            wx.MessageBox("No occurrences found", "Replace All Result", wx.OK | wx.ICON_INFORMATION)

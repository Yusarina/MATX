import sys
import ctypes
import ctypes.wintypes

if sys.platform.startswith('win'):
    from ctypes import windll
else:
    windll = None

class WindowsUI:
    def __init__(self, editor):
        self.editor = editor
        self.setup_ui()

def setup_ui(self):
    WS_OVERLAPPEDWINDOW = 0xcf0000
    WS_VISIBLE = 0x10000000
    
    def window_proc(hwnd, msg, wparam, lparam):
        if msg == 2:  # WM_DESTROY
            windll.user32.PostQuitMessage(0)
            return 0
        if msg == 273:  # WM_COMMAND
            if wparam == 1:  # New
                self.editor.new_file()
            elif wparam == 2:  # Open
                self.editor.open_file()
            elif wparam == 3:  # Save
                self.editor.save_file()
            elif wparam == 4:  # Exit
                windll.user32.DestroyWindow(hwnd)
        return windll.user32.DefWindowProcW(hwnd, msg, wparam, lparam)

    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int, HWND, UINT, ctypes.wintypes.WPARAM, ctypes.wintypes.LPARAM)
    wc = ctypes.wintypes.WNDCLASS()
    wc.lpfnWndProc = WNDPROC(window_proc)
    wc.lpszClassName = "EditorClass"
    
    windll.user32.RegisterClassW(ctypes.byref(wc))
    hwnd = windll.user32.CreateWindowExW(
        0, wc.lpszClassName, "Simple Editor",
        WS_OVERLAPPEDWINDOW | WS_VISIBLE,
        100, 100, 500, 400, 0, 0, 0, 0
    )
    
    # Create buttons
    windll.user32.CreateWindowExW(
        0, "BUTTON", "New", WS_VISIBLE | 0x50000000,
        10, 10, 50, 30, hwnd, 1, 0, 0
    )
    windll.user32.CreateWindowExW(
        0, "BUTTON", "Open", WS_VISIBLE | 0x50000000,
        70, 10, 50, 30, hwnd, 2, 0, 0
    )
    windll.user32.CreateWindowExW(
        0, "BUTTON", "Save", WS_VISIBLE | 0x50000000,
        130, 10, 50, 30, hwnd, 3, 0, 0
    )
    windll.user32.CreateWindowExW(
        0, "BUTTON", "Exit", WS_VISIBLE | 0x50000000,
        190, 10, 50, 30, hwnd, 4, 0, 0
    )
    
    # Create text area
    self.text_area = windll.user32.CreateWindowExW(
        0, "EDIT", "", WS_VISIBLE | 0x50810000,
        10, 50, 480, 340, hwnd, 0, 0, 0
    )


    def run(self):
        msg = ctypes.wintypes.MSG()
        while windll.user32.GetMessageW(ctypes.byref(msg), 0, 0, 0) != 0:
            windll.user32.TranslateMessage(ctypes.byref(msg))
            windll.user32.DispatchMessageW(ctypes.byref(msg))

    def update_content(self, content):
        # Update the text area with new content
        windll.user32.SetWindowTextW(self.text_area, content)

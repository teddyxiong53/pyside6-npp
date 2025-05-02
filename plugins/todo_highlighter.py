from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter
from PySide6.QtWidgets import QDockWidget, QListWidget, QListWidgetItem

class TodoHighlighterPlugin:
    """TODO和FIXME高亮及任务列表插件"""
    
    def __init__(self, editor):
        self.editor = editor
        # self.highlighter = TodoHighlighter(self.editor.document()) # Removed: Highlighter logic moved to main SyntaxHighlighter
        self.todo_dock = None
        self.todo_list = None
        self.setup_todo_panel()
        
        # 连接文档变更信号
        self.editor.document().contentsChanged.connect(self.update_todo_list)
        
    def setup_todo_panel(self):
        """设置TODO面板"""
        # 获取主窗口实例
        main_window = None
        parent = self.editor.parent()
        while parent:
            if isinstance(parent, QMainWindow):
                main_window = parent
                break
            parent = parent.parent()
            
        if main_window:
            self.todo_dock = QDockWidget("TODO List", main_window)
            self.todo_list = QListWidget()
            self.todo_dock.setWidget(self.todo_list)
            main_window.addDockWidget(Qt.RightDockWidgetArea, self.todo_dock)
            
            # 只有在成功创建todo_list后才连接信号和更新列表
            self.todo_list.itemClicked.connect(self.goto_todo_item)
            self.update_todo_list()
        
    def update_todo_list(self):
        """更新TODO列表"""
        if self.todo_list is None:
            return
            
        self.todo_list.clear()
        text = self.editor.toPlainText()
        lines = text.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            # 查找TODO和FIXME
            if 'TODO:' in line or 'FIXME:' in line:
                item = QListWidgetItem(f"Line {line_num}: {line.strip()}")
                item.setData(Qt.UserRole, line_num)
                self.todo_list.addItem(item)
                
    def goto_todo_item(self, item):
        """跳转到TODO项所在行"""
        line_num = item.data(Qt.UserRole)
        cursor = self.editor.textCursor()
        cursor.movePosition(cursor.Start)
        for _ in range(line_num - 1):
            cursor.movePosition(cursor.NextBlock)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        
# Removed TodoHighlighter class as its logic is integrated into the main SyntaxHighlighter
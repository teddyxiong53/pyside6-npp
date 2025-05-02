from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCharFormat, QColor, QSyntaxHighlighter
from PySide6.QtWidgets import QDockWidget, QListWidget, QListWidgetItem

class TodoHighlighterPlugin:
    """TODO和FIXME高亮及任务列表插件"""
    
    def __init__(self, editor):
        self.editor = editor
        self.highlighter = TodoHighlighter(self.editor.document())
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
        

class TodoHighlighter(QSyntaxHighlighter):
    """TODO和FIXME语法高亮器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.todo_format = QTextCharFormat()
        self.todo_format.setForeground(QColor("#FF8C00"))  # 深橙色
        self.todo_format.setFontWeight(700)
        
        self.fixme_format = QTextCharFormat()
        self.fixme_format.setForeground(QColor("#FF4500"))  # 红橙色
        self.fixme_format.setFontWeight(700)
        
    def highlightBlock(self, text):
        """高亮TODO和FIXME"""
        # 高亮TODO
        index = text.find('TODO:')
        while index >= 0:
            # 确保TODO前面是注释符号
            if index == 0 or text[index-1].isspace():
                # 查找行尾或下一个标点符号
                end = text.find('.', index)
                if end == -1:
                    end = len(text)
                self.setFormat(index, end - index, self.todo_format)
            index = text.find('TODO:', index + 1)
            
        # 高亮FIXME
        index = text.find('FIXME:')
        while index >= 0:
            # 确保FIXME前面是注释符号
            if index == 0 or text[index-1].isspace():
                # 查找行尾或下一个标点符号
                end = text.find('.', index)
                if end == -1:
                    end = len(text)
                self.setFormat(index, end - index, self.fixme_format)
            index = text.find('FIXME:', index + 1)
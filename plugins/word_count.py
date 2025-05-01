from PySide6.QtWidgets import QMainWindow, QAction, QMessageBox
from PySide6.QtGui import QTextCursor
from plugins import Plugin

class WordCountPlugin(Plugin):
    """示例插件：统计文档中的字数"""
    
    @property
    def name(self) -> str:
        return "Word Count"
    
    @property
    def description(self) -> str:
        return "统计当前文档中的字数、行数和字符数"
    
    def initialize(self, window: QMainWindow) -> None:
        self.window = window
        
        # 创建菜单项
        tools_menu = window.menuBar().addMenu("工具")
        word_count_action = QAction("字数统计", window)
        word_count_action.triggered.connect(self.count_words)
        tools_menu.addAction(word_count_action)
    
    def cleanup(self) -> None:
        # 清理资源（如有需要）
        pass
    
    def count_words(self) -> None:
        """统计当前文档的字数"""
        editor = self.window.get_current_editor()
        if not editor:
            return
        
        text = editor.toPlainText()
        
        # 统计字符数（包括空格）
        char_count = len(text)
        
        # 统计行数
        line_count = len(text.splitlines()) or 1  # 至少有1行
        
        # 统计单词数（按空格分割）
        words = text.split()
        word_count = len(words)
        
        # 显示统计结果
        QMessageBox.information(
            self.window,
            "字数统计",
            f"字符数（含空格）：{char_count}\n"
            f"行数：{line_count}\n"
            f"单词数：{word_count}"
        )
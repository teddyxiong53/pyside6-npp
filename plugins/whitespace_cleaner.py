from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QStatusBar

class WhitespaceCleanerPlugin:
    """行尾空格清除器插件"""
    
    def __init__(self, editor):
        self.editor = editor
        self.status_bar = self.editor.window().statusBar()
        
        # 连接保存信号
        self.editor.window().save_file_as = self._wrap_save_file_as
        self.editor.window().save_file = self._wrap_save_file
        
    def _wrap_save_file(self):
        """包装保存文件函数"""
        # 清理空格
        removed_count = self.clean_trailing_whitespace()
        
        # 调用原始的保存函数
        result = self.editor.window().save_file()
        
        # 显示清理结果
        if removed_count > 0:
            self.status_bar.showMessage(f"已清理 {removed_count} 处行尾空格", 3000)
            
        return result
        
    def _wrap_save_file_as(self):
        """包装另存为函数"""
        # 清理空格
        removed_count = self.clean_trailing_whitespace()
        
        # 调用原始的另存为函数
        result = self.editor.window().save_file_as()
        
        # 显示清理结果
        if removed_count > 0:
            self.status_bar.showMessage(f"已清理 {removed_count} 处行尾空格", 3000)
            
        return result
        
    def clean_trailing_whitespace(self):
        """清理所有行尾空格"""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        # 保存当前光标位置
        original_position = cursor.position()
        
        # 移动到文档开始
        cursor.movePosition(QTextCursor.Start)
        removed_count = 0
        
        while not cursor.atEnd():
            # 移动到行尾
            cursor.movePosition(QTextCursor.EndOfLine)
            
            # 选择行尾空格
            cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
            while cursor.selectedText().endswith(' ') and not cursor.selectedText() == ' ':
                cursor.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor)
                
            # 如果选中了空格，删除它们
            if cursor.selectedText().endswith(' '):
                removed_count += len(cursor.selectedText())
                cursor.removeSelectedText()
                
            # 移动到下一行
            cursor.movePosition(QTextCursor.NextBlock)
            
        # 恢复光标位置
        cursor.setPosition(original_position)
        cursor.endEditBlock()
        
        return removed_count
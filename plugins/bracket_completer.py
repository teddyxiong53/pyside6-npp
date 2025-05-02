from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

class BracketCompleterPlugin:
    """括号自动补全和跳转插件"""
    
    def __init__(self, editor):
        self.editor = editor
        self.brackets = {
            '(': ')',
            '[': ']',
            '{': '}',
            '"': '"',
            "'": "'"
        }
        self.stack = []
        
        # 连接按键事件
        self.editor.keyPressEvent = self._wrap_key_press
        
    def _wrap_key_press(self, event):
        """包装原始的keyPressEvent以添加括号补全功能"""
        # 处理Ctrl+]跳转
        if event.key() == Qt.Key_BracketRight and event.modifiers() == Qt.ControlModifier:
            self.jump_to_matching_bracket()
            return
            
        # 获取当前光标
        cursor = self.editor.textCursor()
        char = event.text()
        
        # 处理左括号输入
        if char in self.brackets:
            # 如果选中了文本，将其包裹在括号中
            if cursor.hasSelection():
                start = cursor.selectionStart()
                end = cursor.selectionEnd()
                text = cursor.selectedText()
                cursor.beginEditBlock()
                cursor.setPosition(start)
                cursor.insertText(char)
                cursor.setPosition(end + 1)
                cursor.insertText(self.brackets[char])
                cursor.endEditBlock()
                event.accept()
                return
            else:
                # 自动插入右括号
                cursor.insertText(char + self.brackets[char])
                cursor.movePosition(QTextCursor.Left)
                self.editor.setTextCursor(cursor)
                event.accept()
                return
                
        # 处理右括号输入
        elif char in self.brackets.values():
            # 如果下一个字符就是右括号，直接移动光标
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor)
            if cursor.selectedText() == char:
                cursor.clearSelection()
                self.editor.setTextCursor(cursor)
                event.accept()
                return
                
        # 调用原始的keyPressEvent
        QPlainTextEdit.keyPressEvent(self.editor, event)
        
    def jump_to_matching_bracket(self):
        """跳转到匹配的括号"""
        cursor = self.editor.textCursor()
        pos = cursor.position()
        text = self.editor.toPlainText()
        
        # 获取当前字符
        if pos >= len(text):
            return
        char = text[pos]
        
        # 如果是右括号，向前查找匹配的左括号
        if char in self.brackets.values():
            stack = []
            for i in range(pos - 1, -1, -1):
                if text[i] in self.brackets.values():
                    stack.append(text[i])
                elif text[i] in self.brackets:
                    if not stack:
                        cursor.setPosition(i)
                        self.editor.setTextCursor(cursor)
                        return
                    if self.brackets[text[i]] == stack[-1]:
                        stack.pop()
                    else:
                        return
                        
        # 如果是左括号，向后查找匹配的右括号
        elif char in self.brackets:
            stack = []
            for i in range(pos + 1, len(text)):
                if text[i] in self.brackets:
                    stack.append(text[i])
                elif text[i] in self.brackets.values():
                    if not stack:
                        cursor.setPosition(i + 1)
                        self.editor.setTextCursor(cursor)
                        return
                    if self.brackets[stack[-1]] == text[i]:
                        stack.pop()
                    else:
                        return
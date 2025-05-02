from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import QPlainTextEdit

class CodeSnippetsPlugin:
    """代码片段模板插件"""
    
    def __init__(self, editor):
        self.editor = editor
        self.snippets = {
            'for': 'for (let i = 0; i < $1; i++) {\n    $0\n}',
            'if': 'if ($1) {\n    $0\n}',
            'while': 'while ($1) {\n    $0\n}',
            'func': 'function $1($2) {\n    $0\n}',
            'class': 'class $1 {\n    constructor($2) {\n        $0\n    }\n}',
            'try': 'try {\n    $1\n} catch (error) {\n    $0\n}',
            'log': 'console.log($0);',
            'div': '<div class="$1">\n    $0\n</div>',
            'html': '<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n    <title>$1</title>\n</head>\n<body>\n    $0\n</body>\n</html>'
        }
        
        # 连接按键事件
        self.editor.keyPressEvent = self._wrap_key_press
        self.current_snippet = None
        self.placeholder_positions = []
        self.current_placeholder = 0
        
    def _wrap_key_press(self, event):
        """包装原始的keyPressEvent以添加代码片段功能"""
        # 如果按下Tab键且有当前片段
        if event.key() == Qt.Key_Tab and self.current_snippet:
            # 跳转到下一个占位符
            if self.current_placeholder < len(self.placeholder_positions):
                cursor = self.editor.textCursor()
                pos = self.placeholder_positions[self.current_placeholder]
                cursor.setPosition(pos[0])
                cursor.setPosition(pos[1], QTextCursor.KeepAnchor)
                self.editor.setTextCursor(cursor)
                self.current_placeholder += 1
                event.accept()
                return
            else:
                # 完成片段插入
                self.current_snippet = None
                self.placeholder_positions = []
                self.current_placeholder = 0
                
        # 检查是否需要展开代码片段
        cursor = self.editor.textCursor()
        block = cursor.block().text()
        pos = cursor.positionInBlock()
        
        # 获取光标前的单词
        word = ''
        i = pos - 1
        while i >= 0 and block[i].isalnum():
            word = block[i] + word
            i -= 1
            
        # 如果按下空格键且单词是一个代码片段
        if event.key() == Qt.Key_Space and word in self.snippets:
            # 删除触发词
            for _ in range(len(word)):
                cursor.deletePreviousChar()
                
            # 插入代码片段
            snippet = self.snippets[word]
            self.insert_snippet(snippet)
            event.accept()
            return
            
        # 调用原始的keyPressEvent
        QPlainTextEdit.keyPressEvent(self.editor, event)
        
    def insert_snippet(self, snippet):
        """插入代码片段并设置占位符"""
        cursor = self.editor.textCursor()
        self.current_snippet = snippet
        self.placeholder_positions = []
        self.current_placeholder = 0
        
        # 查找所有占位符位置
        pos = 0
        while True:
            pos1 = snippet.find('$', pos)
            if pos1 == -1:
                break
                
            if pos1 + 1 < len(snippet) and snippet[pos1 + 1].isdigit():
                num_end = pos1 + 2
                while num_end < len(snippet) and snippet[num_end].isdigit():
                    num_end += 1
                placeholder_num = int(snippet[pos1 + 1:num_end])
                start_pos = cursor.position() + pos1
                self.placeholder_positions.append((start_pos, start_pos))
                snippet = snippet[:pos1] + snippet[num_end:]
                pos = pos1
            else:
                pos = pos1 + 1
                
        # 插入处理后的代码片段
        cursor.insertText(snippet)
        
        # 跳转到第一个占位符
        if self.placeholder_positions:
            pos = self.placeholder_positions[0]
            cursor.setPosition(pos[0])
            cursor.setPosition(pos[1], QTextCursor.KeepAnchor)
            self.editor.setTextCursor(cursor)
import sys
import os
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QTextEdit, QFileDialog, 
                               QMessageBox, QFontDialog, QColorDialog, 
                               QMenu, QToolBar, QTabWidget, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
                               QDialog, QCheckBox, QRadioButton, QButtonGroup, QGridLayout,
                               QStatusBar, QSplitter, QListWidget, QDockWidget, QListWidgetItem)
from PySide6.QtGui import (QFont, QFontMetrics, QTextCharFormat, QTextCursor, 
                         QKeySequence, QTextDocument, QColor, QSyntaxHighlighter, 
                         QTextFormat, QIcon, QAction, QPainter, QTextOption, QActionGroup)
from PySide6.QtCore import Qt, QRegularExpression, QSize, Signal, Slot, QSettings, QTimer, QFile

class FindReplaceDialog(QDialog):
    """Dialog for find and replace functionality"""
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings
        self.parent = parent
        self.setWindowTitle("Find/Replace")
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Find section
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel("Find:"))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        self.find_button = QPushButton("Find Next")
        self.find_button.clicked.connect(self.find_text)
        find_layout.addWidget(self.find_button)
        layout.addLayout(find_layout)
        
        # Replace section
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel("Replace with:"))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        self.replace_button = QPushButton("Replace")
        self.replace_button.clicked.connect(self.replace_text)
        replace_layout.addWidget(self.replace_button)
        layout.addLayout(replace_layout)
        
        # Replace All button
        self.replace_all_button = QPushButton("Replace All")
        self.replace_all_button.clicked.connect(self.replace_all)
        layout.addWidget(self.replace_all_button)
        
        # Options
        options_layout = QHBoxLayout()
        self.case_sensitive = QCheckBox("Match case")
        self.whole_word = QCheckBox("Whole word")
        options_layout.addWidget(self.case_sensitive)
        options_layout.addWidget(self.whole_word)
        layout.addLayout(options_layout)
        
        # Direction
        direction_layout = QHBoxLayout()
        direction_layout.addWidget(QLabel("Direction:"))
        self.direction_group = QButtonGroup()
        self.up_radio = QRadioButton("Up")
        self.down_radio = QRadioButton("Down")
        self.down_radio.setChecked(True)
        self.direction_group.addButton(self.up_radio)
        self.direction_group.addButton(self.down_radio)
        direction_layout.addWidget(self.up_radio)
        direction_layout.addWidget(self.down_radio)
        layout.addLayout(direction_layout)
        
        self.setLayout(layout)
        
    def find_text(self):
        text_to_find = self.find_input.text()
        if not text_to_find:
            return
        
        editor = self.parent.get_current_editor()
        if not editor:
            return
            
        # Get options
        flags = QTextDocument.FindFlags()
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextDocument.FindWholeWords
        if self.up_radio.isChecked():
            flags |= QTextDocument.FindBackward
            
        # Find the text
        found = editor.find(text_to_find, flags)
        if not found:
            QMessageBox.information(self, "Not Found", 
                                  f"Cannot find '{text_to_find}'")
    
    def replace_text(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        
        if not text_to_find:
            return
            
        editor = self.parent.get_current_editor()
        if not editor:
            return
            
        # Replace selected text if it matches
        cursor = editor.textCursor()
        if cursor.hasSelection() and cursor.selectedText() == text_to_find:
            cursor.insertText(replace_with)
            
        # Find the next occurrence
        self.find_text()
    
    def replace_all(self):
        text_to_find = self.find_input.text()
        replace_with = self.replace_input.text()
        
        if not text_to_find:
            return
            
        editor = self.parent.get_current_editor()
        if not editor:
            return
            
        # Start from the beginning
        cursor = editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        editor.setTextCursor(cursor)
        
        # Get options
        flags = QTextDocument.FindFlags()
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextDocument.FindWholeWords
            
        # Replace all occurrences
        count = 0
        while editor.find(text_to_find, flags):
            cursor = editor.textCursor()
            cursor.insertText(replace_with)
            count += 1
            
        QMessageBox.information(self, "Replace All", 
                              f"Replaced {count} occurrences")


class SyntaxHighlighter(QSyntaxHighlighter):
    """Basic syntax highlighter for programming languages"""
    
    # 文件扩展名到语言的映射
    EXTENSION_LANGUAGE_MAP = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.html': 'HTML',
        '.css': 'CSS',
        '.cpp': 'C++',
        '.h': 'C++',
        '.java': 'Java',
        '.txt': 'Plain Text'
    }
    
    @staticmethod
    def get_language_from_extension(file_path):
        """根据文件扩展名获取对应的编程语言"""
        if not file_path:
            return 'Plain Text'
        
        ext = os.path.splitext(file_path)[1].lower()
        return SyntaxHighlighter.EXTENSION_LANGUAGE_MAP.get(ext, 'Plain Text')

    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings
        self.highlighting_rules = []
        self.current_language = "Plain Text"
        
        # Define formats for different syntax elements
        self.formats = {}
        
        # 初始化各种语言的高亮规则
        self.init_highlighting_rules()
        
    def init_highlighting_rules(self):
        # 基本格式
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0000FF"))  # 更鲜明的蓝色
        keyword_format.setFontWeight(QFont.Bold)
        
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#A31515"))  # 更深的红色
        
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#008000"))  # 更鲜明的绿色
        
        # TODO format
        todo_format = QTextCharFormat()
        todo_format.setForeground(QColor("#FF0000"))  # 醒目的红色
        todo_format.setFontWeight(QFont.Bold)
        todo_format.setBackground(QColor("#FFFF00"))  # 黄色背景
        self.add_mapping(["\\bTODO:\s*.*$"], todo_format)
        
        # 语言特定的规则
        self.language_rules = {
            "Python": [
                (["\\b(def|class|import|from|as|if|elif|else|while|for|in|try|except|finally|with|return|yield|break|continue|pass|raise|True|False|None)\\b"], keyword_format),
                (["#[^\n]*"], comment_format),
                (["\".*?\"|'.*?'"], string_format)
            ],
            "JavaScript": [
                (["\\b(function|var|let|const|if|else|for|while|do|switch|case|break|continue|return|try|catch|finally|throw|typeof|instanceof|new|this|delete|void|in|of)\\b"], keyword_format),
                (["//[^\n]*|/\\*[^*]*\\*+(?:[^/*][^*]*\\*+)*/"], comment_format),
                (["\".*?\"|'.*?'|`.*?`"], string_format)
            ],
            "HTML": [
                (["<[!?]?/?[a-zA-Z0-9-]+(?:\\s+[a-zA-Z-]+(?:=\"[^\"]*\")?)*\\s*/?>|</[a-zA-Z0-9-]+>"], keyword_format),
                (["<!--[\\s\\S]*?-->"], comment_format),
                (["\"[^\"]*\""], string_format)
            ],
            "CSS": [
                (["[.#]?[a-zA-Z0-9-_]+\\s*(?:[,{]|$)|@[a-zA-Z-]+|(?:margin|padding|border|color|background|font|text|line|display|position|width|height|top|right|bottom|left|float|clear|overflow|z-index|opacity)(?=\\s*:)"], keyword_format),
                (["[{};:]"], keyword_format),
                (["#[0-9a-fA-F]{3,6}"], string_format),
                (["[0-9]+(?:px|em|rem|%|pt|vh|vw)"], string_format),
                (["(?<=/\\*).*?(?=\\*/)"], comment_format)
            ],
            "C++": [
                (["\\b(class|struct|enum|union|typedef|template|namespace|using|public|private|protected|virtual|static|const|volatile|friend|inline|extern|auto|register|void|int|char|short|long|float|double|bool|signed|unsigned|true|false|if|else|for|while|do|switch|case|break|continue|return|try|catch|throw|new|delete)\\b"], keyword_format),
                (["//[^\n]*|/\\*[^*]*\\*+(?:[^/*][^*]*\\*+)*/"], comment_format),
                (["\".*?\"|'.*?'"], string_format)
            ],
            "Java": [
                (["\\b(class|interface|enum|extends|implements|package|import|public|private|protected|static|final|abstract|synchronized|volatile|transient|native|strictfp|void|boolean|byte|char|short|int|long|float|double|if|else|for|while|do|switch|case|break|continue|return|try|catch|finally|throw|throws|new|instanceof|this|super|null|true|false)\\b"], keyword_format),
                (["//[^\n]*|/\\*[^*]*\\*+(?:[^/*][^*]*\\*+)*/"], comment_format),
                (["\".*?\"|'.*?'"], string_format)
            ]
        }
        
    def set_language(self, language):
        self.current_language = language
        self.highlighting_rules = [] # 清空现有规则

        # 1. 添加通用高亮规则 (如 TODO, 通用关键字等)
        # TODO format (保持在最前面，优先匹配)
        todo_format = QTextCharFormat()
        todo_format.setForeground(QColor("#FF0000"))  # 醒目的红色
        todo_format.setFontWeight(QFont.Bold)
        todo_format.setBackground(QColor("#FFFF00"))  # 黄色背景
        self.add_mapping(["\\bTODO:\\s*.*$"], todo_format)

        # FIXME format (similar to TODO)
        fixme_format = QTextCharFormat()
        fixme_format.setForeground(QColor("#FF4500"))  # 红橙色
        fixme_format.setFontWeight(QFont.Bold)
        fixme_format.setBackground(QColor("#FFFF00")) # Yellow background like TODO
        self.add_mapping(["\\bFIXME:\\s*.*$"], fixme_format)

        # 通用 Comment format (适用于所有语言的基础注释)
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955")) # 默认注释颜色
        # 基础注释规则，语言特定规则会覆盖或补充
        self.add_mapping(["#[^\n]*", "//[^\n]*"], comment_format)

        # 通用 String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178")) # 默认字符串颜色
        self.add_mapping(['"[^"\\]*(\\.[^"\\]*)*"', "'[^'\\]*(\\.[^'\\]*)*'"], string_format)

        # 通用 Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8")) # 默认数字颜色
        self.add_mapping(["\\b[0-9]+\\b"], number_format)

        # 2. 添加特定语言的高亮规则
        if language in self.language_rules:
            for patterns, format in self.language_rules[language]:
                self.add_mapping(patterns, format)
        # else: # 如果没有特定语言规则，可以考虑添加一些非常通用的规则，但目前已在上面添加
            # pass

        # 3. 重新应用高亮
        self.rehighlight()

    def add_mapping(self, patterns, format):
        """Add a mapping between a list of patterns and a format"""
        for pattern in patterns:
            regex = QRegularExpression(pattern)
            self.highlighting_rules.append((regex, format))
            
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given text block"""
        for pattern, format in self.highlighting_rules:
            match_iterator = pattern.globalMatch(text)
            while match_iterator.hasNext():
                match = match_iterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class LineNumberArea(QWidget):
    """Widget for displaying line numbers"""
    
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor
        
    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)
        
    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    """Enhanced text editor with line numbers and syntax highlighting"""
    
    blockCountChanged = Signal(int)
    updateRequest = Signal(QTextCursor, int)
    
    def __init__(self, parent=None, settings=None):
        super().__init__(parent)
        self.settings = settings

        # 设置Tab键为4个空格宽度
        fm = QFontMetrics(self.font())
        self.setTabStopDistance(4 * fm.horizontalAdvance(' '))

        # 显示空白字符
        text_option = self.document().defaultTextOption()
        text_option.setFlags(text_option.flags() | QTextOption.ShowTabsAndSpaces)
        self.document().setDefaultTextOption(text_option)

        # 添加节流定时器
        self.update_timer = QTimer(self)
        self.update_timer.setSingleShot(True)
        self.update_timer.timeout.connect(lambda: self.line_number_area.update())
        
        # Set up line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        # Syntax highlighter - Instantiate before setting font
        self.highlighter = SyntaxHighlighter(self.document(), settings=self.settings)

        # Initialize font and related settings
        self.init_font()

        # Update initial area width and highlight
        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def init_font(self):
        # Load font settings from Config object
        font = QFont()
        font.setFamily(self.settings.get_editor_setting("font_family", "Monospace"))
        font.setPointSize(int(self.settings.get_editor_setting("font_size", "12")))
        self.setFont(font)

        if hasattr(self, 'line_number_area'):
            self.line_number_area.setFont(font)

        # Update tab stop distance based on new font metrics
        fm = QFontMetrics(self.font())
        self.setTabStopDistance(int(self.settings.get_editor_setting("tab_size", "4")) * fm.horizontalAdvance(' '))
        
    def line_number_area_width(self):
        """Calculate the width of the line number area"""
        digits = 1
        # 获取实际可见行数
        visible_lines = sum(1 for block in (self.document().findBlockByNumber(i) for i in range(self.document().blockCount())) if block.isVisible())
        max_num = max(1, visible_lines)
        
        # 动态计算数字位数
        digits = len(str(max_num))
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
        
    def update_line_number_area_width(self, new_block_count):
        """Update the line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            # 立即触发更新并重置定时器
            self.line_number_area.update()
            self.update_timer.start(10)
        
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
            
    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#E8E8E8"))

        block = self.firstVisibleBlock()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        # 仅绘制可见区域
        visible_rect = event.rect()
        while block.isValid() and top <= visible_rect.bottom():
            if block.isVisible() and bottom >= visible_rect.top():
                line_number = block.blockNumber() + 1
                painter.setPen(QColor("#606060"))
                painter.drawText(
                    0, top, self.line_number_area.width() - 10,
                    self.fontMetrics().height(),
                    Qt.AlignRight, str(line_number)
                )
            
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            
            if top > visible_rect.bottom():
                break
            
        painter.end()
            
    def highlight_current_line(self):
        """Highlight the current line"""
        extra_selections = []
        
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#F8F8F8")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
            
        self.setExtraSelections(extra_selections)
        
    def set_language(self, language):
        """Set the current programming language for syntax highlighting"""
        if hasattr(self, 'highlighter'):
            self.highlighter.set_language(language)
        



class EditorTab(QWidget):
    """Tab containing an editor and its related information"""
    
    def __init__(self, parent=None, file_path=None, settings=None):
        super().__init__(parent)
        self.file_path = file_path
        self.modified = False
        
        # 接收并保存settings参数
        self.settings = settings
        
        # Create layout
        layout = QVBoxLayout()
        
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create editor
        self.settings = settings
        self.editor = CodeEditor(settings=self.settings)

        # 根据文件扩展名设置语言
        language = 'Plain Text' # Default language
        if file_path:
            language = SyntaxHighlighter.get_language_from_extension(file_path)
        self.editor.set_language(language)
        self.editor.textChanged.connect(self.text_modified)
        layout.addWidget(self.editor)
        
        # 初始化插件
        from plugins.bracket_completer import BracketCompleterPlugin
        from plugins.todo_highlighter import TodoHighlighterPlugin
        self.bracket_completer = BracketCompleterPlugin(self.editor)
        self.todo_highlighter = TodoHighlighterPlugin(self.editor)
        
        self.setLayout(layout)
        
        # Load file if provided
        if file_path:
            self.load_file(file_path)
            
    def text_modified(self):
        """Handle text modifications"""
        if not self.modified:
            self.modified = True
            # 遍历父级组件直到找到QTabWidget
            parent = self
            while parent:
                parent = parent.parent()
                if isinstance(parent, QTabWidget):
                    index = parent.indexOf(self)
                    text = parent.tabText(index)
                    if not text.endswith('*'):
                        parent.setTabText(index, text + '*')
                    break
    
    def load_file(self, file_path):
        """Load a file into the editor"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                self.editor.setPlainText(f.read())
            self.file_path = file_path
            self.modified = False
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")
            return False
    
    def save_file(self, file_path=None):
        """Save the editor content to a file"""
        if not file_path:
            file_path = self.file_path
            
        if not file_path:
            return False
            
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.editor.toPlainText())
            self.file_path = file_path
            self.modified = False
            parent = self.parent()
            if hasattr(parent, 'tabText'):
                index = parent.indexOf(self)
                text = parent.tabText(index)
                if text.endswith('*'):
                    parent.setTabText(index, text[:-1])
            return True
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not save file: {str(e)}")
            return False


class NotePadPlusPlus(QMainWindow):
    """Main window for the NotePad++ clone"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NotePad++ Clone")
        self.resize(800, 600)
        
        # 设置应用程序图标
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
            if not icon.isNull():
                self.setWindowIcon(icon)
            else:
                print("警告：无法加载图标文件")
        
        # 初始化配置管理
        from config import Config
        from history import History
        from plugins import PluginManager
        
        self.config = Config('npp.ini')
        self.settings = self.config  # 添加settings属性
        self.history = History()  # 使用.recent_files隐藏文件
        self.plugin_manager = PluginManager('plugins')
        
        self.setup_ui()
        
        # 加载配置和插件
        self.load_settings()
        self.load_plugins()
        
        # 恢复上次会话的文件
        recent_files = self.history.recent_files
        if recent_files:
            for file_path in recent_files:
                if os.path.exists(file_path):
                    self.open_file(file_path)
        
        # 如果没有打开任何文件，显示欢迎标签页
        if self.tab_widget.count() == 0:
            self.new_file()
            
        # 添加最近文件菜单
        self.update_recent_files_menu()
            
    def setup_ui(self):
        """Set up the user interface"""
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.setStyleSheet("QTabBar::tab { height: 30px; }")
        self.setCentralWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Line and column indicator
        self.line_col_label = QLabel("Ln: 1, Col: 1")
        self.status_bar.addPermanentWidget(self.line_col_label)
        
        # Create menus
        self.create_menus()
        
        # Create toolbars
        self.create_toolbars()
        
        # Set default font
        default_font = QFont()
        default_font.setPointSize(16)
        QApplication.setFont(default_font)
        
        # Enable line numbers
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if hasattr(editor, 'setLineNumbersVisible'):
                editor.setLineNumbersVisible(True)
        
        # Create document list dock
        self.create_document_list()
        
        # Connect signals
        self.tab_widget.currentChanged.connect(self.update_ui)
        
    def create_menus(self):
        """Create the menu bar"""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        new_action = QAction("&New", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction("&Open...", self)
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)
        
        save_action = QAction("&Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)
        
        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut(QKeySequence.SaveAs)
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)
        
        file_menu.addSeparator()
        
        close_action = QAction("&Close", self)
        close_action.setShortcut(QKeySequence.Close)
        close_action.triggered.connect(self.close_current_tab)
        file_menu.addAction(close_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        undo_action = QAction("&Undo", self)
        undo_action.setShortcut(QKeySequence.Undo)
        undo_action.triggered.connect(self.undo)
        edit_menu.addAction(undo_action)
        
        redo_action = QAction("&Redo", self)
        redo_action.setShortcut(QKeySequence.Redo)
        redo_action.triggered.connect(self.redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        cut_action = QAction("Cu&t", self)
        cut_action.setShortcut(QKeySequence.Cut)
        cut_action.triggered.connect(self.cut)
        edit_menu.addAction(cut_action)
        
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self.copy)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self.paste)
        edit_menu.addAction(paste_action)
        
        delete_action = QAction("&Delete", self)
        delete_action.setShortcut(QKeySequence.Delete)
        delete_action.triggered.connect(self.delete)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select &All", self)
        select_all_action.setShortcut(QKeySequence.SelectAll)
        select_all_action.triggered.connect(self.select_all)
        edit_menu.addAction(select_all_action)
        
        # Search menu
        search_menu = self.menuBar().addMenu("&Search")
        
        find_action = QAction("&Find...", self)
        find_action.setShortcut(QKeySequence.Find)
        find_action.triggered.connect(self.find)
        search_menu.addAction(find_action)
        
        find_next_action = QAction("Find &Next", self)
        find_next_action.setShortcut(QKeySequence("F3"))
        find_next_action.triggered.connect(self.find_next)
        search_menu.addAction(find_next_action)
        
        find_prev_action = QAction("Find &Previous", self)
        find_prev_action.setShortcut(QKeySequence("Shift+F3"))
        find_prev_action.triggered.connect(self.find_previous)
        search_menu.addAction(find_prev_action)
        
        replace_action = QAction("&Replace...", self)
        replace_action.setShortcut(QKeySequence("Ctrl+H"))
        replace_action.triggered.connect(self.replace)
        search_menu.addAction(replace_action)
        
        goto_action = QAction("&Go to...", self)
        goto_action.setShortcut(QKeySequence("Ctrl+G"))
        goto_action.triggered.connect(self.goto_line)
        search_menu.addAction(goto_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        font_action = QAction("设置字体...", self)
        font_action.triggered.connect(self.select_font)
        view_menu.addAction(font_action)
        
        # Language menu
        language_menu = self.menuBar().addMenu("&Language")
        language_group = QActionGroup(self)
        
        # 添加支持的语言
        languages = ["Plain Text", "Python", "JavaScript", "HTML", "CSS", "C++", "Java"]
        for lang in languages:
            action = QAction(lang, self, checkable=True)
            action.triggered.connect(lambda checked, l=lang: self.change_language(l))
            language_group.addAction(action)
            language_menu.addAction(action)
            if lang == "Plain Text":
                action.setChecked(True)
        
        zoom_in_action = QAction("Zoom &In", self)
        zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        zoom_in_action.triggered.connect(self.zoom_in)
        view_menu.addAction(zoom_in_action)
        
        zoom_out_action = QAction("Zoom &Out", self)
        zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        zoom_out_action.triggered.connect(self.zoom_out)
        view_menu.addAction(zoom_out_action)
        
        reset_zoom_action = QAction("&Reset Zoom", self)
        reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        reset_zoom_action.triggered.connect(self.reset_zoom)
        view_menu.addAction(reset_zoom_action)
        
        view_menu.addSeparator()
        
        toggle_status_bar_action = QAction("Status &Bar", self)
        toggle_status_bar_action.setCheckable(True)
        toggle_status_bar_action.setChecked(True)
        toggle_status_bar_action.triggered.connect(self.toggle_status_bar)
        view_menu.addAction(toggle_status_bar_action)
        
        # Format menu
        format_menu = self.menuBar().addMenu("F&ormat")
        
        word_wrap_action = QAction("&Word Wrap", self)
        word_wrap_action.setCheckable(True)
        word_wrap_action.setChecked(False)
        word_wrap_action.triggered.connect(self.toggle_word_wrap)
        format_menu.addAction(word_wrap_action)
        
        font_action = QAction("&Font...", self)
        font_action.triggered.connect(self.choose_font)
        format_menu.addAction(font_action)
        
        # Language menu
        language_menu = self.menuBar().addMenu("&Language")
        language_group = QActionGroup(self)
        language_group.setExclusive(True)
        
        languages = ["Plain Text", "HTML", "CSS", "JavaScript", "Python", "C++", "Java"]
        for lang in languages:
            lang_action = QAction(lang, self)
            lang_action.setCheckable(True)
            if lang == "Plain Text":
                lang_action.setChecked(True)
            lang_action.triggered.connect(lambda checked, l=lang: self.set_language(l))
            language_group.addAction(lang_action)
            language_menu.addAction(lang_action)
        
        # Settings menu
        settings_menu = self.menuBar().addMenu("Se&ttings")
        
        preferences_action = QAction("&Preferences...", self)
        preferences_action.triggered.connect(self.show_preferences)
        settings_menu.addAction(preferences_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbars(self):
        """Create toolbars with emoji icons"""
        # File toolbar
        file_toolbar = self.addToolBar("File")
        file_toolbar.setIconSize(QSize(32, 32))
        
        new_action = QAction("📄", self)
        new_action.setToolTip("New File")
        new_action.triggered.connect(self.new_file)
        file_toolbar.addAction(new_action)
        
        open_action = QAction("📂", self)
        open_action.setToolTip("Open File")
        open_action.triggered.connect(self.open_file)
        file_toolbar.addAction(open_action)
        
        save_action = QAction("💾", self)
        save_action.setToolTip("Save File")
        save_action.triggered.connect(self.save_file)
        file_toolbar.addAction(save_action)
        
        # Edit toolbar
        edit_toolbar = self.addToolBar("Edit")
        edit_toolbar.setIconSize(QSize(16, 16))
        
        undo_action = QAction("↩️", self)
        undo_action.setToolTip("Undo")
        undo_action.triggered.connect(self.undo)
        edit_toolbar.addAction(undo_action)
        
        redo_action = QAction("↪️", self)
        redo_action.setToolTip("Redo")
        redo_action.triggered.connect(self.redo)
        edit_toolbar.addAction(redo_action)
        
        cut_action = QAction("✂️", self)
        cut_action.setToolTip("Cut")
        cut_action.triggered.connect(self.cut)
        edit_toolbar.addAction(cut_action)
        
        copy_action = QAction("📋", self)
        copy_action.setToolTip("Copy")
        copy_action.triggered.connect(self.copy)
        edit_toolbar.addAction(copy_action)
        
        paste_action = QAction("📌", self)
        paste_action.setToolTip("Paste")
        paste_action.triggered.connect(self.paste)
        edit_toolbar.addAction(paste_action)
        
        # Search toolbar
        search_toolbar = self.addToolBar("Search")
        search_toolbar.setIconSize(QSize(16, 16))
        
        find_action = QAction("🔍", self)
        find_action.setToolTip("Find")
        find_action.triggered.connect(self.find)
        search_toolbar.addAction(find_action)
        
        replace_action = QAction("🔄", self)
        replace_action.setToolTip("Replace")
        replace_action.triggered.connect(self.replace)
        search_toolbar.addAction(replace_action)
        
        # View toolbar
        view_toolbar = self.addToolBar("View")
        view_toolbar.setIconSize(QSize(16, 16))
        
        zoom_in_action = QAction("🔍+", self)
        zoom_in_action.setToolTip("Zoom In")
        zoom_in_action.triggered.connect(self.zoom_in)
        view_toolbar.addAction(zoom_in_action)
        
        zoom_out_action = QAction("🔍-", self)
        zoom_out_action.setToolTip("Zoom Out")
        zoom_out_action.triggered.connect(self.zoom_out)
        view_toolbar.addAction(zoom_out_action)
        
    def create_document_list(self):
        """Create a dock widget with a list of open documents"""
        self.doc_list = QListWidget()
        self.doc_list.itemClicked.connect(self.activate_document)
        
        dock = QDockWidget("Document List", self)
        dock.setWidget(self.doc_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)
        
    def get_current_editor(self):
        """Get the current active editor"""
        current_tab = self.tab_widget.currentWidget()
        if current_tab:
            return current_tab.editor
        return None
    
    def update_ui(self):
        """Update UI based on the current tab"""
        editor = self.get_current_editor()
        if editor:
            # Update status bar
            cursor = editor.textCursor()
            line = cursor.blockNumber() + 1
            column = cursor.columnNumber() + 1
            self.line_col_label.setText(f"Ln: {line}, Col: {column}")
            
            # Update document list
            self.update_document_list()
        
    def update_document_list(self):
        """Update the document list"""
        self.doc_list.clear()
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            name = self.tab_widget.tabText(i)
            if tab.file_path:
                name = os.path.basename(tab.file_path)
            self.doc_list.addItem(name)
        
        # Highlight current item
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.doc_list.setCurrentRow(current_index)
            
    def activate_document(self, item):
        """Activate the document corresponding to the clicked item"""
        index = self.doc_list.row(item)
        if 0 <= index < self.tab_widget.count():
            self.tab_widget.setCurrentIndex(index)
    
    def new_file(self):
        """Create a new empty tab"""
        tab = EditorTab(self.tab_widget, settings=self.settings)
        index = self.tab_widget.addTab(tab, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        tab.editor.cursorPositionChanged.connect(self.update_ui)
        self.update_document_list()
        return tab
    
    def open_file(self, file_path=None):
        """Open a file"""
        if file_path is None:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Open File", "", "All Files (*)"
            )
        
        if file_path:
            # Check if the file is already open
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                if tab.file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return
                    
            # Create new tab and load file
            tab = EditorTab(self.tab_widget, file_path)
            name = os.path.basename(file_path)
            index = self.tab_widget.addTab(tab, name)
            self.tab_widget.setCurrentIndex(index)
            tab.editor.cursorPositionChanged.connect(self.update_ui)
            self.update_document_list()
            
    def dragEnterEvent(self, event):
        """Handle drag enter events"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            
    def dropEvent(self, event):
        """Handle drop events"""
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                self.open_file(file_path)
    
    def save_file(self):
        """Save the current file"""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return
            
        if not current_tab.file_path:
            return self.save_file_as()
            
        success = current_tab.save_file()
        if success:
            self.update_document_list()
        return success
    
    def save_file_as(self):
        """Save the current file with a new name"""
        current_tab = self.tab_widget.currentWidget()
        if not current_tab:
            return False
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save File As", "", "All Files (*)"
        )
        
        if not file_path:
            return False
            
        success = current_tab.save_file(file_path)
        if success:
            name = os.path.basename(file_path)
            self.tab_widget.setTabText(self.tab_widget.currentIndex(), name)
            self.update_document_list()
        return success
    
    def close_tab(self, index):
        """Close the tab at the given index"""
        tab = self.tab_widget.widget(index)
        
        if tab.modified:
            msg_box = QMessageBox()
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setText(f"The document has been modified.")
            msg_box.setInformativeText("Do you want to save your changes?")
            msg_box.setStandardButtons(
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            msg_box.setDefaultButton(QMessageBox.Save)
            ret = msg_box.exec_()
            
            if ret == QMessageBox.Save:
                # Save was clicked
                current_index = self.tab_widget.currentIndex()
                self.tab_widget.setCurrentIndex(index)
                if not self.save_file():
                    # Save failed, abort closing
                    self.tab_widget.setCurrentIndex(current_index)
                    return
            elif ret == QMessageBox.Cancel:
                # Cancel was clicked
                return
                
        self.tab_widget.removeTab(index)
        tab.deleteLater()
        self.update_document_list()
        
        # Create a new tab if none left
        if self.tab_widget.count() == 0:
            self.new_file()
    
    def close_current_tab(self):
        """Close the current tab"""
        current_index = self.tab_widget.currentIndex()
        if current_index >= 0:
            self.close_tab(current_index)
    
    def undo(self):
        """Undo the last action"""
        editor = self.get_current_editor()
        if editor:
            editor.undo()
    
    def redo(self):
        """Redo the last undone action"""
        editor = self.get_current_editor()
        if editor:
            editor.redo()
    
    def cut(self):
        """Cut the selected text"""
        editor = self.get_current_editor()
        if editor:
            editor.cut()
    
    def copy(self):
        """Copy the selected text"""
        editor = self.get_current_editor()
        if editor:
            editor.copy()
    
    def paste(self):
        """Paste text from clipboard"""
        editor = self.get_current_editor()
        if editor:
            editor.paste()
    
    def delete(self):
        """Delete the selected text"""
        editor = self.get_current_editor()
        if editor:
            editor.textCursor().removeSelectedText()
    
    def select_all(self):
        """Select all text"""
        editor = self.get_current_editor()
        if editor:
            editor.selectAll()
    
    def find(self):
        """Show find dialog"""
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
    
    def find_next(self):
        """Find the next occurrence"""
        if hasattr(self, 'find_replace_dialog'):
            self.find_replace_dialog.find_text()
        else:
            self.find()
    
    def find_previous(self):
        """Find the previous occurrence"""
        if hasattr(self, 'find_replace_dialog'):
            old_state = self.find_replace_dialog.up_radio.isChecked()
            self.find_replace_dialog.up_radio.setChecked(True)
            self.find_replace_dialog.find_text()
            self.find_replace_dialog.up_radio.setChecked(old_state)
        else:
            self.find()
    
    def replace(self):
        """Show replace dialog"""
        self.find_replace_dialog = FindReplaceDialog(self)
        self.find_replace_dialog.show()
        
    def goto_line(self):
        """Go to a specific line"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        line, ok = QInputDialog.getInt(
            self, "Go to Line", "Line number:", 1, 1, editor.document().blockCount()
        )
        
        if ok:
            cursor = QTextCursor(editor.document().findBlockByNumber(line - 1))
            editor.setTextCursor(cursor)
            editor.ensureCursorVisible()
    
    def zoom_in(self):
        """Increase font size"""
        editor = self.get_current_editor()
        if editor:
            font = editor.font()
            size = font.pointSize()
            font.setPointSize(size + 1)
            editor.setFont(font)
    
    def zoom_out(self):
        """Decrease font size"""
        editor = self.get_current_editor()
        if editor:
            font = editor.font()
            size = font.pointSize()
            if size > 1:
                font.setPointSize(size - 1)
                editor.setFont(font)
    
    def reset_zoom(self):
        """Reset font size to default"""
        editor = self.get_current_editor()
        if editor:
            font = editor.font()
            font.setPointSize(10)
            editor.setFont(font)
    
    def toggle_status_bar(self, checked):
        """Toggle status bar visibility"""
        self.status_bar.setVisible(checked)
    
    def toggle_word_wrap(self, checked):
        """Toggle word wrap"""
        editor = self.get_current_editor()
        if editor:
            if checked:
                editor.setLineWrapMode(QTextEdit.WidgetWidth)
            else:
                editor.setLineWrapMode(QTextEdit.NoWrap)
    
    def choose_font(self):
        """Open font dialog"""
        editor = self.get_current_editor()
        if not editor:
            return
            
        current_font = editor.font()
        font, ok = QFontDialog.getFont(current_font, self)
        
        if ok:
            editor.setFont(font)
    
    def change_language(self, language):
        """切换当前编辑器的语言"""
        editor = self.get_current_editor()
        if editor and hasattr(editor, 'editor'):
            editor.editor.highlighter.set_language(language)
            self.status_bar.showMessage(f"当前语言: {language}", 2000)
    
    def set_language(self, language):
        """Set the language for syntax highlighting"""
        editor = self.get_current_editor()
        if editor:
            # 更新语法高亮器的语言
            if hasattr(editor, 'highlighter'):
                editor.highlighter.set_language(language)
            
            # 更新状态栏显示当前语言
            self.status_bar.showMessage(f"当前语言: {language}", 2000)
            editor.set_language(language)
    
    def show_preferences(self):
        """Show preferences dialog"""
        QMessageBox.information(self, "Preferences", 
                              "Preferences dialog would be shown here.")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About NotePad++ Clone",
                        """<b>NotePad++ Clone</b>
                        <p>A simple clone of NotePad++ using PySide6.</p>
                        <p>Created with emoji-based toolbar icons.</p>""")
    
    def select_font(self):
        font, ok = QFontDialog.getFont(self)
        if ok:
            self.settings.setValue("editorFont", font.toString())
            self.update_all_editor_fonts(font)
    
    def update_all_editor_fonts(self, font):
        for i in range(self.tab_widget.count()):
            editor = self.tab_widget.widget(i)
            if isinstance(editor, CodeEditor):
                editor.setFont(font)
    
    def load_settings(self):
        """加载窗口几何信息"""
        geometry_file = QFile('.geometry')
        if geometry_file.exists():
            if geometry_file.open(QFile.ReadOnly):
                self.restoreGeometry(geometry_file.readAll())
                geometry_file.close()
        else:
            # 向后兼容旧配置
            geometry = self.config.get_editor_setting('geometry')
            if geometry:
                self.restoreGeometry(bytes.fromhex(geometry))

        # 加载windowstate
        state_file = QFile('.windowstate')
        if state_file.exists():
            if state_file.open(QFile.ReadOnly):
                self.restoreState(state_file.readAll())
                state_file.close()
        else:
            # 向后兼容旧配置
            state = self.config.get_editor_setting('windowstate')
            if state:
                self.restoreState(bytes.fromhex(state))

    def save_settings(self):
        """保存窗口设置"""

        
        # 加载独立窗口状态文件
        geometry_file = QFile('.geometry')
        if geometry_file.exists() and geometry_file.open(QFile.ReadOnly):
            self.restoreGeometry(geometry_file.readAll())
            geometry_file.close()
            
        state_file = QFile('.windowstate')
        if state_file.exists() and state_file.open(QFile.ReadOnly):
            self.restoreState(state_file.readAll())
            state_file.close()
        
        # 删除旧的INI配置保存逻辑
        
        # 保存到独立文件
        geometry_file = QFile('.geometry')
        if geometry_file.open(QFile.WriteOnly):
            geometry_file.write(self.saveGeometry())
            geometry_file.close()
            
        state_file = QFile('.windowstate')
        if state_file.open(QFile.WriteOnly):
            state_file.write(self.saveState())
            state_file.close()

        # 保存当前编辑器设置
        font_family = self.config.get_editor_setting("font_family", "Monospace")
        font_size = int(self.config.get_editor_setting("font_size", "12"))
        tab_size = int(self.config.get_editor_setting("tab_size", "4"))
        
        # 应用字体设置
        font = QFont(font_family, font_size)
        QApplication.setFont(font)
        
        # 更新所有编辑器的设置
        for i in range(self.tab_widget.count()):
            editor_tab = self.tab_widget.widget(i)
            if hasattr(editor_tab, 'editor'):
                editor_tab.editor.setFont(font)
                metrics = QFontMetrics(font)
                editor_tab.editor.setTabStopDistance(tab_size * metrics.horizontalAdvance(' '))
    
    def load_plugins(self):
        """加载启用的插件"""
        enabled_plugins = self.config.get_enabled_plugins()
        
        # 创建新的插件菜单
        plugins_menu = QMenu("&Plugins", self)
        
        # 添加管理插件菜单项
        manage_plugins_action = QAction("Manage Plugins...", self)
        manage_plugins_action.triggered.connect(self.manage_plugins)
        plugins_menu.addAction(manage_plugins_action)
        
        # 添加分隔线
        plugins_menu.addSeparator()
        
        # 加载插件并创建菜单项
        for plugin_name in enabled_plugins:
            plugin = self.plugin_manager.load_plugin(plugin_name, self)
            if plugin:
                # 为插件创建菜单项
                plugin_action = QAction(plugin.name, self)
                plugin_action.setStatusTip(plugin.description)
                plugins_menu.addAction(plugin_action)
        
        # 替换原有的插件菜单
        for action in self.menuBar().actions():
            if action.text() == "&Plugins":
                self.menuBar().removeAction(action)
                break
        
        self.menuBar().addMenu(plugins_menu)
    
    def manage_plugins(self):
        """管理插件"""
        dialog = QDialog(self)
        dialog.setWindowTitle("插件管理")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # 创建插件列表
        plugin_list = QListWidget()
        layout.addWidget(plugin_list)
        
        # 获取所有可用插件和已启用插件
        available_plugins = self.plugin_manager.discover_plugins()
        enabled_plugins = self.config.get_enabled_plugins()
        
        # 添加插件到列表
        for plugin_name in available_plugins:
            item = QListWidgetItem(plugin_name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Checked if plugin_name in enabled_plugins else Qt.Unchecked)
            plugin_list.addItem(item)
        
        # 添加按钮
        button_box = QHBoxLayout()
        
        apply_button = QPushButton("应用")
        apply_button.clicked.connect(lambda: self.apply_plugin_changes(plugin_list, dialog))
        button_box.addWidget(apply_button)
        
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(dialog.reject)
        button_box.addWidget(cancel_button)
        
        layout.addLayout(button_box)
        dialog.setLayout(layout)
        dialog.exec_()
    
    def apply_plugin_changes(self, plugin_list: QListWidget, dialog: QDialog):
        """应用插件更改"""
        # 获取选中的插件
        enabled_plugins = []
        for i in range(plugin_list.count()):
            item = plugin_list.item(i)
            if item.checkState() == Qt.Checked:
                enabled_plugins.append(item.text())
        
        # 保存启用的插件
        self.config.set_enabled_plugins(enabled_plugins)
        
        # 重新加载插件
        self.plugin_manager.unload_all_plugins()
        self.load_plugins()
        
        dialog.accept()
    
    def update_recent_files_menu(self):
        """Update the recent files menu"""
        # Initialize recent file actions list if not exists
        if not hasattr(self, 'recent_file_actions'):
            self.recent_file_actions = []
            
        # Find the File menu
        file_menu = None
        for action in self.menuBar().actions():
            if action.text() == "&File":
                file_menu = action.menu()
                break
        
        if not file_menu:
            return
            
        # Find separators and clear old recent files
        recent_files_start = None
        recent_files_end = None
        
        # Get current actions safely
        try:
            current_actions = file_menu.actions()
            
            # Find separator positions
            for i, action in enumerate(current_actions):
                if action and action.isSeparator():
                    if recent_files_start is None:
                        recent_files_start = i
                        self.separator_action = action
                    elif recent_files_end is None:
                        recent_files_end = i
                        break
                        
            # Remove old recent file entries
            if recent_files_start is not None:
                # Get actions to remove
                for action in self.recent_file_actions:
                    if action and action.parent() == file_menu:
                        file_menu.removeAction(action)
                        action.deleteLater()
                self.recent_file_actions.clear()
                
            # Add new recent file entries
            recent_files = self.history.recent_files
            if recent_files and self.separator_action:
                for file_path in recent_files:
                    # Create new action with proper ownership
                    action = QAction(os.path.basename(file_path), file_menu)
                    action.setStatusTip(file_path)
                    action.triggered.connect(
                        lambda checked, path=file_path: self.open_file(path)
                    )
                    
                    # Insert action and track it
                    file_menu.insertAction(self.separator_action, action)
                    self.recent_file_actions.append(action)
                    
        except RuntimeError:
            # Handle case where menu is being deleted
            pass  # 设置父对象确保生命周期管理
    
    def open_file(self, file_path=None):
        """打开文件"""
        if not file_path:
            file_path, _ = QFileDialog.getOpenFileName(self, "Open File")
        
        if file_path:
            # 检查文件是否已经打开
            for i in range(self.tab_widget.count()):
                tab = self.tab_widget.widget(i)
                if hasattr(tab, 'file_path') and tab.file_path == file_path:
                    self.tab_widget.setCurrentIndex(i)
                    return
            
            # 创建新标签页并加载文件
            tab = EditorTab(self, file_path, self.config)
            if tab.load_file(file_path):
                index = self.tab_widget.addTab(tab, os.path.basename(file_path))
                self.tab_widget.setCurrentIndex(index)
                self.history.add_file(file_path)
                self.update_recent_files_menu()
    
    def save_settings(self):
        """保存应用程序设置"""
        # 保存窗口几何信息和状态到隐藏文件
        geometry_file = QFile('.geometry')
        if geometry_file.open(QFile.WriteOnly):
            geometry_file.write(self.saveGeometry())
            geometry_file.close()
            
        state_file = QFile('.windowstate')
        if state_file.open(QFile.WriteOnly):
            state_file.write(self.saveState())
            state_file.close()
        
        # 保存当前编辑器设置
        if self.tab_widget.count() > 0:
            editor = self.get_current_editor()
            if editor:
                font = editor.font()
                self.config.set_editor_setting("font_family", font.family())
                self.config.set_editor_setting("font_size", str(font.pointSize()))
                
                # 计算当前的tab大小
                metrics = QFontMetrics(font)
                tab_size = int(editor.tabStopDistance() / metrics.horizontalAdvance(' '))
                self.config.set_editor_setting("tab_size", str(tab_size))
    
    def closeEvent(self, event):
        """Handle close event"""
        # Check for unsaved changes
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if tab.modified:
                self.tab_widget.setCurrentIndex(i)
                
                msg_box = QMessageBox()
                msg_box.setIcon(QMessageBox.Question)
                msg_box.setText(f"The document has been modified.")
                msg_box.setInformativeText("Do you want to save your changes?")
                msg_box.setStandardButtons(
                    QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
                )
                msg_box.setDefaultButton(QMessageBox.Save)
                ret = msg_box.exec_()
                
                if ret == QMessageBox.Save:
                    # Save was clicked
                    if not self.save_file():
                        # Save failed, cancel closing
                        event.ignore()
                        return
                elif ret == QMessageBox.Cancel:
                    # Cancel was clicked
                    event.ignore()
                    return
        
        # Save settings
        self.save_settings()
        
        # Accept the close event
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Use Fusion style for a modern look
    window = NotePadPlusPlus()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
import sys
import os
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QPlainTextEdit, QTextEdit, QFileDialog, 
                               QMessageBox, QFontDialog, QColorDialog, 
                               QMenu, QToolBar, QTabWidget, QWidget, QVBoxLayout,
                               QHBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton,
                               QDialog, QCheckBox, QRadioButton, QButtonGroup, QGridLayout,
                               QStatusBar, QSplitter, QListWidget, QDockWidget)
from PySide6.QtGui import (QFont, QFontMetrics, QTextCharFormat, QTextCursor, 
                         QKeySequence, QTextDocument, QColor, QSyntaxHighlighter, 
                         QTextFormat, QIcon, QAction, QPainter)
from PySide6.QtCore import Qt, QRegularExpression, QSize, Signal, Slot, QSettings, QTimer

class FindReplaceDialog(QDialog):
    """Dialog for find and replace functionality"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Define formats for different syntax elements
        self.formats = {}
        
        # Keywords format
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#569CD6"))
        keyword_format.setFontWeight(QFont.Bold)
        keywords = [
            "\\bclass\\b", "\\bdef\\b", "\\bfor\\b", "\\bif\\b", "\\belif\\b",
            "\\belse\\b", "\\bwhile\\b", "\\breturn\\b", "\\bimport\\b", "\\bas\\b",
            "\\bfrom\\b", "\\bTrue\\b", "\\bFalse\\b", "\\btry\\b", "\\bexcept\\b",
            "\\bfinally\\b", "\\braise\\b", "\\bNone\\b", "\\bbreak\\b", "\\bcontinue\\b",
            "\\bpass\\b", "\\bin\\b", "\\bis\\b", "\\bnot\\b", "\\band\\b", "\\bor\\b",
            "\\blambda\\b", "\\bwith\\b", "\\bglobal\\b", "\\bnonlocal\\b"
        ]
        self.add_mapping(keywords, keyword_format)
        
        # HTML tag format
        tag_format = QTextCharFormat()
        tag_format.setForeground(QColor("#569CD6"))
        tag_format.setFontWeight(QFont.Bold)
        self.add_mapping(["<[\\s]*[/]?[\\s]*[a-zA-Z0-9_]+[^>]*>"], tag_format)
        
        # HTML attribute format
        attr_format = QTextCharFormat()
        attr_format.setForeground(QColor("#9CDCFE"))
        self.add_mapping(["\\b[a-zA-Z\\-]+(?=\\=)"], attr_format)
        
        # String format
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#CE9178"))
        self.add_mapping(['"[^"\\\\]*(\\\\.[^"\\\\]*)*"', "'[^'\\\\]*(\\\\.[^'\\\\]*)*'"], string_format)
        
        # Number format
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#B5CEA8"))
        self.add_mapping(["\\b[0-9]+\\b"], number_format)
        
        # Comment format
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6A9955"))
        self.add_mapping(["#[^\n]*", "//[^\n]*", "/\\*.*?\\*/"], comment_format)
        
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up line numbers
        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)
        
        # Font settings
        self.setFont(QFont("Consolas", 10))
        
        # Syntax highlighter
        self.highlighter = SyntaxHighlighter(self.document())
        
        # Update initial area width
        self.update_line_number_area_width(0)
        self.highlight_current_line()
        
    def line_number_area_width(self):
        """Calculate the width of the line number area"""
        digits = 1
        max_num = max(1, self.document().blockCount())
        while max_num >= 10:
            max_num //= 10
            digits += 1
        
        space = 3 + self.fontMetrics().horizontalAdvance('9') * digits
        return space
        
    def update_line_number_area_width(self, new_block_count):
        """Update the line number area width"""
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)
        
    def update_line_number_area(self, rect, dy):
        """Update the line number area"""
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
            
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)
            
    def resizeEvent(self, event):
        """Handle resize events"""
        super().resizeEvent(event)
        
        cr = self.contentsRect()
        self.line_number_area.setGeometry(
            cr.left(), cr.top(), self.line_number_area_width(), cr.height()
        )
        
    def line_number_area_paint_event(self, event):
        """Paint the line number area"""
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#E8E8E8"))
        
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = self.blockBoundingGeometry(block).translated(self.contentOffset()).top()
        bottom = top + self.blockBoundingRect(block).height()
        
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#808080"))
                painter.drawText(
                    0, top, self.line_number_area.width() - 5, 
                    self.fontMetrics().height(),
                    Qt.AlignRight, number
                )
                
            block = block.next()
            top = bottom
            bottom = top + self.blockBoundingRect(block).height()
            block_number += 1
            
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
        # In a more complete implementation, this would change the syntax rules
        # based on the selected language
        pass


class EditorTab(QWidget):
    """Tab containing an editor and its related information"""
    
    def __init__(self, parent=None, file_path=None):
        super().__init__(parent)
        self.file_path = file_path
        self.modified = False
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create editor
        self.editor = CodeEditor()
        self.editor.textChanged.connect(self.text_modified)
        layout.addWidget(self.editor)
        
        self.setLayout(layout)
        
        # Load file if provided
        if file_path:
            self.load_file(file_path)
            
    def text_modified(self):
        """Handle text modifications"""
        if not self.modified:
            self.modified = True
            index = self.parent().indexOf(self)
            text = self.parent().tabText(index)
            if not text.endswith('*'):
                self.parent().setTabText(index, text + '*')
    
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
            index = self.parent().indexOf(self)
            text = self.parent().tabText(index)
            if text.endswith('*'):
                self.parent().setTabText(index, text[:-1])
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
        self.setup_ui()
        
        # Settings
        self.settings = QSettings("NPPClone", "NPPClone")
        
        # Load settings
        self.load_settings()
        
        # Show welcome tab
        if self.tab_widget.count() == 0:
            self.new_file()
            
    def setup_ui(self):
        """Set up the user interface"""
        # Create central widget with tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
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
        
        languages = ["Plain Text", "HTML", "CSS", "JavaScript", "Python", "C++", "Java"]
        for lang in languages:
            lang_action = QAction(lang, self)
            lang_action.setCheckable(True)
            if lang == "Plain Text":
                lang_action.setChecked(True)
            lang_action.triggered.connect(lambda checked, l=lang: self.set_language(l))
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
        file_toolbar.setIconSize(QSize(16, 16))
        
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
        """Create a new file tab"""
        tab = EditorTab(self.tab_widget)
        index = self.tab_widget.addTab(tab, "Untitled")
        self.tab_widget.setCurrentIndex(index)
        tab.editor.cursorPositionChanged.connect(self.update_ui)
        self.update_document_list()
        return tab
    
    def open_file(self):
        """Open a file"""
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
    
    def set_language(self, language):
        """Set the language for syntax highlighting"""
        editor = self.get_current_editor()
        if editor:
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
    
    def load_settings(self):
        """Load application settings"""
        # Window geometry
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
            
        # Window state
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def save_settings(self):
        """Save application settings"""
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
    
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
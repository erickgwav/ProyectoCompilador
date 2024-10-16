from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTextEdit, QPlainTextEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QWidget, QTreeView, QHeaderView
from PyQt5.uic import loadUi
import sys
import os

from lexer import lexer
from sint import parser, set_error_output
from sem import SemanticAnalyzer

class NoScrollTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(NoScrollTextEdit, self).__init__(parent)

    def wheelEvent(self, event):
        pass

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi("main.ui", self)
        
        self.line_numbers = []
        self.syntax_errors = []
        
        self.current_path = None
        self.current_fontSize = 10
        self.setWindowTitle("Compilador")
        self.showMaximized() 
        
        self.actionNuevo_archivo.triggered.connect(self.newFile)
        self.actionGuardar.triggered.connect(self.saveFile)
        self.actionGuardar_como.triggered.connect(self.saveFileAs)
        self.actionAbrir_archivo.triggered.connect(self.openFile)
        self.actionCerrar_archivo.triggered.connect(self.closeFile)
        self.actionDeshacer.triggered.connect(self.undo)
        self.actionRehacer.triggered.connect(self.redo)
        self.actionCortar.triggered.connect(self.cut)
        self.actionCopiar.triggered.connect(self.copy)
        self.actionPegar.triggered.connect(self.paste)
        
        self.actionNuevoArchivo.triggered.connect(self.newFile)
        self.actionGuardar_2.triggered.connect(self.saveFile)
        self.actionGuardarComo.triggered.connect(self.saveFileAs)
        self.actionAbrirArchivo.triggered.connect(self.openFile)
        self.actionCerrarArchivo.triggered.connect(self.closeFile)
        self.actionDeshacer_2.triggered.connect(self.undo)
        self.actionRehacer_2.triggered.connect(self.redo)
        
        self.actionAnalisis_sintactico.triggered.connect(self.sintax_analize)
        self.actionCompSintax.triggered.connect(self.sintax_analize)
        tree_view = self.tabCompilacion.findChild(QWidget, "tabSintactico").findChild(QTreeView, "txtSintactico")
        tree_view.setAlternatingRowColors(True)
        tree_view.setStyleSheet("QTreeView { alternate-background-color: #f0f0f0; }")
        tree_view.header().setDefaultAlignment(Qt.AlignCenter)
        tree_view.header().setStretchLastSection(True)
        tree_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        tree_view2 = self.tabCompilacion.findChild(QWidget, "tabSemantico").findChild(QTreeView, "txtSemantico")
        tree_view2.setAlternatingRowColors(True)
        tree_view2.setStyleSheet("QTreeView { alternate-background-color: #f0f0f0; }")
        tree_view2.header().setDefaultAlignment(Qt.AlignCenter)
        tree_view2.header().setStretchLastSection(True)
        tree_view2.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        
        self.listNumeroLinea = NoScrollTextEdit(self.centralwidget)
        self.listNumeroLinea.setReadOnly(True)
        self.listNumeroLinea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listNumeroLinea.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listNumeroLinea.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        
        self.listNumeroLinea.setMinimumWidth(40)
        self.listNumeroLinea.setMaximumWidth(40)
        
        self.textCodigoFuente.textChanged.connect(self.onTextChanged)
        self.textCodigoFuente.cursorPositionChanged.connect(self.onCursorChange)
        
        layoutPrincipal = QVBoxLayout(self.centralwidget)
        
        layoutArriba = QHBoxLayout()
        layoutArriba.addWidget(self.listNumeroLinea)
        layoutArriba.addWidget(self.textCodigoFuente)
        layoutArriba.addWidget(self.tabCompilacion)
        
        layoutAbajo = QHBoxLayout()
        layoutAbajo.addWidget(self.tabErroresResultado)
        self.tabErroresResultado.setMaximumHeight(170)
        
        layoutPrincipal.addLayout(layoutArriba)
        layoutPrincipal.addLayout(layoutAbajo)
        
        self.textCodigoFuente.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.textCodigoFuente.verticalScrollBar().valueChanged.connect(self.syncScrollBars)
        self.listNumeroLinea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.set_default_font_size()
        
        self.textCodigoFuente.textChanged.connect(self.analyzeText)
        
        self.band = 0
        
        self.token_formats = {
            'DOUBLE': QColor(45, 132, 214),
            'INT': QColor(45, 132, 214),
            'IDENTIFICADOR': QColor(141, 22, 184),
            'COMENTARIO': QColor(189, 189, 189),
            'IF': QColor(184, 22, 87),
            'ELSE': QColor(184, 22, 87),
            'DO': QColor(184, 22, 87),
            'WHILE': QColor(184, 22, 87),
            'UNTIL': QColor(184, 22, 87),
            'END': QColor(184, 22, 87),
            'SWITCH': QColor(184, 22, 87),
            'CASE': QColor(184, 22, 87),
            'INT': QColor(184, 22, 87),
            'REAL': QColor(184, 22, 87),
            'MAIN': QColor(184, 22, 87),
            'CIN': QColor(184, 22, 87),
            'COUT': QColor(184, 22, 87),
            'INC': QColor(227, 9, 9),
            'DEC': QColor(227, 9, 9),
            'MAS': QColor(227, 9, 9),
            'MENOS': QColor(227, 9, 9),
            'ENTRE': QColor(227, 9, 9),
            'POR': QColor(227, 9, 9),
            'MOD': QColor(227, 9, 9),
            'POT': QColor(227, 9, 9),
            'MORETHAN': QColor(2, 179, 8),
            'LESSTHAN': QColor(2, 179, 8),
            'MOREEQUALS': QColor(2, 179, 8),
            'LESSEQUALS': QColor(2, 179, 8),
            'EQUALS': QColor(2, 179, 8),
            'NOTEQUALS': QColor(2, 179, 8),
            'AND': QColor(184, 22, 87),
            'OR': QColor(184, 22, 87),
        }
    
    def restart_timer(self):
        self.timer.start()
    
    def analyzeText(self):
        text = self.textCodigoFuente.toPlainText()
        
        if not text:
            self.tabCompilacion.findChild(QWidget, "tabLexico").findChild(QTextEdit, "txtLexico").setHtml("")
            return
        
        try:
            if self.band == 0:
                cursor = self.textCodigoFuente.textCursor()
                self.band = 1
            
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(QTextCharFormat())
            cursor.clearSelection()
            
            lexer.input(text)
            
            lexemes = []
            while True:
                tok = lexer.token()
                if not tok:
                    break
                lexemes.append((tok.type, tok.value, tok.lineno, tok.lexpos))
                cursor.setPosition(tok.lexpos)
                start = tok.lexpos
                end = start + len(tok.value)
                if tok.type in self.token_formats:
                    self.apply_format(cursor, start, end, self.token_formats[tok.type])
            
            html_table = "<table style='border-collapse: collapse;' width='100%'><tr style='color: #1155d4; font-size: 15px'><th style='padding: 8px;'>Tipo</th><th style='padding: 8px;'>Valor</th><th style='padding: 8px;'>Línea</th><th style='padding: 8px;'>Posición</th></tr>"
            for lexeme in lexemes:
                html_table += f"<tr><td style='text-align: center; padding: 5px; font-weight: bold;'>{lexeme[0]}</td><td style='text-align: center; padding: 5px; font-weight: bold; color: #c4213f;'>{lexeme[1]}</td><td style='text-align: center; padding: 5px;'>{lexeme[2]}</td><td style='text-align: center; padding: 5px;'>{lexeme[3]}</td></tr>"
            html_table += "</table>"

            scroll_position = self.tabCompilacion.findChild(QWidget, "tabLexico").findChild(QTextEdit, "txtLexico").verticalScrollBar().value()
            self.tabCompilacion.findChild(QWidget, "tabLexico").findChild(QTextEdit, "txtLexico").setHtml(html_table)
            self.tabCompilacion.findChild(QWidget, "tabLexico").findChild(QTextEdit, "txtLexico").verticalScrollBar().setValue(scroll_position)
            self.band = 0
        except Exception as e:
            print("ERROR: ", e)
    
    def sintax_analize(self):
        global syntax_errors    
        text = self.textCodigoFuente.toPlainText()
                
        self.txtErroresSint.clear()
        
        result = parser.parse(text)
        print('ARBOL SINTACTICO:\n', result)
        
        self.show_syntax_tree(result)
        self.semantic_analize()
    
    def semantic_analize(self):
        analyzer = SemanticAnalyzer()
        analyzer.clean_temp_sym_table()
        text = self.textCodigoFuente.toPlainText()
        result = parser.parse(text)
        annotated_tree = analyzer.analyze(result)
        annotated_root = analyzer.build_annotated_tree(annotated_tree)
        tree_view2 = self.tabCompilacion.findChild(QWidget, "tabSemantico").findChild(QTreeView, "txtSemantico")
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Árbol Sintáctico con Anotaciones'])

        model.appendRow(annotated_root)

        scroll_position = self.tabCompilacion.findChild(QWidget, "tabHash").findChild(QTextEdit, "txtHash").verticalScrollBar().value()
        self.tabCompilacion.findChild(QWidget, "tabHash").findChild(QTextEdit, "txtHash").setHtml(analyzer.print_symbol_table())
        self.tabCompilacion.findChild(QWidget, "tabHash").findChild(QTextEdit, "txtHash").verticalScrollBar().setValue(scroll_position)
        
        tree_view2.setModel(model)
        tree_view2.expandAll()

        tree_view2.setAlternatingRowColors(True)
        tree_view2.setStyleSheet("QTreeView { alternate-background-color: #f0f0f0; }")
        tree_view2.header().setDefaultAlignment(Qt.AlignCenter)
        tree_view2.header().setStretchLastSection(True)
        tree_view2.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        errors = analyzer.print_errors()
        if errors:
            errors = "\n".join(errors)
        else:
            errors = ""
        self.tabErroresResultado.findChild(QWidget, "tabErrorSemantico").findChild(QPlainTextEdit, "txtErroresSemantico").setPlainText(errors)
    
    def show_syntax_tree(self, tree):
        tree_view = self.tabCompilacion.findChild(QWidget, "tabSintactico").findChild(QTreeView, "txtSintactico")
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(['Árbol Sintáctico'])

        root_item = self.add_items(tree)
        model.appendRow(root_item)

        tree_view.setModel(model)
        tree_view.expandAll()

        tree_view.setAlternatingRowColors(True) 
        tree_view.setStyleSheet("QTreeView { alternate-background-color: #f0f0f0; }")
        tree_view.header().setDefaultAlignment(Qt.AlignCenter)
        tree_view.header().setStretchLastSection(True)
        tree_view.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        
    def add_items(self, element):
        if element is None:
            return None

        if isinstance(element, tuple):
            item = QStandardItem(str(element[0]))
            for child in element[1:]:
                child_item = self.add_items(child)
                if child_item is not None: 
                    item.appendRow(child_item)
        elif isinstance(element, list):
            item = QStandardItem("lista_declaraciones")
            for subelement in element:
                subitem = self.add_items(subelement)
                if subitem is not None: 
                    item.appendRow(subitem)
        else:
            item = QStandardItem(str(element))
        return item
    
    def show_syntax_errors(self):
        global syntax_errors
        error_text = "\n".join(syntax_errors)
        self.tabErroresResultado.findChild(QWidget, "tabErrorSintactico").findChild(QPlainTextEdit, "txtErroresSintactico").setPlainText(error_text)


    def apply_format(self, cursor, start, end, color):
        format = QTextCharFormat()
        format.setForeground(color)
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, end - start)
        cursor.setCharFormat(format)

    def syncScrollBars(self):
        value = self.textCodigoFuente.verticalScrollBar().value()
        self.listNumeroLinea.verticalScrollBar().setValue(value)
        
    def newFile(self):
        self.textCodigoFuente.clear()
        self.textCodigoFuente.setReadOnly(False)
        self.setWindowTitle("Compilador - Untitled")
        self.current_path = None
        
    def saveFile(self):
        if self.current_path is not None:
            fileText = self.textCodigoFuente.toPlainText()
            with open(self.current_path, 'w') as f:
                f.write(fileText)
        else:
            self.saveFileAs()
        
    def saveFileAs(self):
        try:
            documents_folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            pathName = QFileDialog.getSaveFileName(self, 'Save File', documents_folder, 'Text files (*.txt)')
            fileText = self.textCodigoFuente.toPlainText()
            with open(pathName[0], 'w') as f:
                f.write(fileText)
            self.current_path = pathName[0]
            self.setWindowTitle(pathName[0])
        except Exception as e:
            print(f"Error al abrir el archivo: {e}")
            
    def openFile(self):
        try:
            self.textCodigoFuente.setReadOnly(False)
            documents_folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            fname = QFileDialog.getOpenFileName(self, 'Open File', documents_folder, 'Text files (*.txt)')
            self.setWindowTitle("Compilador - " + fname[0])
            with open(fname[0], 'r') as f:
                fileText = f.read()
                self.textCodigoFuente.setText(fileText)
            self.current_path = fname[0]
        except Exception as e:
            print(f"Error al abrir el archivo: {e}")
            
    def closeFile(self):
        self.textCodigoFuente.clear()
        self.setWindowTitle("Compilador")
        self.listNumeroLinea.setPlainText("")
    def undo(self):
        self.textCodigoFuente.undo()
    def redo(self):
        self.textCodigoFuente.redo()
    def cut(self):
        self.textCodigoFuente.cut()
    def copy(self):
        self.textCodigoFuente.copy()
    def paste(self):
        self.textCodigoFuente.paste()
        
    def onTextChanged(self):
        text = self.textCodigoFuente.toPlainText()
        lines = text.split('\n')
        if len(lines) != len(self.line_numbers):
            self.line_numbers = list(range(1, len(lines) + 1))
            self.updateLineNumbers()
            
    def onCursorChange(self):
        cursor = self.textCodigoFuente.textCursor()
        block_number = cursor.blockNumber() + 1
        column_number = cursor.columnNumber()
        self.statusbar.showMessage("Linea: " + str(block_number) + " Columna: " + str(column_number))
        

    def updateLineNumbers(self):
        self.listNumeroLinea.blockSignals(True)
        scroll_position = self.listNumeroLinea.verticalScrollBar().value()
        self.listNumeroLinea.clear()
        lines = len(self.line_numbers)
        line_numbers = '\n'.join(str(i + 1) for i in range(lines))
        self.listNumeroLinea.setPlainText(line_numbers)
        self.listNumeroLinea.verticalScrollBar().setValue(scroll_position)
        self.listNumeroLinea.blockSignals(False)

    def set_default_font_size(self):
        font = self.textCodigoFuente.font()
        font.setPointSize(self.current_fontSize)
        self.textCodigoFuente.setFont(font)

        lineNumberFont = self.listNumeroLinea.font()
        lineNumberFont.setFamily("Consolas")
        lineNumberFont.setPointSize(self.current_fontSize)
        self.listNumeroLinea.setFont(lineNumberFont)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec())

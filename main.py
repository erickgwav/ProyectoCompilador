from PyQt5.QtCore import Qt, QStandardPaths
from PyQt5.QtGui import QTextCharFormat, QColor, QTextCursor, QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, QTextEdit, QPlainTextEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QWidget, QTreeView, QHeaderView, QInputDialog
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

class CodeGenerator:
    def __init__(self):
        self.code_p = []
        self.label_counter = 0

    def generate_code(self, syntax_tree):
        self.code_p = []
        self.label_counter = 0
        self.traverse_tree(syntax_tree)
        return self.code_p

    def new_label(self):
        label = f"LABEL_{self.label_counter}"
        self.label_counter += 1
        return label

    def traverse_tree(self, node):
        if not node:
            return

        if isinstance(node, tuple):
            node_type = node[0]

            if node_type == 'programa':
                for declaration in node[1]:
                    self.traverse_tree(declaration)

            elif node_type == '=':
                var_name = node[1]
                expr = node[2]
                self.traverse_tree(expr)
                self.code_p.append(f"STORE {var_name}")

            elif node_type in ('+', '-', '*', '/', '%'):
                self.traverse_tree(node[1])
                self.traverse_tree(node[2])
                operation = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV', '%': 'MOD'}[node_type]
                self.code_p.append(operation)

            elif node_type == 'if-else':
                self.traverse_tree(node[1])  # Condición
                label_else = self.new_label()
                self.code_p.append(f"JMPZ {label_else}")
                self.traverse_tree(node[2])  # Rama if
                label_end = self.new_label()
                self.code_p.append(f"JMP {label_end}")
                self.code_p.append(f"{label_else}:")
                self.traverse_tree(node[3])  # Rama else
                self.code_p.append(f"{label_end}:")

            elif node_type == 'while':
                label_start = self.new_label()
                self.code_p.append(f"{label_start}:")
                self.traverse_tree(node[1])  # Condición
                label_end = self.new_label()
                self.code_p.append(f"JMPZ {label_end}")
                self.traverse_tree(node[2])  # Cuerpo
                self.code_p.append(f"JMP {label_start}")
                self.code_p.append(f"{label_end}:")

            elif node_type == 'do-until':
                label_start = self.new_label()
                self.code_p.append(f"{label_start}:")
                self.traverse_tree(node[1])  # Cuerpo
                self.traverse_tree(node[2])  # Condición
                self.code_p.append(f"JMPZ {label_start}")

            elif node_type == 'cout':
                if isinstance(node[1], str) and node[1].startswith('"') and node[1].endswith('"'):
                    # Es un literal de texto
                    self.code_p.append(f'PUSH {node[1]}')
                else:
                    # Es una variable o expresión
                    self.traverse_tree(node[1])
                self.code_p.append("PRINT")

            elif node_type == 'cin':
                var_name = node[1]
                self.code_p.append(f"CIN {var_name}")


            elif node_type == 'relacion':
                # Relación como '>', '<', '==', etc.
                self.traverse_tree(node[2][0])  # Lado izquierdo
                self.traverse_tree(node[2][1])  # Lado derecho
                operador = {
                    '>': 'GT',
                    '<': 'LT',
                    '>=': 'GE',
                    '<=': 'LE',
                    '==': 'EQ',
                    '!=': 'NE'
                }[node[1]]
                self.code_p.append(operador)

            elif node_type == 'incremento':
                var_name = node[1]
                self.code_p.append(f"LOAD {var_name}")
                self.code_p.append("PUSH 1")
                self.code_p.append("ADD")
                self.code_p.append(f"STORE {var_name}")

            elif node_type == 'decremento':
                var_name = node[1]
                self.code_p.append(f"LOAD {var_name}")
                self.code_p.append("PUSH 1")
                self.code_p.append("SUB")
                self.code_p.append(f"STORE {var_name}")


        elif isinstance(node, list):
            for element in node:
                self.traverse_tree(element)

        elif isinstance(node, str):
            if node.isdigit() or node.replace('.', '', 1).isdigit():
                self.code_p.append(f"PUSH {node}")
            else:
                self.code_p.append(f"LOAD {node}")


class StackMachine:
    def __init__(self):
        self.stack = []
        self.variables = {}
        self.output = []
        self.errors = []

    def execute(self, code_p):
        pc = 0
        labels = {line.split(':', 1)[0]: idx for idx, line in enumerate(code_p) if line.strip().endswith(':')}
        while pc < len(code_p):
            try:
                instruction = code_p[pc]
                parts = instruction.split()
                command = parts[0]

                print(f"Instrucción: {instruction}")
                print(f"Pila antes: {self.stack}")
                print(f"Variables: {self.variables}")

                if command == "PUSH":
                    value = " ".join(parts[1:])
                    if value.startswith('"') and value.endswith('"'):
                        # Es una cadena de texto
                        self.stack.append(value.strip('"'))
                    elif value in self.variables:
                        # Es una variable
                        self.stack.append(self.variables[value])
                    else:
                        # Es un número
                        self.stack.append(float(value) if '.' in value else int(value))


                elif command == "LOAD":
                    var_name = parts[1]
                    if var_name not in self.variables:
                        raise KeyError(f"Variable no inicializada: {var_name}")
                    self.stack.append(self.variables[var_name])

                elif command == "STORE":
                    var_name = parts[1]
                    if not self.stack:
                        raise IndexError("Pila vacía durante operación STORE.")
                    self.variables[var_name] = self.stack.pop()

                elif command == "PRINT":
                    if not self.stack:
                        raise IndexError("Pila vacía durante operación PRINT.")
                    value = self.stack.pop()
                    if isinstance(value, (int, float)):
                        self.output.append(str(value))
                    else:
                        self.output.append(value)

                elif command == "CIN":
                    print(f"Solicitando entrada para la variable '{parts[1]}'")
                    var_name = parts[1]
                    if hasattr(self, "input_callback"):
                        input_value = self.input_callback(var_name)
                        try:
                            self.variables[var_name] = float(input_value) if '.' in input_value else int(input_value)
                            print(f"Entrada recibida: {input_value}")
                        except ValueError:
                            raise ValueError(f"Entrada inválida para la variable '{var_name}': {input_value}")
                    else:
                        raise ValueError("No se configuró ningún callback para manejar la entrada.")

                elif command in ("ADD", "SUB", "MUL", "DIV", "MOD"):
                    if len(self.stack) < 2:
                        raise IndexError(f"Pila insuficiente para operación {command}.")
                    b = self.stack.pop()
                    a = self.stack.pop()
                    result = {
                        "ADD": a + b,
                        "SUB": a - b,
                        "MUL": a * b,
                        "DIV": a / b if b != 0 else 0,
                        "MOD": a % b,
                    }[command]
                    self.stack.append(result)

                elif command in ("GT", "LT", "GE", "LE", "EQ", "NE"):
                    if len(self.stack) < 2:
                        raise IndexError(f"Pila insuficiente para operación {command}.")
                    b = self.stack.pop()
                    a = self.stack.pop()
                    result = {
                        "GT": a > b,
                        "LT": a < b,
                        "GE": a >= b,
                        "LE": a <= b,
                        "EQ": a == b,
                        "NE": a != b
                    }[command]
                    self.stack.append(1 if result else 0)

                elif command == "JMP":
                    if parts[1] not in labels:
                        raise ValueError(f"Etiqueta no encontrada: {parts[1]}")
                    pc = labels[parts[1]]
                    continue

                elif command == "JMPZ":
                    if not self.stack:
                        raise IndexError("Pila vacía durante operación JMPZ.")
                    if not self.stack.pop():
                        if parts[1] not in labels:
                            raise ValueError(f"Etiqueta no encontrada: {parts[1]}")
                        pc = labels[parts[1]]
                        continue

                elif instruction.endswith(":"):
                    pass  # Etiquetas

                else:
                    raise ValueError(f"Instrucción desconocida: {command}")

                print(f"Pila después: {self.stack}")
                print(f"Salida: {self.output}")

                pc += 1

            except Exception as e:
                error_message = f"Error en ejecución: {e}"
                print(error_message)
                self.errors.append(error_message)  # Agregar error a la lista
                break

        return self.output


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
        self.generate_and_execute_code()
    
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

        self.tabCompilacion.findChild(QWidget, "tabHash").findChild(QTextEdit, "txtHash").setHtml(analyzer.print_symbol_table())
        
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

    def generate_and_execute_code(self):
        text = self.textCodigoFuente.toPlainText()
        try:
            syntax_tree = parser.parse(text)
            if not syntax_tree:
                raise ValueError("Árbol sintáctico no generado. Revisa el código fuente.")
            print("Árbol Sintáctico:", syntax_tree)

            # Generar código P
            code_generator = CodeGenerator()
            code_p = code_generator.generate_code(syntax_tree)

            # Ejecutar código P
            stack_machine = StackMachine()
            stack_machine.input_callback = self.input_callback
            result_output = stack_machine.execute(code_p)

            error_widget = self.tabErroresResultado.findChild(QWidget, "tabErroresEjecucion").findChild(QPlainTextEdit, "txtErroresEjecucion")
            if stack_machine.errors:
                errors = "\n".join(stack_machine.errors)
                error_widget.setPlainText(errors)
            else:
                error_widget.setPlainText("Sin errores en ejecución.")

            # Mostrar resultados
            self.tabCompilacion.findChild(QWidget, "tabCodigoP").findChild(QTextEdit, "txtCodigoP").setPlainText("\n".join(code_p))
            self.tabCompilacion.findChild(QWidget, "tabResultados").findChild(QTextEdit, "txtResultados").setPlainText("\n".join(map(str, result_output)))

        except Exception as e:
            print(f"Error: {e}")

    def input_callback(self, var_name):
        # Muestra un mensaje en txtResultados pidiendo un valor
        value, ok = QInputDialog.getText(self, "Entrada requerida", f"Ingrese un valor para '{var_name}':")
        if ok:
            return value
        else:
            raise ValueError(f"Se canceló la entrada para la variable '{var_name}'")

    
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

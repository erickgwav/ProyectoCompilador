from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtGui import QTextOption, QIcon, QTextCharFormat, QColor, QTextCursor, QPalette
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QTextEdit, QHBoxLayout, QVBoxLayout, QSizePolicy, QLabel, QGridLayout
from PyQt6 import uic
from lexer import lexer, errores
import sys
import io
import os

class NoScrollTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(NoScrollTextEdit, self).__init__(parent)
    def wheelEvent(self, event):
        # Bloquea el evento de la rueda del mouse
        pass

class LexicalAnalyzer:
    def __init__(self):
        # Colores para resaltar los tokens
        self.colors = {
            "ENTERO": QColor(45, 132, 214),
            "REAL": QColor(45, 132, 214),
            "IDENTIFICADOR": QColor(141, 22, 184),
            "OPERADOR_ARITMETICO": QColor(227, 9, 9),
            "OPERADOR_RELACIONAL": QColor(2, 179, 8),
            "PALABRA_CLAVE": QColor(184, 22, 87),
            "OPERADOR_LOGICO": QColor(184, 22, 87),
            "COMENTARIO": QColor(189, 189, 189),
            "COMENTARIO_MULTILINEA": QColor(189, 189, 189),
        }

    def analyze(self, textEdit, outputTextEdit):
        text = textEdit.toPlainText()
        cursor = textEdit.textCursor()

        # Guardar la posición actual de la barra de desplazamiento
        scroll_bar_value = outputTextEdit.verticalScrollBar().value()

        # Reiniciar el lexer
        lexer.input(text)

         # Construir la tabla HTML
        html_table = "<table style='border-collapse: collapse;' width='100%'><tr style='color: #1155d4; font-size: 15px'><th style='padding: 8px;'>Tipo</th><th style='padding: 8px;'>Valor</th><th style='padding: 8px;'>Línea</th><th style='padding: 8px;'>Columna</th></tr>"

        # Obtener el siguiente token
        while True:
            tok = lexer.token()
            if not tok:
                break  # No hay más tokens

            # Obtener la posición del cursor para calcular la columna del token
            cursor.setPosition(tok.lexpos)
            line_number = cursor.blockNumber() + 1
                
            if(tok.type != 'COMENTARIO' and tok.type != 'COMENTARIO_MULTILINEA'):
                # Construir una fila de la tabla para el token actual
                html_row = f"<tr><td style='text-align: center; padding: 5px; font-weight: bold;'>{tok.type}</td><td style='text-align: center; padding: 5px; font-weight: bold; color: #c4213f;'>{tok.value}</td><td style='text-align: center; padding: 5px;'>{line_number}</td><td style='text-align: center; padding: 5px;'>{self.find_column(text, tok)}</td></tr>"
                html_table += html_row
            
            start = tok.lexpos
            end = start + len(tok.value)
            # Aplicar formato solo si el tipo de token tiene un color definido
            if tok.type in self.colors:
                self.apply_format(cursor, start, end, self.colors[tok.type])

         # Cerrar la tabla
        html_table += "</table>"

        # Guardar la posición del cursor antes de cambiar el contenido
        cursor_position = outputTextEdit.textCursor().position()

        # Insertar la tabla HTML en el QTextEdit
        outputTextEdit.setHtml(html_table)

        # Restaurar la posición del cursor después de cambiar el contenido
        cursor = outputTextEdit.textCursor()
        cursor.setPosition(cursor_position)
        outputTextEdit.setTextCursor(cursor)

        # Restaurar la posición de la barra de desplazamiento
        outputTextEdit.verticalScrollBar().setValue(scroll_bar_value)

        outputTextEdit.adjustSize()
        outputTextEdit.setMinimumSize(711, 450)

    def apply_format(self, cursor, start, end, color):
        format = QTextCharFormat()
        format.setForeground(color)
        cursor.setPosition(start)
        cursor.movePosition(QTextCursor.MoveOperation.Right, QTextCursor.MoveMode.KeepAnchor, end - start)
        cursor.setCharFormat(format)

    def find_column(self, text, token):
        line_start = text.rfind('\n', 0, token.lexpos) + 1
        return (token.lexpos - line_start) + 1

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        template = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>MainWindow</class>
 <widget class="QMainWindow" name="MainWindow">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1709</width>
    <height>881</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>MainWindow</string>
  </property>
  <widget class="QWidget" name="centralwidget">
   <widget class="QTextEdit" name="textEdit">
    <property name="geometry">
     <rect>
      <x>60</x>
      <y>30</y>
      <width>751</width>
      <height>581</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <family>Consolas</family>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="readOnly">
     <bool>true</bool>
    </property>
    <property name="placeholderText">
     <string/>
    </property>
   </widget>
   <widget class="QTextEdit" name="textEdit_2">
    <property name="geometry">
     <rect>
      <x>10</x>
      <y>30</y>
      <width>41</width>
      <height>571</height>
     </rect>
    </property>
    <property name="font">
     <font>
      <family>Consolas</family>
      <pointsize>10</pointsize>
     </font>
    </property>
    <property name="lineWrapMode">
     <enum>QTextEdit::NoWrap</enum>
    </property>
    <property name="readOnly">
     <bool>true</bool>
    </property>
   </widget>
   <widget class="QTabWidget" name="tabWidget">
    <property name="geometry">
     <rect>
      <x>830</x>
      <y>30</y>
      <width>751</width>
      <height>581</height>
     </rect>
    </property>
    <property name="currentIndex">
     <number>0</number>
    </property>
    <widget class="QWidget" name="tabLexico">
     <attribute name="title">
      <string>Lexico</string>
     </attribute>
     <widget class="QTextEdit" name="textLexico">
      <property name="geometry">
       <rect>
        <x>10</x>
        <y>10</y>
        <width>711</width>
        <height>491</height>
       </rect>
      </property>
      <property name="readOnly">
       <bool>true</bool>
      </property>
     </widget>
    </widget>
    <widget class="QWidget" name="tabSintactico">
     <attribute name="title">
      <string>Sintactico</string>
     </attribute>
     <widget class="QTextEdit" name="textSintactico">
      <property name="geometry">
       <rect>
        <x>10</x>
        <y>10</y>
        <width>671</width>
        <height>531</height>
       </rect>
      </property>
      <property name="readOnly">
       <bool>true</bool>
      </property>
     </widget>
    </widget>
    <widget class="QWidget" name="tabSemantico">
     <attribute name="title">
      <string>Semántico</string>
     </attribute>
     <widget class="QTextEdit" name="textSemantico">
      <property name="geometry">
       <rect>
        <x>10</x>
        <y>10</y>
        <width>671</width>
        <height>531</height>
       </rect>
      </property>
      <property name="readOnly">
       <bool>true</bool>
      </property>
     </widget>
    </widget>
    <widget class="QWidget" name="tabHashTable">
     <attribute name="title">
      <string>Hash Table</string>
     </attribute>
     <widget class="QTextEdit" name="textHashTable">
      <property name="geometry">
       <rect>
        <x>10</x>
        <y>10</y>
        <width>671</width>
        <height>531</height>
       </rect>
      </property>
     </widget>
    </widget>
    <widget class="QWidget" name="tabInterCode">
     <attribute name="title">
      <string>CodigoIntermedio</string>
     </attribute>
     <widget class="QTextEdit" name="textInterCode">
      <property name="geometry">
       <rect>
        <x>10</x>
        <y>10</y>
        <width>671</width>
        <height>531</height>
       </rect>
      </property>
     </widget>
    </widget>
   </widget>
   <widget class="QTabWidget" name="tabWidget_2">
    <property name="geometry">
     <rect>
      <x>0</x>
      <y>640</y>
      <width>1521</width>
      <height>191</height>
     </rect>
    </property>
    <property name="currentIndex">
     <number>0</number>
    </property>
    <widget class="QWidget" name="tabErroresLex">
     <attribute name="title">
      <string>Errores</string>
     </attribute>
     <widget class="QTextEdit" name="textErrores">
      <property name="geometry">
       <rect>
        <x>10</x>
        <y>10</y>
        <width>1491</width>
        <height>131</height>
       </rect>
      </property>
      <property name="readOnly">
       <bool>true</bool>
      </property>
     </widget>
    </widget>
   </widget>
  </widget>
  <widget class="QStatusBar" name="statusbar"/>
  <widget class="QToolBar" name="toolBar">
   <property name="windowTitle">
    <string>toolBar</string>
   </property>
   <attribute name="toolBarArea">
    <enum>TopToolBarArea</enum>
   </attribute>
   <attribute name="toolBarBreak">
    <bool>false</bool>
   </attribute>
   <addaction name="iconNew"/>
   <addaction name="iconOpen"/>
   <addaction name="iconSave"/>
   <addaction name="iconClose"/>
  </widget>
  <widget class="QMenuBar" name="menubar">
   <property name="geometry">
    <rect>
     <x>0</x>
     <y>0</y>
     <width>1709</width>
     <height>26</height>
    </rect>
   </property>
   <property name="nativeMenuBar">
    <bool>false</bool>
   </property>
   <widget class="QMenu" name="menuFile">
    <property name="title">
     <string>File</string>
    </property>
    <addaction name="actionNew"/>
    <addaction name="actionOpen"/>
    <addaction name="actionClose"/>
    <addaction name="separator"/>
    <addaction name="actionSave"/>
    <addaction name="actionSave_As"/>
   </widget>
   <widget class="QMenu" name="menuEdit">
    <property name="title">
     <string>Edit</string>
    </property>
    <addaction name="actionUndo"/>
    <addaction name="actionRedo"/>
    <addaction name="separator"/>
    <addaction name="actionCopy"/>
    <addaction name="actionPaste"/>
    <addaction name="actionCut"/>
   </widget>
   <widget class="QMenu" name="menuBuild_and_Debug">
    <property name="title">
     <string>Build and Debug</string>
    </property>
   </widget>
   <widget class="QMenu" name="menuAppearance">
    <property name="title">
     <string>Appearance</string>
    </property>
    <addaction name="actionSet_Dark_Mode"/>
    <addaction name="actionSet_Light_Mode"/>
    <addaction name="separator"/>
    <addaction name="actionIncrease_Font_Size"/>
    <addaction name="actionDecrease_Font_Size"/>
   </widget>
   <widget class="QMenu" name="menuLexico">
    <property name="title">
     <string>Lexico</string>
    </property>
   </widget>
   <widget class="QMenu" name="menuSintactico">
    <property name="title">
     <string>Sintactico</string>
    </property>
   </widget>
   <widget class="QMenu" name="menuSemantico">
    <property name="title">
     <string>Semantico</string>
    </property>
   </widget>
   <widget class="QMenu" name="menuCompilar">
    <property name="title">
     <string>Compilar</string>
    </property>
   </widget>
   <addaction name="menuFile"/>
   <addaction name="menuEdit"/>
   <addaction name="menuBuild_and_Debug"/>
   <addaction name="menuAppearance"/>
   <addaction name="menuLexico"/>
   <addaction name="menuSintactico"/>
   <addaction name="menuSemantico"/>
   <addaction name="menuCompilar"/>
  </widget>
  <action name="actionNew">
   <property name="icon">
    <iconset>
     <normaloff>images/new.png</normaloff>images/new.png</iconset>
   </property>
   <property name="text">
    <string>New</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+N</string>
   </property>
  </action>
  <action name="actionSave">
   <property name="icon">
    <iconset>
     <normaloff>images/save.png</normaloff>images/save.png</iconset>
   </property>
   <property name="text">
    <string>Save</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+S</string>
   </property>
  </action>
  <action name="actionOpen">
   <property name="icon">
    <iconset>
     <normaloff>images/open.png</normaloff>images/open.png</iconset>
   </property>
   <property name="text">
    <string>Open</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+O</string>
   </property>
  </action>
  <action name="actionSave_As">
   <property name="text">
    <string>Save As</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+Shift+S</string>
   </property>
  </action>
  <action name="actionUndo">
   <property name="text">
    <string>Undo</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+Z</string>
   </property>
  </action>
  <action name="actionRedo">
   <property name="text">
    <string>Redo</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+Y</string>
   </property>
  </action>
  <action name="actionCopy">
   <property name="text">
    <string>Copy</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+C</string>
   </property>
  </action>
  <action name="actionPaste">
   <property name="text">
    <string>Paste</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+V</string>
   </property>
  </action>
  <action name="actionCut">
   <property name="text">
    <string>Cut</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+X</string>
   </property>
  </action>
  <action name="actionChange_Font_Size">
   <property name="text">
    <string>Change Font Size</string>
   </property>
  </action>
  <action name="actionSet_Dark_Mode">
   <property name="text">
    <string>Set Dark Mode</string>
   </property>
  </action>
  <action name="actionSet_Light_Mode">
   <property name="text">
    <string>Set Light Mode</string>
   </property>
  </action>
  <action name="actionIncrease_Font_Size">
   <property name="text">
    <string>Increase Font Size</string>
   </property>
   <property name="shortcut">
    <string>Ctrl++</string>
   </property>
  </action>
  <action name="actionDecrease_Font_Size">
   <property name="text">
    <string>Decrease Font Size</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+_</string>
   </property>
  </action>
  <action name="actionClose">
   <property name="icon">
    <iconset>
     <normaloff>images/close.png</normaloff>images/close.png</iconset>
   </property>
   <property name="text">
    <string>Close</string>
   </property>
   <property name="shortcut">
    <string>Ctrl+F4</string>
   </property>
  </action>
  <action name="iconNew">
   <property name="icon">
    <iconset>
     <normaloff>images/new.png</normaloff>images/new.png</iconset>
   </property>
   <property name="text">
    <string>e</string>
   </property>
  </action>
  <action name="iconSave">
   <property name="icon">
    <iconset>
     <normaloff>images/save.png</normaloff>images/save.png</iconset>
   </property>
   <property name="text">
    <string>s</string>
   </property>
  </action>
  <action name="iconOpen">
   <property name="icon">
    <iconset>
     <normaloff>images/open.png</normaloff>images/open.png</iconset>
   </property>
   <property name="text">
    <string>o</string>
   </property>
  </action>
  <action name="iconClose">
   <property name="icon">
    <iconset>
     <normaloff>images/close.png</normaloff>images/close.png</iconset>
   </property>
   <property name="text">
    <string>c</string>
   </property>
  </action>
 </widget>
 <resources/>
 <connections/>
</ui>
"""

        f = io.StringIO(template)
        uic.loadUi(f, self)

        # Ruta actual del archivo
        self.current_path = None
        # Tamaño de la fuente
        self.current_fontSize = 12
        # Titulo de la ventana
        self.setWindowTitle("Compilador")
        # Iniciar en pantalla completa
        self.showMaximized() 
         # Lista para mantener un seguimiento de los errores ya mostrados
        self.displayed_errors = set()

        # Se conectan las opciones del menú con las funciones
        self.actionNew.triggered.connect(self.newFile)
        self.actionSave.triggered.connect(self.saveFile)
        self.actionSave_As.triggered.connect(self.saveFileAs)
        self.actionOpen.triggered.connect(self.openFile)
        self.actionClose.triggered.connect(self.closeFile)
        self.actionUndo.triggered.connect(self.undo)
        self.actionRedo.triggered.connect(self.redo)
        self.actionCut.triggered.connect(self.cut)
        self.actionCopy.triggered.connect(self.copy)
        self.actionPaste.triggered.connect(self.paste)
        self.actionIncrease_Font_Size.triggered.connect(self.increaseFontSize)
        self.actionDecrease_Font_Size.triggered.connect(self.decreaseFontSize)
        self.actionSet_Dark_Mode.triggered.connect(self.setDarkMode)
        self.actionSet_Light_Mode.triggered.connect(self.setLightMode)
        self.iconNew.triggered.connect(self.newFile)
        self.iconOpen.triggered.connect(self.openFile)
        self.iconClose.triggered.connect(self.closeFile)
        self.iconSave.triggered.connect(self.saveFile)

        
        icon_path = os.path.join(os.path.dirname(__file__), 'images')
        self.iconNew.setIcon(QIcon(os.path.join(icon_path, 'new.png')))
        self.iconSave.setIcon(QIcon(os.path.join(icon_path, 'save.png')))
        self.iconOpen.setIcon(QIcon(os.path.join(icon_path, 'open.png')))
        self.iconClose.setIcon(QIcon(os.path.join(icon_path, 'close.png')))
        self.actionNew.setIcon(QIcon(os.path.join(icon_path, 'new.png')))
        self.actionSave.setIcon(QIcon(os.path.join(icon_path, 'save.png')))
        self.actionOpen.setIcon(QIcon(os.path.join(icon_path, 'open.png')))
        self.actionClose.setIcon(QIcon(os.path.join(icon_path, 'close.png')))

        # Agrega el QPlainTextEdit para los números de línea
        self.lineNumberTextEdit = NoScrollTextEdit(self.centralwidget)
        self.lineNumberTextEdit.setReadOnly(True)
        self.lineNumberTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.lineNumberTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Establece el tamaño mínimo y máximo del ancho del widget
        self.lineNumberTextEdit.setMinimumWidth(40)
        self.lineNumberTextEdit.setMaximumWidth(40)

        # Establece la política de expansión horizontal del widget
        self.lineNumberTextEdit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Añade los números de línea al QTextEdit
        line_numbers = '\n'.join(str(i + 1) for i in range(5000))  # Cambia 100 al número máximo de líneas posible
        self.lineNumberTextEdit.setPlainText(line_numbers)
        layoutPrincipal = QVBoxLayout(self.centralwidget)

        # Aplicar tamaño de fuente por defecto
        self.set_default_font_size()

        # Primer QHBoxLayout para lineNumberTextEdit, textEdit y tabWidget
        layoutArriba = QHBoxLayout()
        layoutArriba.addWidget(self.lineNumberTextEdit)
        layoutArriba.addWidget(self.textEdit)
        layoutArriba.addWidget(self.tabWidget)

        # Segundo QHBoxLayout para tabWidget_2
        layoutAbajo = QHBoxLayout()
        layoutAbajo.addWidget(self.tabWidget_2)
        self.tabWidget_2.setMaximumHeight(170)

        # Agrega los subdiseños al diseño principal
        layoutPrincipal.addLayout(layoutArriba)
        layoutPrincipal.addLayout(layoutAbajo)

        # Sincroniza el scroll entre textEdit y lineNumberTextEdit
        self.textEdit.verticalScrollBar().valueChanged.connect(self.syncScrollBars)

        # Deshabilita el scroll manual en lineNumberTextEdit
        self.lineNumberTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Contador de líneas
        self.line_count_label = QLabel()
        # Contador de columnas
        self.column_count_label = QLabel()
        # Contador de errores
        self.error_count_label = QLabel()

        # Crea el layout de la cuadrícula y agrega los contadores
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.line_count_label, 0, 0)
        grid_layout.addWidget(self.column_count_label, 0, 1)
        grid_layout.addWidget(self.error_count_label, 0, 2)
        layoutPrincipal.addLayout(grid_layout)

        # Actualizar contador de líneas
        self.textEdit.cursorPositionChanged.connect(self.update_cursor_position)

        # Deshabilita el ajuste de palabras y habilita la barra de desplazamiento horizontal
        self.textEdit.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self.textEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

        # Instanciar el analizador léxico
        self.lexical_analyzer = LexicalAnalyzer()

        # Conectar el evento de cambio de texto al analizador léxico
        self.textEdit.textChanged.connect(self.analyze_text)
        self.last_text = ""

                # Obtener la paleta actual del QTextEdit
        palette = self.textErrores.palette()

        # Establecer el color del texto en rojo
        palette.setColor(QPalette.ColorRole.Text, QColor("red"))

        # Aplicar la paleta actualizada al QTextEdit
        self.textErrores.setPalette(palette)

    def analyze_text(self):
        # Desconectar temporalmente el evento textChanged
        self.textEdit.textChanged.disconnect(self.analyze_text)

        # Limpiar el formato existente antes de aplicar uno nuevo
        cursor = self.textEdit.textCursor()
        cursor.select(QTextCursor.SelectionType.Document)
        cursor.setCharFormat(QTextCharFormat())  # Borrar formato existente
        cursor.clearSelection()

        # Llamar al analizador léxico solo si el texto ha cambiado
        if self.textEdit.toPlainText() != self.last_text:
            self.last_text = self.textEdit.toPlainText()
            self.lexical_analyzer.analyze(self.textEdit, self.textLexico)

            # Mostrar errores en textErrores
            for error in errores:
                if error not in self.displayed_errors:
                    self.textErrores.insertPlainText(error)
                    self.textErrores.insertPlainText("\n")  # Agregar una línea en blanco entre cada error
                    self.displayed_errors.add(error)

            # Limpiar la lista de errores
            errores.clear()
        # Volver a conectar el evento textChanged
        self.textEdit.textChanged.connect(self.analyze_text)

    def syncScrollBars(self):
        # Obtiene el valor actual de la barra de desplazamiento vertical de textEdit
        value = self.textEdit.verticalScrollBar().value()

        # Establece el mismo valor en la barra de desplazamiento vertical de lineNumberTextEdit
        self.lineNumberTextEdit.verticalScrollBar().setValue(value)

    # Crear nuevo archivo
    def newFile(self):
        self.textEdit.clear()
        self.textErrores.clear()
        self.textEdit.setReadOnly(False)
        self.setWindowTitle("Untitled")
        self.current_path = None

    def saveFile(self):
        if self.current_path is not None:
            fileText = self.textEdit.toPlainText()
            with open(self.current_path, 'w') as f:
                f.write(fileText)
        else:
            self.saveFileAs()
    
    # Guardar el archivo como
    def saveFileAs(self):
        try:
            documents_folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            pathName = QFileDialog.getSaveFileName(self, 'Save File', documents_folder, 'Text files (*.txt)')
            fileText = self.textEdit.toPlainText()
            with open(pathName[0], 'w') as f:
                f.write(fileText)
            self.current_path = pathName[0]
            self.setWindowTitle(pathName[0])
        except Exception as e:
            print(f"Error al abrir el archivo: {e}")

    # Abrir un archivo
    def openFile(self):
        try:
            self.textErrores.clear()
            self.textEdit.setReadOnly(False)
            documents_folder = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.DocumentsLocation)
            fname = QFileDialog.getOpenFileName(self, 'Open File', documents_folder, 'Text files (*.txt)')
            self.setWindowTitle(fname[0])
            with open(fname[0], 'r') as f:
                fileText = f.read()
                self.textEdit.setText(fileText)
            self.current_path = fname[0]
        except Exception as e:
            print(f"Error al abrir el archivo: {e}")

    # Cerrar el archivo
    def closeFile(self):
        self.textEdit.clear()
        self.textErrores.clear()
        self.setWindowTitle("Compilador")

    # Ctrl Z
    def undo(self):
        self.textEdit.undo()

    # Ctrl Y
    def redo(self):
        self.textEdit.redo()

    # Ctrl X
    def cut(self):
        self.textEdit.cut()

    # Ctrl C
    def copy(self):
        self.textEdit.copy()

    # Ctrl V
    def paste(self):
        self.textEdit.paste()

    # Ctrl +
    def increaseFontSize(self):
        self.current_fontSize += 1
        self.updateFontSize()

    # Ctrl -
    def decreaseFontSize(self):
        self.current_fontSize -= 1
        self.updateFontSize()

    # Selecciona todo el texto para actualizar el tamaño dependiendo de current_fontSize
    def updateFontSize(self):
        cursor = self.textEdit.textCursor()
        self.textEdit.selectAll()  # Seleccionar todo el texto
        format = cursor.charFormat()
        format.setFontPointSize(self.current_fontSize)
        cursor.mergeCharFormat(format)
        self.textEdit.setCurrentCharFormat(format)
    
    # Modo oscuro
    def setDarkMode(self):
        self.setStyleSheet('''
            QWidget {
                background-color: rgb(33, 33, 33);
                color: #FFFFFF;
            }
            QTextEdit {
                background-color: rgb(46, 46, 46);
            }
            QMenuBar::item:selected {
                color: #000000;
            }
            QTabWidget {
                background-color: rgb(33, 33, 33);  /* Fondo del QTabWidget */
                color: #FFFFFF;  /* Color del texto en las pestañas */
            }
            QTabBar::tab {
                background-color: rgb(77, 77, 77);  /* Fondo de cada pestaña */
                color: #FFFFFF;  /* Color del texto de cada pestaña */
                border: 1px solid #555555;  /* Borde de cada pestaña */
                padding: 5px;  /* Espaciado interno de cada pestaña */
            }
            QTabBar::tab:selected {
                background-color: rgb(46, 46, 46);  /* Fondo de la pestaña seleccionada */
                color: #FFFFFF;  /* Color del texto de la pestaña seleccionada */
                border-bottom: 2px solid #FFFFFF;  /* Borde inferior de la pestaña seleccionada */
            }
        ''')

    # Modo claro
    def setLightMode(self):
        self.setStyleSheet("")

    def update_cursor_position(self):
        cursor = self.textEdit.textCursor()
        line_number = cursor.blockNumber() + 1
        column_number = cursor.columnNumber() + 1
        self.line_count_label.setText(f"Línea: {line_number}")
        self.column_count_label.setText(f"Columna: {column_number}")

    def set_default_font_size(self):
        # Establecer el tamaño de fuente por defecto para textEdit
        font = self.textEdit.font()
        font.setPointSize(self.current_fontSize)
        self.textEdit.setFont(font)

        # Establecer el tamaño de fuente por defecto para lineNumberTextEdit
        lineNumberFont = self.lineNumberTextEdit.font()
        lineNumberFont.setFamily("Consolas")
        lineNumberFont.setPointSize(self.current_fontSize)
        self.lineNumberTextEdit.setFont(lineNumberFont)
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec())
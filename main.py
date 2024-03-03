from PyQt6.QtCore import Qt, QStandardPaths
from PyQt6.QtWidgets import QMainWindow, QApplication, QFileDialog, QTextEdit, QHBoxLayout, QVBoxLayout, QSizePolicy
from PyQt6.uic import loadUi
import sys

class NoScrollTextEdit(QTextEdit):
    def __init__(self, parent=None):
        super(NoScrollTextEdit, self).__init__(parent)

    def wheelEvent(self, event):
        # Bloquea el evento de la rueda del mouse
        pass

class Main(QMainWindow):
    def __init__(self):
        super(Main, self).__init__()
        loadUi("main.ui", self) 

        # Ruta actual del archivo
        self.current_path = None
        # Tamaño de la fuente
        self.current_fontSize = 10
        # Titulo de la ventana
        self.setWindowTitle("Compilador")
        # Iniciar en pantalla completa
        self.showMaximized() 

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

    def syncScrollBars(self):
        # Obtiene el valor actual de la barra de desplazamiento vertical de textEdit
        value = self.textEdit.verticalScrollBar().value()
        # Establece el mismo valor en la barra de desplazamiento vertical de lineNumberTextEdit
        self.lineNumberTextEdit.verticalScrollBar().setValue(value)

    # Crear nuevo archivo
    def newFile(self):
        self.textEdit.clear()
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = Main()
    ui.show()
    sys.exit(app.exec())

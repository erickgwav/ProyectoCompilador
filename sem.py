from PyQt5.QtGui import QStandardItem

class SymbolTable:
    def __init__(self):
        # Usaremos una lista de diccionarios para representar los ámbitos (scopes)
        self.scopes = [{}]

    def add_symbol(self, name, symbol_type, value=None):
        # Agregar un símbolo al ámbito actual
        if name in self.scopes[-1]:
            raise Exception(f"Error: La variable '{name}' ya está declarada en el mismo ámbito.")
        self.scopes[-1][name] = {"type": symbol_type, "value": value}
        print(self.scopes[-1][name])

    def lookup(self, name):
        # Buscar el símbolo en los ámbitos (scope)
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Error: La variable '{name}' no está declarada.")

    def enter_scope(self):
        # Entrar a un nuevo ámbito (scope)
        self.scopes.append({})

    def exit_scope(self):
        # Salir del ámbito actual
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Error: No se puede salir del ámbito global.")

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.annotated_tree = None

    def analyze(self, node):
        print(f"Procesando nodo: {node}")
        # El nodo es una tupla que viene del árbol sintáctico generado por parser.py
        if isinstance(node, list):
            for item in node:
                if item is not None:
                    self.analyze(item)
            return

        node_type = node[0]

        if node_type == "programa":
            # Entramos en el ámbito global
            self.symbol_table.enter_scope()
            for decl in node[1]:  # Analizar las declaraciones dentro del programa
                self.analyze(decl) # Analizar cada declaración por separado
            self.symbol_table.exit_scope()

        elif node_type == "declaracion_variable":
            var_type = node[1]
            for var in node[2]:
                try:
                    self.symbol_table.add_symbol(var, var_type)
                    self.annotate_node(var, var_type, None)
                except Exception as e:
                    self.errors.append(str(e))

        elif node_type == "asignacion":
            var_name = node[1]
            try:
                symbol = self.symbol_table.lookup(var_name)
                expr_value = self.evaluate_expression(node[2])  # Evalúa la expresión
                expr_type = self.get_type(expr_value)

                # Verificar que el tipo de la expresión coincide con el tipo de la variable
                if not self.is_type_compatible(symbol['type'], expr_type):
                    raise Exception(f"Error de tipos: No se puede asignar un valor de tipo '{expr_type}' a la variable '{var_name}' de tipo '{symbol['type']}'.")

                symbol["value"] = expr_value
                self.annotate_node(node, symbol["type"], expr_value)  # Anota el valor y el tipo
            except Exception as e:
                self.errors.append(str(e))

        elif node_type in ["if", "if-else"]:
            condition = node[1]
            condition_value = self.evaluate_expression(condition)
            condition_type = self.get_type(condition_value)

            if condition_type != "int":
                self.errors.append(f"Error: La condición del 'if' debe ser de tipo 'int', no '{condition_type}'.")

            self.annotate_node(node, "int", None)  # Anotar el tipo de la condición
            for statement in node[2]:
                self.analyze(statement)
            if node_type == "if-else":
                for statement in node[3]:
                    self.analyze(statement)

        elif node_type == "while":
            condition = node[1]
            condition_value = self.evaluate_expression(condition)
            condition_type = self.get_type(condition_value)

            if condition_type != "int":
                self.errors.append(f"Error: La condición del 'while' debe ser de tipo 'int', no '{condition_type}'.")

            self.annotate_node(node, "int", None)
            for statement in node[2]:
                self.analyze(statement)

        elif node_type == "do-until":
            for statement in node[1]:
                self.analyze(statement)
            condition = node[2]
            condition_value = self.evaluate_expression(condition)
            condition_type = self.get_type(condition_value)

            if condition_type != "int":
                self.errors.append(f"Error: La condición del 'do-until' debe ser de tipo 'int', no '{condition_type}'.")

            self.annotate_node(node, "int", None)

        elif node_type == "cin":
            var_name = node[1]
            try:
                symbol = self.symbol_table.lookup(var_name)
                self.annotate_node(node, symbol['type'], None)
            except Exception as e:
                self.errors.append(f"Error: La variable '{var_name}' no está declarada para CIN.")

        elif node_type == "cout":
            expression = node[1]
            expression_value = self.evaluate_expression(expression)
            expression_type = self.get_type(expression_value)
            self.annotate_node(node, expression_type, None)

        elif node_type in ('+', '-', '*', '/', 'and', 'or', '>', '<', '>=', '<=', '==', '!='):
            self.annotate_node(node, "operador", None)

        else:
            # Aquí se pueden manejar otros nodos como expresiones, condicionales, etc.
            pass

    def annotate_node(self, node, node_type=None, value=None):
        if isinstance(node, tuple):
            node_name = node[0]
            if node_type is None:
                try:
                    symbol_info = self.symbol_table.lookup(node_name)
                    node_type = symbol_info.get("type", "desconocido")
                    value = symbol_info.get("value", None)
                except Exception:
                    node_type = "desconocido"
                    value = None

            annotated_node = QStandardItem(f"{node_name} [Tipo: {node_type}, Valor: {value}]")

            for child in node[1:]:
                annotated_child = self.build_annotated_tree(child)
                if annotated_child:
                    annotated_node.appendRow(annotated_child)

            if self.annotated_tree is None:
                self.annotated_tree = annotated_node

            return annotated_node

        elif isinstance(node, (int, float)):
            # Corrige el tipo para números
            node_type = "int" if isinstance(node, int) else "double"
            return QStandardItem(f"{node} [Tipo: {node_type}, Valor: {node}]")

        elif isinstance(node, str):
            # Corrige el tipo para cadenas e identificadores
            try:
                symbol = self.symbol_table.lookup(node)
                node_type = symbol['type']
                value = symbol['value']
            except Exception:
                node_type = "string"  # Para literales que no son variables
                value = node
            return QStandardItem(f"{node} [Tipo: {node_type}, Valor: {value}]")

    def evaluate_expression(self, node):
        if isinstance(node, str):
            if node == 'true':
                return True
            elif node == 'false':
                return False

            # Intentamos convertir a número
            try:
                if '.' in node:
                    return float(node)
                else:
                    return int(node)
            except ValueError:
                pass

            # Si no es un número, es una variable
            try:
                symbol = self.symbol_table.lookup(node)
                if symbol['value'] is None:
                    raise Exception(f"Error: La variable '{node}' no ha sido inicializada.")
                return symbol['value']
            except Exception as e:
                raise Exception(f"Error: {str(e)}")

        if isinstance(node, (int, float, bool)):
            return node

        if not isinstance(node, tuple) or len(node) < 2:
            raise Exception(f"Nodo mal formado: {node}")

        operator = node[0]

        if operator in ('++', '--'):
            operand = self.evaluate_expression(node[1])
            if isinstance(operand, (int, float)):
                result = operand + 1 if operator == '++' else operand - 1
                self.annotate_node(node, "operador", result)
                return result
            else:
                raise Exception(f"Error de tipos: {operand} no es compatible con la operación {operator}.")

        if len(node) < 3:
            raise Exception(f"Nodo mal formado para operación binaria: {node}")
        
        left = self.evaluate_expression(node[1])
        right = self.evaluate_expression(node[2])
        if left is None or right is None:
            raise Exception(f"Error: La variable no ha sido inicializada antes de su uso en la operación {operator}.")

        # Operaciones aritméticas
        if operator in ('+', '-', '*', '/'):
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if operator == '+':
                    result = left + right
                elif operator == '-':
                    result = left - right
                elif operator == '*':
                    result = left * right
                elif operator == '/':
                    if right != 0:
                        result = left / right
                    else:
                        raise Exception("Error: División por cero.")
                self.annotate_node(node, "operador", result)
                return result
            else:
                raise Exception(f"Error de tipos: {left} y {right} no son compatibles para la operación {operator}.")
        
        # Operaciones lógicas
        elif operator in ('and', 'or'):
            if isinstance(left, bool) and isinstance(right, bool):
                result = left and right if operator == 'and' else left or right
                self.annotate_node(node, "operador", result)
                return result
            else:
                raise Exception(f"Error de tipos: {left} y {right} no son compatibles para la operación {operator}.")

        # Operaciones relacionales
        elif operator in ('>', '<', '>=', '<=', '==', '!='):
            if isinstance(left, (int, float)) and isinstance(right, (int, float)):
                if operator == '>':
                    result = left > right
                elif operator == '<':
                    result = left < right
                elif operator == '>=':
                    result = left >= right
                elif operator == '<=':
                    result = left <= right
                elif operator == '==':
                    result = left == right
                elif operator == '!=':
                    result = left != right
                self.annotate_node(node, "operador", result)
                return result
            else:
                raise Exception(f"Error de tipos: {left} y {right} no son compatibles para la operación {operator}.")
        
        else:
            raise Exception(f"Operador {operator} no reconocido.")

    def build_annotated_tree(self, node):
        if isinstance(node, tuple):
            node_name = node[0]
            try:
                symbol_info = self.symbol_table.lookup(node_name)
                node_type = symbol_info.get("type", "desconocido")
                value = symbol_info.get("value", None)
            except Exception:
                node_type = "desconocido"
                value = None

            annotated_node = QStandardItem(f"{node_name} [Tipo: {node_type}, Valor: {value}]")

            for child in node[1:]:
                child_node = self.build_annotated_tree(child)
                if child_node:
                    annotated_node.appendRow(child_node)

            return annotated_node

        elif isinstance(node, (int, float, bool)):
            node_type = "int" if isinstance(node, int) else "double" if isinstance(node, float) else "bool"
            return QStandardItem(f"{node} [Tipo: {node_type}, Valor: {node}]")

        elif isinstance(node, str):
            try:
                symbol = self.symbol_table.lookup(node)
                node_type = symbol['type']
                value = symbol['value']
            except Exception:
                node_type = "string"  # Para literales que no son variables
                value = node
            return QStandardItem(f"{node} [Tipo: {node_type}, Valor: {value}]")

        elif isinstance(node, list):
            list_node = QStandardItem("Lista")
            for item in node:
                child_node = self.build_annotated_tree(item)
                if child_node:
                    list_node.appendRow(child_node)
            return list_node

        else:
            return QStandardItem(str(node))

    def get_type(self, value):
        if isinstance(value, int):
            return "int"
        elif isinstance(value, float):
            return "double"
        elif isinstance(value, bool):
            return "bool"
        elif isinstance(value, str):
            return "string"
        else:
            return "unknown"

    def is_type_compatible(self, var_type, expr_type):
        # Define las reglas de compatibilidad de tipos
        # Por ejemplo, un int puede ser asignado a un double
        compatibility = {
            "int": ["int"],
            "double": ["int", "double"],
            "bool": ["bool"],
            "string": ["string"],
        }
        return expr_type in compatibility.get(var_type, [])

    def print_errors(self):
        for error in self.errors:
            print(error)

    def print_symbol_table(self):
        print("Tabla de Símbolos:")
        for i, scope in enumerate(self.scopes):
            print(f"Ambito {i}:")
            for name, info in scope.items():
                print(f"  {name}: Tipo={info['type']}, Valor={info['value']}")

# Ejemplo de uso (suponiendo que ya tienes el árbol sintáctico generado en parser.py)
def analyze_syntax_tree(syntax_tree):
    analyzer = SemanticAnalyzer()
    analyzer.analyze(syntax_tree)
    analyzer.print_errors()
    analyzer.print_symbol_table()

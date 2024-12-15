from PyQt5.QtGui import QStandardItem
import math, re

symbol_table = {}
temp_sym_table = {}

class SemanticAnalyzer:
    def __init__(self):
        self.errors = []

    def analyze(self, syntax_tree):
        declarations = syntax_tree[1]
        annotated_tree = self.process_program(declarations)
        return ('programa', annotated_tree)

    def process_program(self, declarations):
        annotated_declarations = []
        for declaration in declarations:
            if isinstance(declaration, tuple) and declaration[0] in ['int', 'double']:
                annotated_declarations.append(self.process_variable_declaration(declaration))
            elif declaration[0] == '=':
                annotated_declarations.append(self.process_assignment(declaration))
            elif declaration[0] in ['if', 'if-else', 'do-until', 'while']:
                annotated_declarations.append(self.process_logical_structure(declaration))
            elif declaration[0] in ['cin', 'cout']:
                annotated_declarations.append(self.process_input_output(declaration))
            elif isinstance(declaration, list):
                annotated_declarations.append(self.process_program(declaration))
        return (annotated_declarations)

    def process_variable_declaration(self, declaration):
        var_type = declaration[0]
        variables = declaration[1]
        annotated_vars = []
        for var in variables:
            if var in symbol_table:
                self.errors.append(f"Error: '{var}' ya se ha declarado")
                return (var, 'Error')
            else:
                default_value = 0 if var_type == 'int' else 0.0
                self.add_to_symbol_table(var, var_type, default_value, temp_sym_table.get(var)["lineno"])
                annotated_vars.append((var, f'tipo={var_type}', f'valor={default_value}'))
        return (var_type, annotated_vars)


    def process_assignment(self, assignment):
        var_name = assignment[1]
        expr = assignment[2]

        if var_name not in symbol_table:
            self.errors.append(f"Error: '{var_name}' aún no se ha declarado.")
            return (var_name, 'error')

        var_type = symbol_table[var_name]["type"]
        if not isinstance(expr, tuple):
            expr_value = self.evaluate_expression(expr, var_type, True)
        else:
            expr_value = self.evaluate_expression(expr, var_type, False)

        if isinstance(expr_value, tuple) and len(expr_value) > 2:
            symbol_table[var_name]["value"] = expr_value[1]
            value = expr_value[1]
            if value == None:
                self.errors.append(f"Error: La asignacion de '{var_name}' es errónea")
                return (assignment[0], var_name, [f'tipo={var_type}', f'valor=Error', (expr_value[0], expr_value[2], expr_value[3])])
            return (assignment[0], var_name, [f'tipo={var_type}', f'valor={expr_value[1]}', (expr_value[0], expr_value[2], expr_value[3])])
        else:
            if isinstance(expr_value, tuple):
                symbol_table[var_name]["value"] = expr_value[0]
            else:
                symbol_table[var_name]["value"] = expr_value
            if expr_value == None:
                self.errors.append(f"Error: La asignacion de '{var_name}' es errónea")
                return (assignment[0], var_name, [f'tipo={var_type}', f'valor=Error'])
            return (assignment[0], var_name, [f'tipo={var_type}', f'valor={expr_value[0]}'])
        
    def process_logical_structure(self, declaration):
        if declaration[0] == 'if':
            return ('if', self.process_logical_relation(declaration, False), self.process_program(declaration[2]))
        elif declaration[0] == 'if-else':
            cond = self.process_logical_relation(declaration, False)
            cuerpo_if = self.process_program(declaration[2])
            cuerpo_else = self.process_program(declaration[3])
            return ('if-else', cond, cuerpo_if, cuerpo_else)
        elif declaration[0] == 'do-until':
            return ('do', self.process_program(declaration[1])), ('until', self.process_logical_relation(declaration[2], True))
        elif declaration[0] == 'while':
            return ('while', self.process_logical_relation(declaration[1], True)), (self.process_program(declaration[2]))
    
    def process_logical_relation(self, condition, comp):
        if comp:
            relation = condition
        else:
            relation = condition[1]
        if relation[0] == 'relacion':
            comparator = relation[1]
            first_term = relation[2][0]
            second_term = relation[2][1]
            isNotInTable_1 = symbol_table.get(first_term) is None
            isNotInTable_2 = symbol_table.get(second_term) is None
            var_type = None
            if not isNotInTable_1 and isNotInTable_2:
                var_type = symbol_table.get(first_term)["type"]
            elif not isNotInTable_2 and isNotInTable_1:
                var_type = symbol_table.get(second_term)["type"]
            else:
                try:
                    int(first_term)
                    var_type = 'int'
                except:
                    try:
                        float(first_term)
                        var_type = 'double'
                    except:
                        var_type = 'int'
            relation_value = self.evaluate_relation(comparator, first_term, second_term, var_type)
            if comp:
                return (relation[0] + f' valor={relation_value}', relation_value, (comparator, first_term, second_term))
            else:
                return (relation[0] + f'valor={relation_value}', relation_value, (comparator, first_term, second_term, self.process_program(condition[2])))
        elif relation[0] == 'comparador':
            comparator = relation[1]
            first_exp = relation[2]
            second_exp = relation[3]
            logical_relation_1 = self.process_logical_relation(first_exp, True)
            logical_relation_2 = self.process_logical_relation(second_exp, True)
            if comparator == 'or':
                return (relation[0], comparator, f'\n valor={logical_relation_1[1] or logical_relation_2[1]}', logical_relation_1, logical_relation_2)
            elif comparator == 'and':
                return (relation[0], comparator, f'\n valor={logical_relation_1[1] and logical_relation_2[1]}', logical_relation_1, logical_relation_2)
    
    
    def process_input_output(self, declaration):
        isNotInTable = symbol_table.get(declaration[1]) is None
        if not isNotInTable:
            return (declaration[0], declaration[1], f'valor={symbol_table.get(declaration[1])["value"]}')
        elif isinstance(declaration[1], tuple):
            expr_value = self.evaluate_expression(declaration[1], 'int', False)
            return (declaration[0], f'valor={expr_value[1]}', expr_value)
        else:
            self.errors.append(f"Error: La variable '{declaration[1][0]}' aún no ha sido declarada")
            return None

    def evaluate_relation(self, comparator, first_term, second_term, var_type):
        if comparator == '>':
            return self.evaluate_expression(first_term, var_type, False) > self.evaluate_expression(second_term, var_type, False)
        elif comparator == '<':
            return self.evaluate_expression(first_term, var_type, False) < self.evaluate_expression(second_term, var_type, False)
        elif comparator == '>=':
            return self.evaluate_expression(first_term, var_type, False) >= self.evaluate_expression(second_term, var_type, False)
        elif comparator == '<=':
            return self.evaluate_expression(first_term, var_type, False) <= self.evaluate_expression(second_term, var_type, False)
        elif comparator == '==':
            return self.evaluate_expression(first_term, var_type, False) == self.evaluate_expression(second_term, var_type, False)
        elif comparator == '!=':
            return self.evaluate_expression(first_term, var_type, False) != self.evaluate_expression(second_term, var_type, False)

    def evaluate_expression(self, expr, var_type, is_assign):
        if expr is None:
            self.errors.append("Error: expresión no válida (valor es None).")
            return None
        isNotInTable = symbol_table.get(expr) is None
        if isinstance(expr, tuple):
            value_1 = self.evaluate_expression(expr[1], var_type, False)
            value_2 = self.evaluate_expression(expr[2], var_type, False)
            if value_1 == None:
                return None
            if value_2 == None:
                return None
            tuple_1 = None
            tuple_2 = None
            value_1_tuple = False
            value_2_tuple = False
            if isinstance(value_1, tuple):
                tuple_1 = value_1
                if len(value_1) == 2:
                    value_1 = value_1[0]
                else:
                    value_1 = value_1[1]
                value_1_tuple = True
            if isinstance(value_2, tuple):
                tuple_2 = value_2
                if len(value_2) == 2:
                    value_2 = value_2[0]
                else:
                    value_2 = value_2[1]
                value_2_tuple = True
            if expr[0] == '+':
                result = value_1 + value_2
                res_type = var_type
                if var_type == 'int':
                    result = math.trunc(result)
                    res_type="int"
                if isinstance(value_1, float) or isinstance(value_2, float):
                    result = float(result)
                    res_type="double"
                if expr[0] == '=' and var_type == 'double':
                    result = float(result)
                if value_1_tuple and value_2_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), (tuple_2), f'tipo={res_type}')
                elif value_1_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), value_2, f'tipo={res_type}')
                elif value_2_tuple:
                    return (expr[0] + f' valor={result}', result, value_1, (tuple_2), f'tipo={res_type}')
                else:
                    return (expr[0] + f' valor={result}', result, value_1, value_2, f'tipo={res_type}')
            elif expr[0] == '-':
                result = value_1 - value_2
                res_type = var_type
                if var_type == 'int':
                    result = math.trunc(result)
                    res_type="int"
                if isinstance(value_1, float) or isinstance(value_2, float):
                    result = float(result)
                    res_type="double"
                if value_1_tuple and value_2_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), (tuple_2), f'tipo={res_type}')
                elif value_1_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), value_2, f'tipo={res_type}')
                elif value_2_tuple:
                    return (expr[0] + f' valor={result}', result, value_1, (tuple_2), f'tipo={res_type}')
                else:
                    return (expr[0] + f' valor={result}', result, value_1, value_2, f'tipo={res_type}')
            elif expr[0] == '*':
                result = value_1 * value_2
                res_type = var_type
                if isinstance(value_1, float) or isinstance(value_2, float):
                    result = float(result)
                    res_type="double"
                if var_type == 'int':
                    result = math.trunc(result)
                    res_type="int"
                if value_1_tuple and value_2_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), (tuple_2), f'tipo={res_type}')
                elif value_1_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), value_2, f'tipo={res_type}')
                elif value_2_tuple:
                    return (expr[0] + f' valor={result}', result, value_1, (tuple_2), f'tipo={res_type}')
                else:
                    return (expr[0] + f' valor={result}', result, value_1, value_2, f'tipo={res_type}')
            elif expr[0] == '/':
                result = value_1 / value_2
                res_type = var_type
                if var_type == 'int' or isinstance(value_1, int):
                    result = math.trunc(result)
                    result = int(result)
                    res_type="int"
                if isinstance(value_1, float) or isinstance(value_2, float):
                    result = float(result)
                    res_type="double"
                if value_1_tuple and value_2_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), (tuple_2), f'tipo={res_type}')
                elif value_1_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), value_2, f'tipo={res_type}')
                elif value_2_tuple:
                    return (expr[0] + f' valor={result}', result, value_1, (tuple_2), f'tipo={res_type}')
                else:
                    return (expr[0] + f' valor={result}', result, value_1, value_2, f'tipo={res_type}')
            elif expr[0] == '%':
                result = value_1 % value_2
                res_type = var_type
                if isinstance(value_1, float) or isinstance(value_2, float):
                    result = float(result)
                    res_type="double"
                if var_type == 'int':
                    result = math.trunc(result)
                    res_type="int"
                if value_1_tuple and value_2_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), (tuple_2), f'tipo={res_type}')
                elif value_1_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), value_2, f'tipo={res_type}')
                elif value_2_tuple:
                    return (expr[0] + f' valor={result}', result, value_1, (tuple_2), f'tipo={res_type}')
                else:
                    return (expr[0] + f' valor={result}', result, value_1, value_2, f'tipo={res_type}')
            elif expr[0] == '^':
                result = value_1 ** value_2
                res_type = var_type
                if isinstance(value_1, float) or isinstance(value_2, float):
                    result = float(result)
                    res_type="double"
                if var_type == 'int':
                    result = math.trunc(result)
                    res_type="int"
                if value_1_tuple and value_2_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), (tuple_2), f'tipo={res_type}')
                elif value_1_tuple:
                    return (expr[0] + f' valor={result}', result, (tuple_1), value_2, f'tipo={res_type}')
                elif value_2_tuple:
                    return (expr[0] + f' valor={result}', result, value_1, (tuple_2), f'tipo={res_type}')
                else:
                    return (expr[0] + f' valor={result}', result, value_1, value_2, f'tipo={res_type}')
        elif not isNotInTable:
            variable = symbol_table.get(expr)
            if variable is None or variable["value"] is None:
                self.errors.append(f"Error: la variable '{expr}' no tiene un valor asignado.")
                return None
            return self.evaluate_expression(variable["value"], variable["type"], False)
        else:
            if is_assign:
                if var_type == 'double':
                    try:
                        return (float(expr), 'type=double')
                    except:
                        return None
                elif var_type == 'int':
                    try:
                        return (int(expr), 'type=int')
                    except:
                        return None
            else:
                str_val = expr
                float_re = re.compile('-?\d+.\d+')
                expr = float(expr)
                is_float = False
                if isinstance(str_val, str):
                    is_float = float_re.match(str_val)
                elif var_type == 'double':
                    is_float = True
                if expr % 1 == 0 and not is_float:
                    math.trunc(expr)
                    return (int(expr), 'type=int')
                else:
                    return (expr, 'type=double')
                
    def return_symbol_table(self):
        return symbol_table

    def add_to_symbol_table(self, var_name, var_type, value, lineno):
        loc = len(symbol_table) + 1
        if var_name in symbol_table:
            if isinstance(symbol_table[var_name], list):
                symbol_table[var_name].append({
                    "name": var_name,
                    "type": var_type,
                    "value": value,
                    "loc": loc,
                    "lineno": lineno
                })
            else:
                symbol_table[var_name] = [symbol_table[var_name], {
                    "name": var_name,
                    "type": var_type,
                    "value": value,
                    "loc": loc,
                    "lineno": lineno
                }]
        else:
            symbol_table[var_name] = {
                "name": var_name,
                "type": var_type,
                "value": value,
                "loc": loc,
                "lineno": lineno
            }

    def clean_temp_sym_table(self):
        temp_sym_table.clear()
        symbol_table.clear()
    
    def add_to_temp_symbol_table(var_name, lineno):
        if not var_name in temp_sym_table:
            temp_sym_table[var_name] = {
                "name": var_name,
                "lineno": [lineno]
            }
        else:
            lineno_tab = temp_sym_table.get(var_name)["lineno"]
            lineno_tab.append(lineno)
            temp_sym_table[var_name] = {
                "name": var_name,
                "lineno": lineno_tab
            }

    def print_symbol_table(self):
        html_table = "<table style='border-collapse: collapse;' width='100%'><tr style='color: #1155d4; font-size: 15px'><th style='padding: 8px;'>Variable</th><th style='padding: 8px;'>Tipo</th><th style='padding: 8px;'>Valor</th><th style='padding: 8px;'>Número de Registro</th><th style='padding: 8px;'>Líneas</th></tr>"
        
        for var, info in symbol_table.items():
            html_table += f"<tr><td style='text-align: center; padding: 5px;'>{var}</td>"
            html_table += f"<td style='text-align: center; padding: 5px;'>{info['type']}</td>"
            html_table += f"<td style='text-align: center; padding: 5px;'>{info['value'] if info['value'] is not None else 'none'}</td>"
            html_table += f"<td style='text-align: center; padding: 5px;'>{info['loc']}</td>"
            html_table += f"<td style='text-align: center; padding: 5px;'>{info['lineno']}</td></tr>"
        
        html_table += "</table>"
        return html_table

    def build_annotated_tree(self, tree):
        annotated_tree_item = self.add_annotated_items(tree)
        return annotated_tree_item

    def add_annotated_items(self, element):
        if element is None:
            return None

        if isinstance(element, tuple):
            node_type = str(element[0])
            annotations = ', '.join([str(item) for item in element[1:]])

            item = QStandardItem(f"{node_type} [{annotations}]")
            
            for child in element[1:]:
                child_item = self.add_annotated_items(child)
                if child_item is not None:
                    item.appendRow(child_item)

        elif isinstance(element, list):
            item = QStandardItem("lista")
            for subelement in element:
                subitem = self.add_annotated_items(subelement)
                if subitem is not None:
                    item.appendRow(subitem)

        elif isinstance(element, tuple) and element[0] == 'do-until':
            item = QStandardItem(f"do-until [{element[1:]}]")
            body_item = self.add_annotated_items(element[1])
            condition_item = self.add_annotated_items(element[2]) 
            if body_item:
                item.appendRow(body_item)
            if condition_item:
                item.appendRow(condition_item)

        else:
            item = QStandardItem(str(element))

        return item


    def print_errors(self):
        if self.errors:
            print("Errores semanticos:")
            for error in self.errors:
                print(error)
            return self.errors
        else:
            print("No se encontraron errores semanticos.")
            return None
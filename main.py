import flet as ft
import re

def get_precedence(op):
    op = op.upper()
    
    if op in ('OR', 'XOR'): return 1
    if op == 'AND': return 2
    if op == 'NOT': return 3
    
    if op in ('+', '-'): return 4
    if op in ('*', '/'): return 5
    if op == '^': return 6
    
    return 0

def is_operand(token):
    logic_operators = ['AND', 'OR', 'NOT', 'XOR']
    if token.endswith('(') or token in ['+', '-', '*', '/', '^', '(', ')']: 
        return False
    return token.isalnum() and token.upper() not in logic_operators

def is_open_paren(t):
    # Detecta '(' normal o funciones como 'sen(', 'cos(', etc.
    return t == '(' or t.endswith('(')

# --- LÓGICA PREFIJA ---
def solve_shunting_yard_prefix(expression):
    # 1. Agrega '*' implícito (ej. "5x" -> "5 * x")
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1 * \2', expression)
    
    # 2. Captura "sen(", "cos (", números, letras y operadores
    tokens = re.findall(r'[a-zA-Z]+\s*\(|\d+|[a-zA-Z]+|[+/*()^-]', expression)
    tokens = [t.replace(" ", "") for t in tokens] # Limpia espacios internos "sen (" -> "sen("
    
    adjusted_tokens = tokens[::-1]
    reversed_str = " ".join(adjusted_tokens)

    output_stack = []
    op_stack = []
    op_snapshots = []

    for token in adjusted_tokens:
        if is_operand(token):
            output_stack.append(token)
        elif token == ')':
            op_stack.append(token)
        elif is_open_paren(token): # Actúa como cierre de paréntesis al estar invertido
            temp_stack = list(op_stack) + [token] 
            
            match_idx = -1
            for i in range(len(op_stack) - 1, -1, -1):
                if op_stack[i] == ')':
                    match_idx = i
                    break
            
            highlights = []
            if match_idx != -1:
                highlights = [match_idx, len(temp_stack) - 1]
            
            op_snapshots.append({'stack': temp_stack, 'highlights': highlights})

            while op_stack and op_stack[-1] != ')':
                output_stack.append(op_stack.pop())
            if op_stack:
                op_stack.pop() # Saca el ')'
                
            # Si era "sen(", agrega "sen" a la salida (sin el paréntesis)
            if token != '(':
                output_stack.append(token[:-1])
        else:
            popped = False
            temp_stack = list(op_stack) + [token]
            
            while op_stack and op_stack[-1] != ')':
                top_op = op_stack[-1]
                # Ajuste de precedencia (Para prefija invertida, '^' es >=, el resto es >)
                if token == '^':
                    if get_precedence(top_op) >= get_precedence(token):
                        if not popped:
                            op_snapshots.append({'stack': temp_stack, 'highlights': [len(temp_stack) - 1]})
                            popped = True
                        output_stack.append(op_stack.pop())
                    else:
                        break
                else:
                    if get_precedence(top_op) > get_precedence(token):
                        if not popped:
                            op_snapshots.append({'stack': temp_stack, 'highlights': [len(temp_stack) - 1]})
                            popped = True
                        output_stack.append(op_stack.pop())
                    else:
                        break
                
            op_stack.append(token)
    
    if op_stack:
        op_snapshots.append({'stack': list(op_stack), 'highlights': []})
        while op_stack:
            popped = op_stack.pop()
            if popped != ')':
                output_stack.append(popped)

    prefix_expr = " ".join(output_stack[::-1])
    return reversed_str, output_stack, op_snapshots, prefix_expr

# --- LÓGICA POSTFIJA ---
def solve_shunting_yard_postfix(expression):
    # 1. Agrega '*' implícito (ej. "5x" -> "5 * x")
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1 * \2', expression)
    
    # 2. Captura "sen(", "cos (", números, letras y operadores
    tokens = re.findall(r'[a-zA-Z]+\s*\(|\d+|[a-zA-Z]+|[+/*()^-]', expression)
    tokens = [t.replace(" ", "") for t in tokens]
    original_str = " ".join(tokens)

    output_stack = []
    op_stack = []
    op_snapshots = []

    for token in tokens:
        if is_operand(token):
            output_stack.append(token)
        elif is_open_paren(token):
            op_stack.append(token) # Se apila completo, ej: 'sen('
        elif token == ')':
            temp_stack = list(op_stack) + [')'] 
            
            match_idx = -1
            for i in range(len(op_stack) - 1, -1, -1):
                if is_open_paren(op_stack[i]):
                    match_idx = i
                    break
            
            highlights = []
            if match_idx != -1:
                highlights = [match_idx, len(temp_stack) - 1]
            
            op_snapshots.append({'stack': temp_stack, 'highlights': highlights})

            while op_stack and not is_open_paren(op_stack[-1]):
                output_stack.append(op_stack.pop())
            if op_stack:
                popped_paren = op_stack.pop()
                # Si sacó un "sen(", manda "sen" a la salida
                if popped_paren != '(':
                    output_stack.append(popped_paren[:-1])
        else:
            popped = False
            temp_stack = list(op_stack) + [token]
            
            while op_stack and not is_open_paren(op_stack[-1]):
                top_op = op_stack[-1]
                # Ajuste de precedencia: '^' se asocia de derecha a izquierda (>)
                if token == '^':
                    if get_precedence(top_op) > get_precedence(token):
                        if not popped:
                            op_snapshots.append({'stack': temp_stack, 'highlights': [len(temp_stack) - 1]})
                            popped = True
                        output_stack.append(op_stack.pop())
                    else:
                        break
                else:
                    if get_precedence(top_op) >= get_precedence(token):
                        if not popped:
                            op_snapshots.append({'stack': temp_stack, 'highlights': [len(temp_stack) - 1]})
                            popped = True
                        output_stack.append(op_stack.pop())
                    else:
                        break
                
            op_stack.append(token)
    
    if op_stack:
        op_snapshots.append({'stack': list(op_stack), 'highlights': []})
        while op_stack:
            popped = op_stack.pop()
            if is_open_paren(popped):
                if popped != '(':
                    output_stack.append(popped[:-1])
            else:
                output_stack.append(popped)

    postfix_expr = " ".join(output_stack)
    return original_str, output_stack, op_snapshots, postfix_expr

# --- INTERFAZ DE USUARIO ---
def main(page: ft.Page):
    page.title = "Algoritmo Shunting Yard"
    page.padding = 30
    page.theme_mode = ft.ThemeMode.DARK 
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.AUTO

    def draw_stack(title, items, highlights=None):
        if highlights is None: highlights = []
        cells = []
        
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            is_highlighted = i in highlights
            
            bg_color = "#E65100" if is_highlighted else "#263238"
            text_color = "white"
            border_color = "#FFA726" if is_highlighted else "#546E7A"
            
            cells.append(
                ft.Container(
                    content=ft.Text(str(item), color=text_color, weight="bold", size=16),
                    border=ft.border.Border(
                        ft.border.BorderSide(2, border_color),
                        ft.border.BorderSide(2, border_color),
                        ft.border.BorderSide(2, border_color),
                        ft.border.BorderSide(2, border_color)
                    ),
                    width=75, 
                    height=35,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=bg_color,
                    border_radius=5
                )
            )
            
        if not cells: 
            cells.append(ft.Container(width=75, height=35))

        return ft.Column([
            ft.Column(cells, spacing=2),
            ft.Text(title, weight="bold", size=16, color="#B0BEC5")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    results_container = ft.Column(spacing=30)

    def on_convert(e):
        if not txt_input.value: return
        results_container.controls.clear()
        
        modo = dropdown_mode.value

        if modo == "Prefija":
            orig_s, out_s, snaps, final_res = solve_shunting_yard_prefix(txt_input.value)
            
            results_container.controls.append(
                ft.Column([
                    ft.Text(f"Original: {txt_input.value}", size=22, color=ft.Colors.CYAN_300, weight="bold"),
                    ft.Text(f"Invertida: {orig_s}", size=22, color=ft.Colors.CYAN_300, weight="bold"),
                ])
            )
        else: # Postfija
            orig_s, out_s, snaps, final_res = solve_shunting_yard_postfix(txt_input.value)
            
            results_container.controls.append(
                ft.Column([
                    ft.Text(f"Original (Procesada): {orig_s}", size=22, color=ft.Colors.CYAN_300, weight="bold"),
                ])
            )

        stacks_row = ft.Row(
            spacing=30, 
            vertical_alignment=ft.CrossAxisAlignment.END,
            scroll=ft.ScrollMode.ALWAYS
        )

        stacks_row.controls.append(draw_stack("Salida", out_s))

        for snap in snaps:
            stacks_row.controls.append(
                draw_stack("Operador", snap['stack'], snap['highlights'])
            )

        stacks_row.controls.append(
            ft.Container(
                content=ft.Column([
                    ft.Text(modo, size=16, weight="bold", color="#B0BEC5"),
                    ft.Text(final_res, size=26, color=ft.Colors.GREEN_400, weight="bold"),
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=ft.padding.only(left=20)
            )
        )

        results_container.controls.append(stacks_row)
        page.update()

    txt_input = ft.TextField(
        label="Escribe tu operación:",
        expand=True,
        on_submit=on_convert,
        border_color=ft.Colors.CYAN_700,
        focused_border_color=ft.Colors.CYAN_300
    )  

    dropdown_mode = ft.Dropdown(
        options=[
            ft.dropdown.Option("Prefija"),
            ft.dropdown.Option("Postfija"),
        ],
        value="Postfija", # Cambié el valor por defecto a Postfija para que pruebes el de la imagen
        width=150,
        border_color=ft.Colors.CYAN_700,
        focused_border_color=ft.Colors.CYAN_300,
        color="white",
        bgcolor="#263238"
    )

    btn = ft.FilledButton(
        "Convertir", 
        on_click=on_convert,
        style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN_700, color="white")
    )
    
    page.add(
        ft.Row([txt_input, dropdown_mode, btn]),
        ft.Divider(height=40, color="#37474F"),
        results_container
    )

if __name__ == "__main__":
    ft.app(main)
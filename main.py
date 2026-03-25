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
    return t == '(' or t.endswith('(')

def is_operator(token):
    return token in ['+', '-', '*', '/', '^']

def is_function(token):
    return token.lower() in ['sen', 'cos', 'tan', 'not']

# --- 1. INFIJA A PREFIJA ---
def solve_shunting_yard_prefix(expression):
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1 * \2', expression)
    tokens = re.findall(r'[a-zA-Z]+\s*\(|\d+|[a-zA-Z]+|[+/*()^-]', expression)
    tokens = [t.replace(" ", "") for t in tokens] 
    
    original_str = " ".join(tokens) # Guardamos la original
    
    adjusted_tokens = tokens[::-1]
    reversed_str = " ".join(adjusted_tokens) # Y esta es la invertida

    output_stack = []
    op_stack = []
    op_snapshots = []

    for token in adjusted_tokens:
        if is_operand(token):
            output_stack.append(token)
        elif token == ')':
            op_stack.append(token)
            # El paréntesis es naranja
            op_snapshots.append({'stack': list(op_stack), 'paren_idx': [len(op_stack) - 1], 'new_idx': []})
        elif is_open_paren(token): 
            temp_stack = list(op_stack) + [token] 
            match_idx = -1
            for i in range(len(op_stack) - 1, -1, -1):
                if op_stack[i] == ')':
                    match_idx = i
                    break
            
            p_idx = [match_idx, len(temp_stack) - 1] if match_idx != -1 else []
            # Ambos paréntesis se pintan de naranja al encontrarse
            op_snapshots.append({'stack': temp_stack, 'paren_idx': p_idx, 'new_idx': []})

            while op_stack and op_stack[-1] != ')':
                output_stack.append(op_stack.pop())
                
            if op_stack:
                op_stack.pop() 
                
            if token != '(':
                output_stack.append(token[:-1])
        else:
            while op_stack and op_stack[-1] != ')':
                top_op = op_stack[-1]
                pop_condition = get_precedence(top_op) >= get_precedence(token) if token == '^' else get_precedence(top_op) > get_precedence(token)
                
                if pop_condition:
                    output_stack.append(op_stack.pop())
                else:
                    break
                
            op_stack.append(token)
            # El operador nuevo se pinta con el color nuevo (azul)
            op_snapshots.append({'stack': list(op_stack), 'paren_idx': [], 'new_idx': [len(op_stack) - 1]})
    
    while op_stack:
        popped = op_stack.pop()
        if popped != ')':
            output_stack.append(popped)

    prefix_expr = " ".join(output_stack[::-1])
    # Ahora retornamos ambas cadenas al principio
    return original_str, reversed_str, output_stack, op_snapshots, prefix_expr

# --- 2. INFIJA A POSTFIJA ---
def solve_shunting_yard_postfix(expression):
    expression = re.sub(r'(\d)([a-zA-Z])', r'\1 * \2', expression)
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
            op_stack.append(token)
            # El paréntesis es naranja
            op_snapshots.append({'stack': list(op_stack), 'paren_idx': [len(op_stack) - 1], 'new_idx': []})
        elif token == ')':
            temp_stack = list(op_stack) + [')'] 
            match_idx = -1
            for i in range(len(op_stack) - 1, -1, -1):
                if is_open_paren(op_stack[i]):
                    match_idx = i
                    break
            
            p_idx = [match_idx, len(temp_stack) - 1] if match_idx != -1 else []
            # Ambos paréntesis se pintan de naranja al encontrarse
            op_snapshots.append({'stack': temp_stack, 'paren_idx': p_idx, 'new_idx': []})

            while op_stack and not is_open_paren(op_stack[-1]):
                output_stack.append(op_stack.pop())
                
            if op_stack:
                popped_paren = op_stack.pop()
                if popped_paren != '(':
                    output_stack.append(popped_paren[:-1])
        else:
            while op_stack and not is_open_paren(op_stack[-1]):
                top_op = op_stack[-1]
                pop_condition = get_precedence(top_op) > get_precedence(token) if token == '^' else get_precedence(top_op) >= get_precedence(token)
                
                if pop_condition:
                    output_stack.append(op_stack.pop())
                else:
                    break
                
            op_stack.append(token)
            # El operador nuevo se pinta con el color nuevo (azul)
            op_snapshots.append({'stack': list(op_stack), 'paren_idx': [], 'new_idx': [len(op_stack) - 1]})
    
    while op_stack:
        popped = op_stack.pop()
        if is_open_paren(popped):
            if popped != '(':
                output_stack.append(popped[:-1])
        else:
            output_stack.append(popped)

    postfix_expr = " ".join(output_stack)
    return original_str, output_stack, op_snapshots, postfix_expr


# --- 3. POLACA (PREFIJA A INFIJA - PASO A PASO) ---
def solve_polaca(expression):
    tokens = re.findall(r'[a-zA-Z]+|\d+|[+/*^()-]', expression)
    steps = [" ".join(tokens)]
    
    while len(tokens) > 1:
        replaced = False
        for i in range(len(tokens) - 1, -1, -1):
            if is_operator(tokens[i]):
                if i + 2 < len(tokens) and not is_operator(tokens[i+1]) and not is_operator(tokens[i+2]) and not is_function(tokens[i+1]) and not is_function(tokens[i+2]):
                    new_expr = f"({tokens[i+1]} {tokens[i]} {tokens[i+2]})"
                    tokens = tokens[:i] + [new_expr] + tokens[i+3:]
                    steps.append(" ".join(tokens))
                    replaced = True
                    break
            elif is_function(tokens[i]):
                 if i + 1 < len(tokens) and not is_operator(tokens[i+1]) and not is_function(tokens[i+1]):
                    new_expr = f"{tokens[i]}({tokens[i+1]})"
                    tokens = tokens[:i] + [new_expr] + tokens[i+2:]
                    steps.append(" ".join(tokens))
                    replaced = True
                    break
        if not replaced: 
            break 
    return steps

# --- 4. POLACA INVERSA (POSTFIJA A INFIJA - PASO A PASO) ---
def solve_polaca_inversa(expression):
    tokens = re.findall(r'[a-zA-Z]+|\d+|[+/*^()-]', expression)
    steps = [" ".join(tokens)]
    
    while len(tokens) > 1:
        replaced = False
        for i in range(len(tokens)):
            if is_operator(tokens[i]):
                if i >= 2 and not is_operator(tokens[i-1]) and not is_operator(tokens[i-2]) and not is_function(tokens[i-1]) and not is_function(tokens[i-2]):
                    new_expr = f"({tokens[i-2]} {tokens[i]} {tokens[i-1]})"
                    tokens = tokens[:i-2] + [new_expr] + tokens[i+1:]
                    steps.append(" ".join(tokens))
                    replaced = True
                    break
            elif is_function(tokens[i]):
                if i >= 1 and not is_operator(tokens[i-1]) and not is_function(tokens[i-1]):
                    new_expr = f"{tokens[i]}({tokens[i-1]})"
                    tokens = tokens[:i-1] + [new_expr] + tokens[i+1:]
                    steps.append(" ".join(tokens))
                    replaced = True
                    break
        if not replaced: 
            break
    return steps


# --- INTERFAZ DE USUARIO ---
def main(page: ft.Page):
    page.title = "Conversor de Notaciones - Algoritmos"
    page.padding = 30
    page.theme_mode = ft.ThemeMode.DARK 
    page.bgcolor = "#121212"
    page.scroll = ft.ScrollMode.AUTO

    def draw_stack(title, items, paren_idx=None, new_idx=None):
        if paren_idx is None: paren_idx = []
        if new_idx is None: new_idx = []
        cells = []
        
        for i in range(len(items) - 1, -1, -1):
            item = items[i]
            
            # Colores base
            bg_color = "#263238"
            border_color = "#546E7A"
            
            # Si es paréntesis, se pinta de naranja
            if i in paren_idx:
                bg_color = "#E65100"
                border_color = "#FFA726"
            # Si es el operador nuevo, se pinta de un tono azul vibrante
            elif i in new_idx:
                bg_color = "#0277BD" # Light Blue 800
                border_color = "#4FC3F7" # Light Blue 300
                
            cells.append(
                ft.Container(
                    content=ft.Text(str(item), color="white", weight="bold", size=16, text_align="center"),
                    border=ft.border.Border(
                        ft.border.BorderSide(2, border_color),
                        ft.border.BorderSide(2, border_color),
                        ft.border.BorderSide(2, border_color),
                        ft.border.BorderSide(2, border_color)
                    ),
                    padding=ft.padding.symmetric(horizontal=15), 
                    width=75,
                    height=35,
                    alignment=ft.Alignment(0, 0),
                    bgcolor=bg_color,
                    border_radius=5
                )
            )
            
        if not cells: cells.append(ft.Container(width=75, height=35))

        return ft.Column([
            ft.Column(cells, spacing=2, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Text(title, weight="bold", size=16, color="#B0BEC5")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER)

    results_container = ft.Column(spacing=30)

    def on_convert(e):
        if not txt_input.value: return
        results_container.controls.clear()
        modo = dropdown_mode.value

        if modo in ["Infija a Prefija", "Infija a Postfija"]:
            stacks_row = ft.Row(spacing=30, vertical_alignment=ft.CrossAxisAlignment.END, scroll=ft.ScrollMode.ALWAYS)
            
            # --- AQUÍ MOSTRARÁ AMBAS CADENAS EN PREFIJA ---
            if modo == "Infija a Prefija":
                orig_s, rev_s, out_s, snaps, final_res = solve_shunting_yard_prefix(txt_input.value)
                results_container.controls.append(
                    ft.Column([
                        ft.Text(f"Original Procesada: {orig_s}", size=18, color=ft.Colors.CYAN_100),
                        ft.Text(f"Original Invertida: {rev_s}", size=22, color=ft.Colors.CYAN_300, weight="bold")
                    ])
                )
            else:
                orig_s, out_s, snaps, final_res = solve_shunting_yard_postfix(txt_input.value)
                results_container.controls.append(ft.Text(f"Original Procesada: {orig_s}", size=22, color=ft.Colors.CYAN_300, weight="bold"))

            stacks_row.controls.append(draw_stack("Salida", out_s))
            for snap in snaps:
                stacks_row.controls.append(draw_stack("Operador", snap['stack'], snap.get('paren_idx', []), snap.get('new_idx', [])))

            stacks_row.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("RESULTADO FINAL", size=16, weight="bold", color="#B0BEC5"),
                        ft.Text(final_res, size=26, color=ft.Colors.GREEN_400, weight="bold"),
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    padding=ft.padding.only(left=20)
                )
            )
            results_container.controls.append(stacks_row)

        else: # POLACA O POLACA INVERSA (Estilo libreta)
            steps = solve_polaca(txt_input.value) if modo == "Polaca" else solve_polaca_inversa(txt_input.value)
            
            results_container.controls.append(ft.Text(f"Resolución paso a paso ({modo}):", size=22, color=ft.Colors.CYAN_300, weight="bold"))
            
            steps_column = ft.Column(spacing=10)
            for step in steps:
                steps_column.controls.append(
                    ft.Text(step, size=20, font_family="Consolas", color=ft.Colors.AMBER_100)
                )
            
            results_container.controls.append(
                ft.Container(
                    content=steps_column,
                    bgcolor="#1E272E",
                    padding=20,
                    border_radius=10,
                    border=ft.border.all(1, "#37474F")
                )
            )

        page.update()

    txt_input = ft.TextField(
        label="Escribe tu operación (Separa con espacios para Polaca):",
        expand=True,
        on_submit=on_convert,
        border_color=ft.Colors.CYAN_700,
        focused_border_color=ft.Colors.CYAN_300
    )  

    dropdown_mode = ft.Dropdown(
        options=[
            ft.dropdown.Option("Infija a Prefija"),
            ft.dropdown.Option("Infija a Postfija"),
            ft.dropdown.Option("Polaca"),
            ft.dropdown.Option("Polaca Inversa"),
        ],
        value="Infija a Prefija",
        width=180,
        border_color=ft.Colors.CYAN_700,
        focused_border_color=ft.Colors.CYAN_300,
        color="white",
        bgcolor="#263238"
    )

    btn = ft.FilledButton("Resolver", on_click=on_convert, style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN_700, color="white"))
    
    page.add(
        ft.Row([txt_input, dropdown_mode, btn]),
        ft.Divider(height=40, color="#37474F"),
        results_container
    )

if __name__ == "__main__":
    ft.app(main)
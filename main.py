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
    return token.isalnum() and token.upper() not in logic_operators

def solve_shunting_yard_prefix(expression):
    tokens = re.findall(r'\d+|[a-zA-Z]+|[+/*()^-]', expression)
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
        elif token == '(':
            temp_stack = list(op_stack) + ['('] 
            
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
                op_stack.pop() 
        else:
            popped = False
            temp_stack = list(op_stack) + [token]
            
            while (op_stack and op_stack[-1] != ')' and 
                   get_precedence(op_stack[-1]) >= get_precedence(token)):
                if not popped:
                    op_snapshots.append({'stack': temp_stack, 'highlights': [len(temp_stack) - 1]})
                    popped = True
                output_stack.append(op_stack.pop())
                
            op_stack.append(token)
    
    if op_stack:
        op_snapshots.append({'stack': list(op_stack), 'highlights': []})
        while op_stack:
            output_stack.append(op_stack.pop())

    prefix_expr = " ".join(output_stack[::-1])
    return reversed_str, output_stack, op_snapshots, prefix_expr

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
        
        rev_s, out_s, snaps, pref_res = solve_shunting_yard_prefix(txt_input.value)

        results_container.controls.append(
            ft.Column([
                ft.Text(f"Original: {txt_input.value}", size=22, color=ft.Colors.CYAN_300, weight="bold"),
                ft.Text(f"Invertida: {rev_s}", size=22, color=ft.Colors.CYAN_300, weight="bold"),
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
                    ft.Text("Prefija", size=16, weight="bold", color="#B0BEC5"),
                    ft.Text(pref_res, size=26, color=ft.Colors.GREEN_400, weight="bold"),
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
    btn = ft.FilledButton(
        "Convertir", 
        on_click=on_convert,
        style=ft.ButtonStyle(bgcolor=ft.Colors.CYAN_700, color="white")
    )
    page.add(
        ft.Row([txt_input, btn]),
        ft.Divider(height=40, color="#37474F"),
        results_container
    )
if __name__ == "__main__":
    ft.app(main)
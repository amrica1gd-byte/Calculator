
import ast
import math
import operator

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
from kivy.utils import get_color_from_hex


# App colors
BG = "#171717"
DISPLAY_BG = "#171717"
BTN = "#292929"
BTN_LIGHT = "#383838"
ORANGE = "#FF9F0A"
WHITE = "#FFFFFF"
GRAY = "#999999"

Window.clearcolor = get_color_from_hex(BG)


def calculate(expression):
    operations = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Mod: operator.mod,
        ast.UAdd: operator.pos,
        ast.USub: operator.neg,
    }

    def solve(node):
        if isinstance(node, ast.Expression):
            return solve(node.body)

        if isinstance(node, ast.Constant):
            if type(node.value) in (int, float):
                return node.value
            raise ValueError("Invalid number")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)

            if op_type not in operations:
                raise ValueError("Invalid operation")

            left = solve(node.left)
            right = solve(node.right)

            if op_type is ast.Div and right == 0:
                raise ZeroDivisionError

            result = operations[op_type](left, right)

            if isinstance(result, float) and not math.isfinite(result):
                raise ValueError("Invalid result")

            return result

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)

            if op_type not in operations:
                raise ValueError("Invalid operation")

            return operations[op_type](solve(node.operand))

        raise ValueError("Invalid expression")

    return solve(ast.parse(expression, mode="eval"))


class CalculatorApp(App):

    def build(self):
        self.expression = ""
        self.just_calculated = False

        root = BoxLayout(
            orientation="vertical",
            padding=[dp(12), dp(35), dp(12), dp(15)],
            spacing=dp(8)
        )

        # Calculation history
        self.history = Label(
            text="",
            color=get_color_from_hex(GRAY),
            font_size=sp(18),
            halign="right",
            valign="bottom",
            size_hint_y=0.12
        )
        self.history.bind(size=self.update_text_size)
        root.add_widget(self.history)

        # Main display
        self.display = Label(
            text="0",
            color=get_color_from_hex(WHITE),
            font_size=sp(42),
            halign="right",
            valign="middle",
            size_hint_y=0.23
        )
        self.display.bind(size=self.update_text_size)
        root.add_widget(self.display)

        # Touch-friendly buttons
        buttons = [
            ["AC", "⌫", "%", "÷"],
            ["7", "8", "9", "×"],
            ["4", "5", "6", "−"],
            ["1", "2", "3", "+"],
            ["±", "0", ".", "="],
        ]

        grid = GridLayout(
            cols=4,
            spacing=dp(8),
            size_hint_y=0.65
        )

        for row in buttons:
            for symbol in row:
                color = BTN
                text_color = WHITE

                if symbol in ["÷", "×", "−", "+", "="]:
                    color = ORANGE

                elif symbol in ["AC", "⌫", "%", "±"]:
                    color = BTN_LIGHT

                button = Button(
                    text=symbol,
                    font_size=sp(23),
                    bold=True,
                    color=get_color_from_hex(text_color),
                    background_normal="",
                    background_down="",
                    background_color=get_color_from_hex(color),
                    border=(0, 0, 0, 0)
                )

                button.bind(
                    on_release=lambda btn: self.press(btn.text)
                )

                grid.add_widget(button)

        root.add_widget(grid)
        return root

    def update_text_size(self, widget, size):
        widget.text_size = size

    def press(self, value):
        if value == "AC":
            self.expression = ""
            self.history.text = ""
            self.display.text = "0"
            self.just_calculated = False
            return

        if value == "⌫":
            self.expression = self.expression[:-1]
            self.just_calculated = False

        elif value == "=":
            if not self.expression:
                return

            try:
                original = self.expression
                result = calculate(original)

                self.history.text = original + " ="

                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                self.expression = str(result)
                self.just_calculated = True

            except ZeroDivisionError:
                self.display.text = "Cannot divide by zero"
                self.expression = ""
                self.just_calculated = False
                return

            except Exception:
                self.display.text = "Error"
                self.expression = ""
                self.just_calculated = False
                return

        elif value == "±":
            if self.expression.startswith("-"):
                self.expression = self.expression[1:]
            else:
                self.expression = "-" + self.expression

            self.just_calculated = False

        else:
            symbols = {
                "÷": "/",
                "×": "*",
                "−": "-"
            }

            value = symbols.get(value, value)

            if self.just_calculated:
                if value not in ["+", "-", "*", "/", "%"]:
                    self.expression = ""
                    self.history.text = ""

                self.just_calculated = False

            self.expression += value

        self.display.text = self.expression if self.expression else "0"


if __name__ == "__main__":
    CalculatorApp().run()

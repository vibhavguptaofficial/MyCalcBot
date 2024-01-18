import telebot
from sympy import symbols, Eq, solve, simplify, diff
import re
import math
from CalcConfig import *
from math import factorial 

bot = telebot.TeleBot(BOT_API)

equation_choices = {
    'linear': 'a*x + b = 0',
    'quadratic': 'a*x**2 + b*x + c = 0',
    'cubic': 'a*x**3 + b*x**2 + c*x + d = 0',
}

variables_required = {
    'linear': ['a', 'b'],
    'quadratic': ['a', 'b', 'c'],
    'cubic': ['a', 'b', 'c', 'd'],
}

def create_main_keyboard():
    markup = telebot.types.InlineKeyboardMarkup()
    
    operation_button = telebot.types.InlineKeyboardButton("Basic Arithmetic Operations", callback_data="basic_arithmetic")
    markup.add(operation_button)

    for equation_type in equation_choices.keys():
        button = telebot.types.InlineKeyboardButton(equation_type, callback_data=f"solve_{equation_type}")
        markup.add(button)

    features = [
        'Factor a polynomial',
        'Find the derivative of a function',
        'Number System',
        'Temperature',
        'Time Calculator',
        'Volume',
        'Length',
        'Mass',
        'Speed',
        'Date',
        'Data',
        'BMI',
        'Area',
        'Discount',
    ]
    for feature in features:
        button = telebot.types.InlineKeyboardButton(feature, callback_data=f"feature_{feature}")
        markup.add(button)

    return markup

var = symbols('x')
def solve_equation(equation_text, var):
    try:
        equation_text = equation_text.replace(" ", "")
        equation_text = equation_text.replace("^", "**")
        equation = Eq(eval(equation_text), 0)
        solution = solve(equation, var)
        solution_str = ""
        for var, val in solution.items():
            solution_str += f"{var}: {val}, "

        return solution_str[:-2]
    except Exception as e:
        print("Sorry, I couldn't solve the equation. Make sure it's a valid equation and try again.")
        return None

def handle_feature(feature_type, text):
    if feature_type == 'Factor a polynomial':
        try:
            polynomial = simplify(text)
            factored = polynomial.factor()
            return str(factored)
        except Exception as e:
            return "Unable to factor the polynomial. Make sure it's a valid polynomial expression."

    if feature_type == 'Find the derivative of a function':
        try:
            x = symbols('x')
            derivative = diff(text, x)
            return str(derivative)
        except Exception as e:
            return "Unable to find the derivative. Make sure it's a valid function."

    if feature_type == 'Number System':
        try:
            number = text.strip()
            binary = bin(int(number))
            octal = oct(int(number))
            hexadecimal = hex(int(number))
            return f"Binary: {binary}\nOctal: {octal}\nHexadecimal: {hexadecimal}"
        except Exception as e:
            return "Unable to convert the number. Make sure it's a valid number."

    if feature_type == 'Temperature':
        try:
            parts = text.split()
            if len(parts) != 2:
                return "Invalid input. Please provide a value and unit (e.g., '30 C' or '75 F')."
            value, unit = float(parts[0]), parts[1].upper()
            if unit == 'C':
                fahrenheit = (value * 9/5) + 32
                kelvin = value + 273.15
                return f"Fahrenheit: {fahrenheit}\nKelvin: {kelvin}"
            elif unit == 'F':
                celsius = (value - 32) * 5/9
                kelvin = (value + 459.67) * 5/9
                return f"Celsius: {celsius}\nKelvin: {kelvin}"
            elif unit == 'K':
                celsius = value - 273.15
                fahrenheit = (value * 9/5) - 459.67
                return f"Celsius: {celsius}\nFahrenheit: {fahrenheit}"
            else:
                return "Invalid unit. Please use 'C', 'F', or 'K'."
        except Exception as e:
            return "Unable to convert the temperature. Make sure it's a valid input."


@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    bot.reply_to(message, f"Welcome, {user.first_name}! I'm Vibhav. Select an option from the menu:", reply_markup=create_main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    callback_data = call.data
    if callback_data == "basic_arithmetic":
        bot.send_message(call.message.chat.id, "You selected to perform Basic Arithmetic Operations. Now, enter an arithmetic expression (e.g., '5 + 3') to calculate the result.")
    elif callback_data.startswith("solve_"):
        equation_type = callback_data.replace("solve_", "")
        bot.send_message(call.message.chat.id, f"You selected to solve a {equation_type} equation. Now, enter the equation in the format: {equation_choices[equation_type]}\nFor example, to solve a {equation_type} equation, enter '{equation_choices[equation_type]}'")
    elif callback_data.startswith("feature_"):
        feature_type = callback_data.replace("feature_", "")
        bot.send_message(call.message.chat.id, f"You selected the '{feature_type}' feature. Now, enter the expression or value you want to work with.")

@bot.message_handler(func=lambda message: True)
def handle_input(message):
    text = message.text
    if text:
        if text.startswith('/start'):
            start(message)
            return
        
        for equation_type in equation_choices.keys():
            equation_format = equation_choices[equation_type]
            if equation_format.replace(" ", "") == text.replace(" ", ""):
                variables = symbols(*variables_required[equation_type])
                solution = solve_equation(text, 'x')
                bot.reply_to(message, f"Solutions:\n{solution}")
                return
        if is_valid_arithmetic_expression(text):
            result = eval_arithmetic_expression(text)
            if result is not None:
                bot.reply_to(message, f"Result of the arithmetic expression: {result}")
            else:
                bot.reply_to(message, "Sorry, I couldn't calculate the result. Make sure it's a valid arithmetic expression and try again.")
            return


        for feature_type in [
            'Factor a polynomial', 'Find the derivative of a function',
            'Number System', 'Temperature', 'Time Calculator', 'Volume',
            'Length', 'Mass', 'Speed', 'Date', 'Data', 'BMI', 'Area', 'Discount',
        ]:
            if text.startswith(feature_type):
                expression = text[len(feature_type):].strip()
                result = handle_feature(feature_type, expression)
                bot.reply_to(message, result)
                return

    bot.reply_to(message, "Sorry, I couldn't handle the input. Make sure it's a valid input and try again.")

def is_valid_arithmetic_expression(text):
    pattern = r'^[0-9+\-*/^()xX! \t\n\r\f\v]+$'
    return re.match(pattern, text) is not None

def eval_arithmetic_expression(text):
    try:
        text = text.replace('X', 'x')

        factorial_pattern = r'(\d+)!'
        match = re.search(factorial_pattern, text)
        if match:
            number = int(match.group(1))
            factorial_result = factorial(number)
           
            text = text.replace(match.group(0), str(factorial_result))

        return eval(text)
    except Exception:
        return None

print("MyCalc Started...")
bot.polling(none_stop=True, interval=5, timeout=60)

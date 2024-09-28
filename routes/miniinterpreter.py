import json
import logging

from flask import request
from routes import app

logger = logging.getLogger(__name__)

@app.route('/lisp-parser', methods=['POST'])
def evaluate():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    print_output = []
    
    def puts(args, line_num):
        if len(args) != 1 or not isinstance(args[0], str):
            return None, error_message(line_num)
        print_output.append(args[0])
        return None, None
    
    def concat(args, line_num):
        if len(args) != 2 or not all(isinstance(arg, str) for arg in args):
            return None, error_message(line_num)
        return args[0] + args[1], None
    
    def lowercase(args, line_num):
        if len(args) != 1 or not isinstance(args[0], str):
            return None, error_message(line_num)
        return args[0].lower(), None
    
    def uppercase(args, line_num):
        if len(args) != 1 or not isinstance(args[0], str):
            return None, error_message(line_num)
        return args[0].upper(), None
    
    def replace(args, line_num):
        if len(args) != 3 or not all(isinstance(arg, str) for arg in args):
            return None, error_message(line_num)
        return args[0].replace(args[1], args[2]), None
    
    def substring(args, line_num):
        if len(args) != 3 or not isinstance(args[0], str) or not all(isinstance(x, int) for x in args[1:]):
            return None, error_message(line_num)
        if args[1] < 0 or args[2] > len(args[0]):
            return None, error_message(line_num)
        return args[0][args[1]:args[2]], None
    
    def add(args, line_num):
        if len(args) < 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return round(sum(args), 4), None
    
    def subtract(args, line_num):
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return round(args[0] - args[1], 4), None
    
    def multiply(args, line_num):
        if len(args) < 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        result = 1
        for arg in args:
            result *= arg
        return round(result, 4), None
    
    def divide(args, line_num):
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args) or args[1] == 0:
            return None, error_message(line_num)
        return round(args[0] / args[1], 4), None
    
    def gt(args, line_num):
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return args[0] > args[1], None
    
    def lt(args, line_num):
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return args[0] < args[1], None
    
    def eq(args, line_num):
        if len(args) != 2:
            return None, error_message(line_num)
        return args[0] == args[1], None
    
    def str_func(args, line_num):
        if len(args) != 1:
            return None, error_message(line_num)
        return str(args[0]), None
    
    def error_message(line_num):
        return f"ERROR at line {line_num}"
    
    function_map = {
        "puts": puts,
        "concat": concat,
        "lowercase": lowercase,
        "uppercase": uppercase,
        "replace": replace,
        "substring": substring,
        "add": add,
        "subtract": subtract,
        "multiply": multiply,
        "divide": divide,
        "gt": gt,
        "lt": lt,
        "eq": eq,
        "str": str_func
    }
    
    def parse_argument(arg):
        if arg.isdigit():
            return int(arg)
        elif arg.replace('.', '', 1).isdigit():
            return float(arg)
        elif arg.startswith('"') and arg.endswith('"'):
            return arg[1:-1]
        else:
            return arg
    
    def split_expression(data):
        data = data.strip()[1:-1]
        tokens = data.split()
        function_name = tokens[0]
        arguments = [parse_argument(arg) for arg in tokens[1:]]
        return function_name, arguments

    def evaluate_expression(expression, line_num):
        function_name, arguments = split_expression(expression)
        if function_name in function_map:
            result, error = function_map[function_name](arguments, line_num)
            return result, error
        return None, error_message(line_num)

    expressions = data['expressions']

    for line_num, expr in enumerate(expressions, 1):
        result, error = evaluate_expression(expr, line_num)
        if error:
            print_output.append(error)
            break
        if result is not None:
            print_output.append(str(result))

    logging.info("Final result list: {}".format(print_output))
    return json.dumps({"output": print_output})

import json
import logging
import re
from flask import request
from routes import app

logger = logging.getLogger(__name__)

@app.route('/lisp-parser', methods=['POST'])
def evaluate():
    data = request.get_json()
    logging.info("Data sent for evaluation: {}".format(data))
    print_output = []
    variables = {}  # Global variable store

    # Define available functions
    def puts(args, line_num):
        logger.info(f"Executing 'puts' with args: {args}")
        if len(args) != 1 or not isinstance(args[0], str):
            return None, error_message(line_num)
        print_output.append(args[0])
        return None, None

    def set_var(args, line_num):
        logger.info(f"Executing 'set' with args: {args}")
        if len(args) != 2 or not isinstance(args[0], str):
            return None, error_message(line_num)
        variables[args[0]] = args[1]  # Store variable globally
        logger.info(f"Stored variable '{args[0]}' with value '{args[1]}'")
        return None, None

    def concat(args, line_num):
        logger.info(f"Executing 'concat' with args: {args}")
        if len(args) != 2 or not all(isinstance(arg, str) for arg in args):
            return None, error_message(line_num)
        return args[0] + args[1], None

    def lowercase(args, line_num):
        logger.info(f"Executing 'lowercase' with args: {args}")
        if len(args) != 1 or not isinstance(args[0], str):
            return None, error_message(line_num)
        return args[0].lower(), None

    def uppercase(args, line_num):
        logger.info(f"Executing 'uppercase' with args: {args}")
        if len(args) != 1 or not isinstance(args[0], str):
            return None, error_message(line_num)
        return args[0].upper(), None

    def replace(args, line_num):
        logger.info(f"Executing 'replace' with args: {args}")
        if len(args) != 3 or not all(isinstance(arg, str) for arg in args):
            return None, error_message(line_num)
        return args[0].replace(args[1], args[2]), None

    def substring(args, line_num):
        logger.info(f"Executing 'substring' with args: {args}")
        if len(args) != 3 or not isinstance(args[0], str) or not all(isinstance(x, int) for x in args[1:]):
            return None, error_message(line_num)
        if args[1] < 0 or args[2] > len(args[0]):
            return None, error_message(line_num)
        return args[0][args[1]:args[2]], None

    def add(args, line_num):
        logger.info(f"Executing 'add' with args: {args}")
        if len(args) < 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return round(sum(args), 4), None

    def subtract(args, line_num):
        logger.info(f"Executing 'subtract' with args: {args}")
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return round(args[0] - args[1], 4), None

    def multiply(args, line_num):
        logger.info(f"Executing 'multiply' with args: {args}")
        if len(args) < 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        result = 1
        for arg in args:
            result *= arg
        return round(result, 4), None

    def divide(args, line_num):
        logger.info(f"Executing 'divide' with args: {args}")
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args) or args[1] == 0:
            return None, error_message(line_num)
        return round(args[0] / args[1], 4), None

    def gt(args, line_num):
        logger.info(f"Executing 'gt' with args: {args}")
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return args[0] > args[1], None

    def lt(args, line_num):
        logger.info(f"Executing 'lt' with args: {args}")
        if len(args) != 2 or not all(isinstance(arg, (int, float)) for arg in args):
            return None, error_message(line_num)
        return args[0] < args[1], None

    def eq(args, line_num):
        logger.info(f"Executing 'eq' with args: {args}")
        if len(args) != 2:
            return None, error_message(line_num)
        return args[0] == args[1], None

    def str_func(args, line_num):
        logger.info(f"Executing 'str' with args: {args}")
        if len(args) != 1:
            return None, error_message(line_num)
        return str(args[0]), None

    def error_message(line_num):
        return f"ERROR at line {line_num}"

    # Mapping function names to Python functions
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
        "set": set_var,
        "gt": gt,
        "lt": lt,
        "eq": eq,
        "str": str_func
    }

    # Function to extract the main body of the expression
    def strip_expressions(data):
        return data['expressions']

    function_names = []
    arguments = []

    def strip_line(expression):
        tokens = re.findall(r'[\(\)]|\"[^\"]*\"|\S+', expression)
        logger.info(f"Tokens: {tokens}")

        expecting_variable = False  # Use this to track if we are expecting a variable name (for 'set')

        for token in tokens:
            # Ignore parentheses
            if token in ['(', ')', '/', '\\']:
                continue

            # Handle valid function names
            elif token in function_map:
                function_names.append(token)
                logger.info(f"Found function: {token}")
                if token == "set":
                    expecting_variable = True  # Set a flag that the next token should be a variable name

            # Handle variables
            elif token in variables:
                arguments.append(variables[token])
                logger.info(f"Found variable '{token}' with value {variables[token]}")

            # Handle variable names (e.g., 'x' in 'set x 15')
            elif expecting_variable:
                arguments.append(token)  # Treat it as a variable name
                logger.info(f"Set variable name: {token}")
                expecting_variable = False  # Reset flag

            else:
                # Strip trailing parentheses from token
                token = token.rstrip(')')

                if token.isdigit():
                    arguments.append(int(token))  # Add as integer if it's a number
                    logger.info(f"Added argument (int): {int(token)}")
                elif token.replace('.', '', 1).isdigit():
                    arguments.append(float(token))  # Add as float if it's a number
                    logger.info(f"Added argument (float): {float(token)}")
                elif token.startswith('"') and token.endswith('"'):
                    arguments.append(token[1:-1])  # Handle quoted strings
                    logger.info(f"Added argument (string): {token[1:-1]}")
                else:
                    logger.warning(f"Unrecognized token: {token}")

        logger.info(f"Function names: {function_names}")
        logger.info(f"Arguments: {arguments}")


    # Global variable to store the result
    final_value = None

    # Function to loop through function names and run them in reverse order
    def run_functions(function_names, arguments):
        global final_value  # Declare global variable

        for i in range(len(function_names) - 1, -1, -1):  # Loop from innermost function to outermost
            func_name = function_names[i]
            logger.info(f"Running function: {func_name}")

            if i == len(function_names) - 1:  # Innermost function uses full arguments
                final_value, error = function_map[func_name](arguments, 1)  # Add line number for error tracking
                logger.info(f"Function result: {final_value}")
                if error:
                    logger.error(f"Error encountered: {error}")
                    return None, error
            else:  # Outer functions take the result of inner functions as input
                final_value, error = function_map[func_name]([final_value], 1)
                logger.info(f"Function result: {final_value}")
                if error:
                    logger.error(f"Error encountered: {error}")
                    return None, error

        return final_value, None  # Return final value and no error

    # Function to combine the results into JSON format
    def combine_results(final_value):
        return {"output": print_output}

    # Step 1: Extract the list of expressions
    expressions = strip_expressions(data)

    # Step 2: Process each expression
    for expression in expressions:
        function_names.clear()
        arguments.clear()

        # Step 2.1: Strip the expression into function names and arguments
        strip_line(expression)

        # Step 2.2: If there was a final_value from the previous expression, add it as the first argument
        if final_value is not None:
            arguments.insert(0, final_value)
            logger.info(f"Inserted previous final_value {final_value} into arguments")

        # Step 2.3: Run through the functions in reverse order, applying them to the arguments
        final_value, error = run_functions(function_names, arguments)
        if error:
            return json.dumps({"output": [error]})

    # Step 3: Combine the final result into the desired JSON format
    result_json = combine_results(final_value)

    logging.info("Final result list: {}".format(result_json))
    return json.dumps(result_json)

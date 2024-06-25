"""A collection of mathematical functions."""

import ast
import datetime
import logging
import operator


def _evaluate_arithmetic_expression(expression_str: str):
    """Evaluates a string containing a valid arithmetic expression.

    Args:
        expression_str: The string representation of the arithmetic expression.

    Returns:
        The calculated result of the expression, or None if the expression is
        invalid.
    """

    # Define allowed operators
    allowed_operators = {
        ast.Add: operator.add,
        ast.Sub: operator.sub,
        ast.Mult: operator.mul,
        ast.Div: operator.truediv,
        ast.Pow: operator.pow,
        ast.USub: operator.neg,
    }

    # Parse the expression into an AST
    tree = ast.parse(expression_str, mode="eval").body

    # Function to recursively evaluate the AST nodes
    def eval_node(node):
        if isinstance(node, ast.Constant):
            return node.n
        elif isinstance(node, ast.BinOp):
            op = allowed_operators.get(type(node.op))
            if op is None:
                raise ValueError("Invalid operator")
            return op(eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):
            op = allowed_operators.get(type(node.op))
            if op is None:
                raise ValueError("Invalid operator")
            return op(eval_node(node.operand))
        else:
            raise ValueError("Invalid expression")

    return eval_node(tree)


async def math(expression: str) -> float:
    """Evaluates a arithmetic expression.

    Args:
        expression: The arithmetic expression to evaluate.

    Returns:
        The result of the arithmetic expression.
    """
    logging.info("Evaluating the expression: %s.", expression)
    return float(_evaluate_arithmetic_expression(expression))


async def diff_date(a: str, b: str) -> int:
    """Calculates the difference between two dates.

    Args:
        a: The first date in YYYY-MM-DD.
        b: The second date in YYYY-MM-DD.

    Returns:
        The number of days from a to b.
    """
    logging.info("Calculating the difference between %s and %s.", a, b)
    date_format = "%Y-%m-%d"
    date_a = datetime.datetime.strptime(a, date_format).date()
    date_b = datetime.datetime.strptime(b, date_format).date()

    return (date_a - date_b).days

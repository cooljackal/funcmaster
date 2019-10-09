# pylint: disable=no-value-for-parameter
from funcmaster import process, operation, execute_process


@operation
def add(context, x, y):
    context.log.info("Add: %i + %i = %i" % (x, y, x + y))
    return x + y


@operation
def sub(context, x, y):
    context.log.info("Subtract: %i - %i = %i" % (x, y, x - y))
    return x - y


@operation
def multiply(context, x, y):
    context.log.info("Multiply: %i * %i = %i" % (x, y, x * y))
    return x * y


@process
def hello_world_process():
    multiply(add(1, 2), sub(5, 3))


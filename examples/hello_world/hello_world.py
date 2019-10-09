# pylint: disable=no-value-for-parameter
from funcmaster import process, operation, execute_process


@operation
def add(x, y):
    return x + y


@operation
def sub(x, y):
    return x - y


@operation
def multiply(x, y):
    return x * y


@process
def hello_world_process():
    multiply(add(1, 2), sub(5, 3))


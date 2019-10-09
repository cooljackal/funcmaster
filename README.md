# funcmaster
A straightforward workflow tool that is easy to use.

## Usage

Install funcmaster using pip:

```
pip install funcmaster
```

Create a file `hello_world.py` with the following contents:

```
# pylint: disable=no-value-for-parameter
from funcmaster import operation, process


@operation
def add(context, x, y):
    context.log.info("%i + %i = %i" % (x, y, x + y))
    return x + y


@operation
def subtract(context, x, y):
    context.log.info("%i - %i = %i" % (x, y, x - y))
    return x - y


@process
def hello_world_process():
    subtract(add(1, 2), 3)
```

Use the funcmaster cli command to execute the process:

```
funcmaster -m hello_world -p hello_world_process
```

Win!
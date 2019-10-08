# pylint: disable=no-value-for-parameter
import sys

sys.path.append("../../")

from funcmaster import process, operation, execute_process


@operation
def add(x, y):
    return x + y


@process
def hello_world():
    add(
        add.clone("add_clone_0")(
            add.clone("add_clone_1")(2, 3), add.clone("add_clone_2")(4, 5)
        ),
        add.clone("add_clone_3")(
            add.clone("add_clone_2")(4, 5), add.clone("add_clone_1")(2, 3)
        ),
    )

execute_process(hello_world)

# pylint: disable=no-member
import pytest
from funcmaster import process, Process, operation, Operation, parent_process


def test_process_str():
    @process
    def test():
        return

    assert test.__str__() == "test"


def test_process_repr():
    @process
    def test():
        return

    assert test.__repr__() == "test"


def test_operation_str():
    @operation
    def test():
        return

    assert test.__str__() == "test"


def test_operation_repr():
    @operation
    def test():
        return

    assert test.__repr__() == "test"


def test_process_decorator():
    @process
    def test():
        return

    assert type(test) == Process


def test_operation_decorator():
    @operation
    def test():
        return

    assert type(test) == Operation


def test_process_init_no_name():
    def func():
        return

    proc = Process(func)

    assert proc.func == func
    assert proc.name == "func"
    assert proc.operations == []
    assert proc.initialized == False
    assert proc.executed == False


def test_process_init_with_name():
    def func():
        return

    proc = Process(func, "other_name")
    assert proc.func == func
    assert proc.name == "other_name"
    assert proc.operations == []
    assert proc.initialized == False
    assert proc.executed == False


def test_parent_process():
    def test_operation():
        return parent_process()

    def test_method(self):
        return test_operation()

    def func():
        return

    proc = Process(func)
    setattr(Process, "test_method", test_method)
    result = proc.test_method()
    assert type(result) == Process
    result = test_operation()
    assert result == None


def test_process_find_operation():
    @operation
    def test_operation():
        return

    def func():
        return

    proc = Process(func)
    assert proc.find_operation("test_operation") == None

    proc.operations.append(test_operation)
    assert proc.find_operation("test_operation") == test_operation


def test_process_add_operation():
    @operation
    def test_operation():
        return

    def func():
        return

    proc = Process(func)
    assert proc.operations == []

    proc.add_operation(test_operation)
    assert proc.operations[0] == test_operation


def test_operation_clone():
    @operation
    def test_operation(x):
        return

    @process
    def test_process():
        test_operation(test_operation.clone("test_operation_clone")())
        return

    test_process()
    cloned_operation = test_process.operations[0]
    cloned_operation.initialized = True
    cloned_operation.executed = True

    assert cloned_operation.name == "test_operation_clone"
    assert cloned_operation.initialized == True
    assert cloned_operation.executed == True
    assert test_operation.name == "test_operation"
    assert test_operation.initialized == True
    assert test_operation.executed == False


def test_operation_run():
    @operation
    def test_operation(x):
        return x + 1

    with pytest.raises(RuntimeError):
        test_operation.run()

    test_operation.initialized = True
    test_operation.args = [1]
    test_operation.kwargs = {}

    result = test_operation.run()
    assert result == 2

    # Run again to get saved result
    result = test_operation.run() 
    assert result == 2



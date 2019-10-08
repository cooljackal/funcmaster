import sys
import logging

name = "funcmaster"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s | %(levelname)5s | %(message)s"
)
logger = logging.getLogger(__name__)


def parent_process():
    """Find the parent Process by traversing up the frame stack."""
    current_frame = sys._getframe(0)
    while True:
        current_frame = current_frame.f_back
        try:
            if "self" in current_frame.f_locals.keys():
                instance = current_frame.f_locals["self"]
                if type(instance) == Process:
                    return instance
        except AttributeError:
            return None


def execute_process(target_process):
    """Build the execution plan then run the process."""
    target_process()
    target_process.run()


def process(func):
    """Decorator function for Process class."""
    return Process(func)


def operation(func):
    """Decorator function for Operation class."""
    return Operation(func)


class Process:
    """A class that represents a complete collection of operations."""

    def __init__(self, func, name=None):
        self.operations = []
        self.func = func
        self.name = name or func.__name__
        self.initialized = False
        self.executed = False

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __call__(self):
        """Build a list of operations by doing a "dry-run"."""
        logger.info("Process [%s] planning started" % self.name)
        if not self.initialized:
            self.func()
            self.initialized = True
            logger.info("Process [%s] initialized" % self.name)
        logger.info("Process [%s] planning complete" % self.name)
        return self

    def add_operation(self, operation):
        """Called by an operation object to add itself to the process."""
        existing_operation = self.find_operation(operation.name)
        if existing_operation == None:
            self.operations.append(operation)
            logger.info(
                "Operation [%s] added to Process [%s]" % (operation.name, self.name)
            )

    def find_operation(self, name):
        """Find an operation object in the list by name."""
        existing_operation = [x for x in self.operations if x.name == name]
        if len(existing_operation) == 0:
            return None
        else:
            return existing_operation[0]

    def run(self):
        if self.initialized and not self.executed:
            logger.info("Process [%s] finished" % self.name)
            for operation in self.operations:
                try:
                    operation.run()
                except Exception:
                    logger.error("Process [%s] stopped due to error" % self.name)
                    exit(1)
            self.executed = True
            logger.info("Process [%s] finished" % self.name)


class Operation:
    """A class that represents a single operation that is part of a process."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.initialized = False
        self.executed = False
        self.result = None

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args, **kwargs):
        if not self.initialized:
            self.args, self.kwargs, self.initialized = args, kwargs, True
            parent_process().add_operation(self)
            return self
        else:
            if self.args != args or self.kwargs != kwargs:
                raise ValueError(
                    (
                        "operation %s already exists with different arguments, "
                        "consider using a clone of the original operation."
                    )
                    % self.name
                )
            else:
                parent_process().add_operation(self)
                return self

    def __evaluate_args__(self, args):
        evaluated_args = []
        for arg in args:
            if type(arg) == Operation:
                arg = arg.result
            elif type(arg) == list:
                arg = self.__evaluate_args__(arg)
            elif type(arg) == dict:
                arg = self.__evaluate_kwargs__(args)
            evaluated_args.append(arg)
        return evaluated_args

    def __evaluate_kwargs__(self, kwargs):
        evaluated_kwargs = {}
        for key in kwargs:
            if type(kwargs[key]) == Operation:
                evaluated_kwargs[key] = kwargs[key].result
            elif type(kwargs[key]) == list:
                evaluated_kwargs[key] = self.__evaluate_args__(kwargs[key])
            elif type(kwargs[key]) == dict:
                evaluated_kwargs[key] = self.__evaluate_kwargs__(kwargs[key])
            else:
                evaluated_kwargs[key] = kwargs[key]
        return evaluated_kwargs

    def run(self):
        if not self.initialized:
            raise RuntimeError(
                "operation %s cannot be run before being initialized" % self.name
            )
        elif self.executed:
            return self.result
        else:
            logger.info("Operation [%s] started" % self.name)
            try:
                self.result = self.func(
                    *self.__evaluate_args__(self.args),
                    **self.__evaluate_kwargs__(self.kwargs)
                )
                self.executed = True
            except Exception:
                logger.error("Operation [%s] stopped due to error" % self.name, exc_info=True)
                raise
            logger.info("Operation [%s] finished" % self.name)
            return self.result

    def clone(self, name):
        """Create a clone of the instance with a different name."""
        existing_operation = parent_process().find_operation(name)
        cloned = existing_operation or operation(self.func)
        cloned.name = name
        return cloned


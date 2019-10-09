import sys
import logging
import traceback

name = "funcmaster"

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)5s - %(message)s"
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


class LogWrapper:
    def __init__(self, logger, source):
        self.logger = logger
        self.source = source

    def __log__(self, event, message, level):
        self.logger.log(
            level, "source='%s' event='%s' message='%s'" % (self.source, event, message)
        )

    def debug(self, message, event="info"):
        self.__log__(event, message, logging.DEBUG)

    def info(self, message, event="info"):
        self.__log__(event, message, logging.INFO)

    def warn(self, message, event="info"):
        self.__log__(event, message, logging.WARN)

    def error(self, message, event="info"):
        self.__log__(event, message, logging.ERROR)

    def critical(self, message, event="info"):
        self.__log__(event, message, logging.CRITICAL)


class Process:
    """A class that represents a complete collection of operations."""

    def __init__(self, func, name=None):
        self.operations = []
        self.func = func
        self.name = name or func.__name__
        self.initialized = False
        self.executed = False
        self.log = LogWrapper(logger, self.name)

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __call__(self):
        """Build a list of operations by doing a "dry-run"."""
        self.log.info(
            "Starting to plan the order of operations", "process_planning_started"
        )
        if not self.initialized:
            self.func()
            self.initialized = True
        self.log.info("Completed the execution plan", "process_planning_finished")
        return self

    def add_operation(self, operation):
        """Called by an operation object to add itself to the process."""
        existing_operation = self.find_operation(operation.name)
        if existing_operation == None:
            self.operations.append(operation)
            self.log.info(
                "Added operation %s" % operation.name, "process_added_operation"
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
            self.log.info("Started execution of process", "process_started")
            for operation in self.operations:
                try:
                    operation.run()
                except Exception:
                    self.log.error(
                        "Process stopped due to an error with operation %s"
                        % operation.name,
                        "process_error",
                    )
                    exit(1)
            self.executed = True
            self.log.info("Finished execution of process", "process_finished")


class Operation:
    """A class that represents a single operation that is part of a process."""

    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.initialized = False
        self.executed = False
        self.result = None
        self.log = LogWrapper(logger, self.name)

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
            self.log.info("Started execution of operation", "operation_started")
            try:
                self.result = self.func(
                    *self.__evaluate_args__(self.args),
                    **self.__evaluate_kwargs__(self.kwargs)
                )
                self.executed = True
            except Exception as e:
                self.log.error(
                    "".join(traceback.format_tb(e.__traceback__)), "operation_error"
                )
                raise
            self.log.info("Finished execution of operation", "operation_finished")
            return self.result

    def clone(self, name):
        """Create a clone of the instance with a different name."""
        existing_operation = parent_process().find_operation(name)
        cloned = existing_operation or operation(self.func)
        cloned.name = name
        cloned.log = LogWrapper(logger, name)
        return cloned


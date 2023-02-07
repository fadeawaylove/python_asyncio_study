import inspect
import objgraph


def foo():
    return inspect.currentframe()


def bar():
    return foo()


f1 = bar()

objgraph.show_refs(f1, max_depth=2, too_many=3)

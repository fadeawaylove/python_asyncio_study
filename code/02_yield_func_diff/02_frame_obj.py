import inspect
import objgraph


def foo():
    return inspect.currentframe()


foo_frame = foo()

objgraph.show_backrefs(foo.__code__)

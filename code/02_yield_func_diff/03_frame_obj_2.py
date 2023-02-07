import inspect
from objgraph import show_backrefs


def foo():
    return inspect.currentframe()


f2 = foo()
show_backrefs(foo.__code__)

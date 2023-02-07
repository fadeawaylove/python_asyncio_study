import inspect
from objgraph import show_backrefs


def foo():
    yield inspect.currentframe()


gen_foo = foo()
f = gen_foo.send(None)
show_backrefs(foo.__code__)

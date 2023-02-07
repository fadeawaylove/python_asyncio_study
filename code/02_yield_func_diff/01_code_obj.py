def foo():
    return 11


foo_code = foo.__code__

print(foo_code)

for attr in dir(foo_code):
    if attr.startswith("co_"):
        print(attr, "\t", getattr(foo_code, attr))

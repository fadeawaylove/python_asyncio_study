
def gen_func():
    a = (yield + 10) - 2
    # a = (yield 10) - 2
    # yield + 10
    # a = yield - 2
    yield a


gen_obj = gen_func()

three = gen_obj.send(None)
print(three)

res_a = gen_obj.send(1)
print(res_a)

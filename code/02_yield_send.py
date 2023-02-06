

def gen_func():
    a = yield 3
    yield a



gen_obj = gen_func()

three = gen_obj.send(None)
print(three)

res_a = gen_obj.send(10)
print(res_a)

# gen_obj.send(20)
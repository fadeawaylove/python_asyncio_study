
def gen():
    yield 3

print(gen)  # 依然是一个方法对象
print(gen()) # 只是返回值是一个生成器对象

gen_obj = gen()
# print(dir(gen_obj))

# print(next(gen_obj))

print(gen_obj.send(None))
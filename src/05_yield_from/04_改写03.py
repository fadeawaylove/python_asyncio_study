import time


def one_task():
    print("begin task")
    print("     begin big_step")
    # big_result = big_step()
    big_result = yield from big_step()
    print(f"    end big_step {big_result}")
    print("end task")


def big_step():
    print(f"        begin small_step")
    small_result = yield from small_step()
    print(f"        end small_step with {small_result}")
    return small_result * 1000


def small_step():
    print("         休息一下")
    yield time.sleep(2)
    print("         努力工作")
    return 123


# if __name__ == "__main__":
#     res = one_task()
#     print(res)
#     res.send(None)
#     res.send(None)


# 手动send太low，写个Task类来运行任务

class Task:

    def __init__(self, coro):
        self.coro = coro

    def run(self):
        while True:
            try:
                x = self.coro.send(None)
            except StopIteration as e:
                result = e
                return
            else:
                # result = ?
                print("x是多少", x)
                resul = "不知道"
        print("-------", result)


# if __name__ == "__main__":
#     t = Task(one_task())
#     t.run()


# 阻塞依然还在small_step中，能不能提出来，到Task中

class YieldFromObj:
    def __init__(self, value):
        self.value = value

    def __iter__(self):
        yield self


def small_step():
    print("         休息一下")
    yield from YieldFromObj((time.sleep, 2))
    print("         努力工作")
    return 123


# if __name__ == "__main__":
#     t = Task(one_task())
#     t.run()


# 改写Task

# class Task:

#     def __init__(self, coro):
#         self.coro = coro

#     def run(self):
#         while True:
#             try:
#                 x = self.coro.send(None)
#             except StopIteration as e:
#                 result = e
#                 return
#             else:
#                 func, value = x.value
#                 result = func(value)
#         print("-------", result)


# if __name__ == "__main__":
#     t = Task(one_task())
#     t.run()

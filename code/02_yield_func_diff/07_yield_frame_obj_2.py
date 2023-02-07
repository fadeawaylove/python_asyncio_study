def async_task_a():
    yield "a1"
    yield "a2"
    yield "a3"


def async_task_b():
    yield "b1"
    yield "b2"
    yield "b3"


def async_task_runner():
    task_a = async_task_a()
    task_b = async_task_b()

    print(next(task_a))
    print(next(task_b))
    print(next(task_a))
    print(next(task_b))
    print(next(task_b))
    print(next(task_a))


if __name__ == '__main__':
    async_task_runner()

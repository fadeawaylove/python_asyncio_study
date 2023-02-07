def task_a():
    print("我是task a")


def task_b():
    print("我是task b")


def sync_task():
    task_a()
    task_b()


if __name__ == '__main__':
    sync_task()

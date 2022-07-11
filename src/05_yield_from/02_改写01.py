import time


def one_task():
    print("begin task")
    print("     begin big_step")
    big_result = big_step()
    print(f"    end big_step {big_result}")
    print("end task")


def big_step():
    print(f"        begin small_step")
    small_result = small_step()
    print(f"        end small_step with {small_result}")
    return small_result * 1000


def small_step():
    print("         休息一下")
    yield time.sleep(2)
    print("         努力工作")
    return 123


if __name__ == "__main__":
    one_task()

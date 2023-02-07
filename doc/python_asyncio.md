# 一文彻底搞懂Python asyncio

标签（空格分隔）： Python 异步

---

本文基于Python3.6.9，适用于有一定Python异步编程基础的同学，文章重点不在介绍用法，只会选择性的将有关用法进行介绍。看完本文，能清楚知道Python asyncio是怎么一回事，并且自己动手写一个简单的asyncio的实现。

---

既然要搞懂`asyncio`
，那咱们先从官方文档看起，先看看Python文档[module-asyncio](https://docs.python.org/3.6/library/asyncio.html?module-asyncio)中的描述：

> - a pluggable event loop with various system-specific implementations;
>
> - transport and protocol abstractions (similar to those in Twisted);
>
> - concrete support for TCP, UDP, SSL, subprocess pipes, delayed calls, and others (some may be system-dependent);
>
> - a Future class that mimics the one in the concurrent.futures module, but adapted for use with the event loop;
>
> - **coroutines and tasks based on yield from (PEP 380), to help write concurrent code in a sequential fashion;**
>
> - cancellation support for Futures and coroutines;
>
> - synchronization primitives for use between coroutines in a single thread, mimicking those in the threading module;
>
> - an interface for passing work off to a threadpool, for times when you absolutely, positively have to use a library that makes blocking I/O calls.

主要关注加粗文字，大意就是：**基于yield from (PEP 380)的协程和任务，以帮助以顺序的方式编写并发代码。**

可以知道，`asyncio`中的协成和任务是基于`yield from`的，那咱们就从这里切入，一步步探究下去。

## 从yield说起

### 简单使用

我们知道，当在一个普通方法中使用`yield`关键字之后，此方法就不再是普通方法，而是生成器方法（也有的文章直接把这个方法叫做生成器）。顾名思义，直接调用此方法，返回值是一个生成器。

```

def gen():
    yield 3

print(gen)  # 依然是一个方法对象
print(gen()) # 只是返回值是一个生成器对象

```

运行结果：

```shell
<function gen at 0x7fe4291d50d0>
<generator object gen at 0x7fe42c812890>
```

如果我们想真的运行这个生成器中的代码，得使用`next`或者`send`方法。

```
gen_obj = gen()
print(next(gen_obj))
```

或者

```
gen_obj = gen()
print(gen_obj.send(None))
```

结果：

```shell
3
```

运行的同时，传值给生成器:

```python
def gen_func():
    a = yield 3
    yield a


gen_obj = gen_func()

three = gen_obj.send(None)
print(three)

res_a = gen_obj.send(10)
print(res_a)

```

输出：

```shell
3
10
```

可以看到，`10`被传进去赋值给了`a`，后又通过`yield`返回了。

将上述代码的第二个`yield`改为`return`，看看会发生什么：

```python
def gen_func():
    a = yield 3
    return a


gen_obj = gen_func()

three = gen_obj.send(None)
print(three)

res_a = gen_obj.send(10)
print(res_a)
```

输出：

```shell
3
Traceback (most recent call last):
  File "/Users/dengrunting/data/code/python_asyncio_study/code/02_yield_stop_iteration.py", line 14, in <module>
    res_a = gen_obj.send(10)
StopIteration: 10
```

第二次使用`next`方法的时候，抛出了`StopIteration`异常，这个不难理解，一个`yield`关键字对应一个`next`，方法里面只有一个`yield`，所以第二次`next`
自然就抛出异常了。但是这里并不是重点，重点是`StopIteration: 10`里面的10，虽然会抛出异常，但是也会将`return`返回的值给抛出，这里先埋个伏笔，看到后面就知道这个特点会被如何使用。

`yield`的基本使用就介绍到这里，再次强调，本文的重点不在如何使用，而是探究整个实现过程。不过此处还是留个小问题，能明白就说明真的懂了`yield`：

```python
def gen_func():
    a = (yield + 10) - 2
    yield a


gen_obj = gen_func()
gen_obj.send(None)
gen_obj.send(1)
```

两次`next`输出是什么呢？为什么是这个结果呢？（Tips：`yield`既是关键字，又是表达式。）

## 生成器与普通方法

### `code`对象

```python
def foo():
    return 11


foo_code = foo.__code__

print(foo_code)

for attr in dir(foo_code):
    if attr.startswith("co_"):
        print(attr, "\t", getattr(foo_code, attr))
```

输出：

```shell
<code object foo at 0x10a96c9d0, file "/Users/dengrunting/data/code/python_asyncio_study/code/02_yield_func_diff/01_code_obj.py", line 1>
co_argcount 	 0
co_cellvars 	 ()
co_code 	 b'd\x01S\x00'
co_consts 	 (None, 11)
co_filename 	 /Users/dengrunting/data/code/python_asyncio_study/code/02_yield_func_diff/01_code_obj.py
co_firstlineno 	 1
co_flags 	 67
co_freevars 	 ()
co_kwonlyargcount 	 0
co_lnotab 	 b'\x00\x01'
co_name 	 foo
co_names 	 ()
co_nlocals 	 0
co_posonlyargcount 	 0
co_stacksize 	 1
co_varnames 	 ()

```

随便定义一个普通方法，通过`__code__`可以取出其对应的`code`对象，`code`对象中保存了这个方法运行时需要的信息。

### 普通方法的`frame`对象

```python
import inspect
import objgraph


def foo():
    return inspect.currentframe()


foo_frame = foo()

objgraph.show_backrefs(foo.__code__)
```

输出:
![](https://gitlab.com/api/v4/projects/42641795/repository/files/tmpz64pt9ir.jpg/raw)

可以清楚的看到`code`对象不仅被`function`对象引用，还被`frame`对象引用了。方法被调用的时候，会生成一个`frame`帧对象，`frame`对象保存了方法运行时的状态。

### 普通方法依次调用

```python
def task_a():
    print("我是task a")


def task_b():
    print("我是task b")


def sync_task():
    task_a()
    task_b()


if __name__ == '__main__':
    sync_task()

```

输出：
```shell
我是task a
我是task b
```

从`frame`的角度来看上述代码运行过程：
1. `task_a`的`frame`入栈，开始执行`task_a`中的代码
2. `task_a`执行完毕，`task_a`的`frame`出栈
3. `task_b`的`frame`入栈，开始执行`task_b`中的代码
4. `task_b`执行完毕，`task_b`的`frame`出栈

从运行过程来看，是无论如何都不可能实现任务交替运行的，只能是同步的依次运行。

### 生成器的`frame`对象

```python
import inspect
from objgraph import show_backrefs


def foo():
    yield inspect.currentframe()


gen_foo = foo()
f = gen_foo.send(None)
show_backrefs(foo.__code__)

```

输出：
![](https://gitlab.com/api/v4/projects/42641795/repository/files/tmppt3s2dh6.jpg/raw)

从图中可以观察到，与普通方法相比，最大的不同就是`gen_foo`这个生成器对象引用了`frame`对象，其实这就是生成器可以暂停的原因。

---


### 生成器调用

```python
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

```

输出：
```shell
a1
b1
a2
b2
b3
a3
```

从结果可以看出，因为生成器有`frame`的引用，我们可以通过`next`方法人为控制运行的顺序，可以让`async_task_a`和`async_task_b`交替运行各自的代码。

### 小结

普通函数
- 调用函数：构建帧对象并入栈
- 函数执行结束：帧对象出栈并销毁

生成器函数
- 创建生成器：构建帧对象
- next触发运行（多次）：帧入栈
- yield获得结果（多次）：帧出栈
- 迭代结束：帧出栈并销毁
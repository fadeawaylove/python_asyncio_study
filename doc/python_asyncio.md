# 一文彻底搞懂Python asyncio

标签（空格分隔）： Python 异步

---

本文基于Python3.6.9，适用于有一定Python异步编程基础的同学，文章重点不在介绍用法，只会选择性的将有关用法进行介绍。看完本文，能清楚知道Python asyncio是怎么一回事，并且自己动手写一个简单的asyncio的实现。

---

既然要搞懂`asyncio`，那咱们先从官方文档看起，先看看Python文档[module-asyncio](https://docs.python.org/3.6/library/asyncio.html?module-asyncio)中的描述：

> - a pluggable event loop with various system-specific implementations;

> - transport and protocol abstractions (similar to those in Twisted);

> - concrete support for TCP, UDP, SSL, subprocess pipes, delayed calls, and others (some may be system-dependent);

> - a Future class that mimics the one in the concurrent.futures module, but adapted for use with the event loop;

> - **coroutines and tasks based on yield from (PEP 380), to help write concurrent code in a sequential fashion;**

> - cancellation support for Futures and coroutines;

> - synchronization primitives for use between coroutines in a single thread, mimicking those in the threading module;

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
第二次使用`next`方法的时候，抛出了`StopIteration`异常，这个不难理解，一个`yield`关键字对应一个`next`，方法里面只有一个`yield`，所以第二次`next`自然就抛出异常了。但是这里并不是重点，重点是`StopIteration: 10`里面的10，虽然会抛出异常，但是也会将`return`返回的值给抛出，这里先埋个伏笔，看到后面就知道这个特点会被如何使用。

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


### 与普通方法的区别




---
title: Python的扩展-Python和C混合编程
date: 2016-07-03 17:42:55
tags: Python
---

# 第一部分: 介绍/动机

## 什么是扩展

扩展就是将 Python 或其它语言（例如C/C++）嵌入到Python当中。
一般来说,所有能被整合或导入到其它 python 脚本的代码,都可以被称为扩展。
大部分 Python 的扩展都是用 C 语言写的，本文示例用 C 语言写的，不过很容易移植到 C++中。

## 扩展的好处

- **添加/额外的(非 Python)功能**。扩展 Python 的一个原因就是出于对一些新功能的需要,
而 Python 语言的核心部分并没有提供这些功能。这时,通过纯 Python 代码或者编译扩展都
可以做到。但是有些情况,比如创建新的数据类型或者将 Python 嵌入到其它已经存在的应
用程序中,则必须得编译。
- **性能瓶颈的效率提升**。众所周知,由于解释型的语言是在运行时动态的翻译解释代码,这导
致其运行速度比编译型的语言慢。一般说来,把所有代码都放到扩展中,可以提升软件的整
体性能。但有时,由于时间与精力有限,这样做并不划算。通常,先做一个简单的代码性能
测试,看看瓶颈在哪里,然后把瓶颈部分在扩展中实现会是一个比较简单有效的做法。效果
立竿见影不说,而且还不用花费太多的时间与精力。
- **保持专有源代码私密**。创建扩展的另一个很重要的原因是脚本语言都有一个共同的缺陷,那
就是所有的脚本语言执行的都是源代码,这样一来源代码的保密性便无从谈起了。把一部分
代码从 Python 转到编译语言就可以保持专有源代码私密。因为,你只要发布二进制文件就
可以了。编译后的文件相对来说,更不容易被反向工程出来。因此,代码能实现保密。尤其
是涉及到特殊的算法,加密方法以及软件安全的时候,这样做就显得非常至关重要了。

另一种对代码保密的方法是只发布预编译后的.pyc 文件。这是介于发布源代码(.py 文件)和把
代码移植到扩展这两种方法之间的一种较好的折中的方法。

# 第二部分: 创建 Python 扩展

创建 Python 扩展的步骤
  1. 创建要扩展的应用程序代码（以C语言为例）
  2. 用样板来包装 C 代码
    - 包含 Python 的头文件
    - 为每个模块的每个函数增加一个型如PyObject * Module_func() 的包装函数
    - 为每个模块增加一个型如PyMethodDef ModuleMethods[]的数组
    - 增加模块初始化函数 void InitModule()
  3. 编译，导入和测试

## 创建应用程序代码

创建如下 Extest.c 文件
``` c
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <python2.7/Python.h>

int Fac(int n)
{
    if (n < 2)
        return 1;
    return n * Fac(n-1);
}

int Pow(int a, int n)
{
    if (n == 0)
        return 1;
    else if (n == 1)
        return a;
    else if (n % 2 == 1)
        return a * Pow(a, n/2) * Pow(a, n/2);
    else
        return Pow(a, n/2) * Pow(a, n/2);
}

char *Reverse(char *str)
{
    char ch;
    char *start = str;
    char *end = str + strlen(str);
    while (start < end) {
        ch = *start;
        *start++ = *--end;
        *end = ch;
    }
    return str;
}

int main(void)
{
    printf("0! = %d\n", Fac(0));
    printf("1! = %d\n", Fac(1));
    printf("2! = %d\n", Fac(2));
    printf("4! = %d\n", Fac(4));

    printf(">>> Pow(0,3) = %d\n", Pow(0,3));
    printf(">>> Pow(1,2) = %d\n", Pow(1,2));
    printf(">>> Pow(2,3) = %d\n", Pow(2,3));
    printf(">>> Pow(4,2) = %d\n", Pow(4,2));

    char str[] = "12345";
    printf("<><> befor: %s\n", str);
    printf("<><> after: %s\n", Reverse(str));
    return 0;

}
```

## 用样板来包装 C 代码

### 包含 Python 的头文件
给 C 代码中添加头文件
``` c
#include <Python.h>
```

如果电脑上同时装有 Python2 和 Python3
则要详细区分
``` c
#include <python2.7/Python.h>
或
#include <python3.4m/Python.h>
```

### 为每个模块的每个函数增加一个型如PyObject * Module_func() 的包装函数
包装函数的作用：
    1. 先把 Python 的值传递给 C。
    2. 调用相关的函数。
    3. 把函数的计算结果转换成 Python 的对象。
    4. 返回给 Python。

从 Python 到 C 的转换就用PyArg_Parse\* 系列函数。
从 C 转到 Python 的时候就用 Py_BuildValue()函数。

| 函数                          | 描述                                                   |
| :---------------------------- | :----------------------------------------------------- |
| PyArg_ParseTuple()            | 把 Python 传过来的参数转为 C                           |
| PyArg_ParseTupleAndKeywords() | 与 PyArg_ParseTuple()作用相同,但是同时解析关键字参数   |
| PyObject\* Py_BuildValue()    | 把 C 的数据转为 Python 的一个对象或一组对象,然后返回之 |

| Format Code | Python Type | C/C++ Type     |
| :---------: | :---------: | :------------: |
| s           | str         | char\*         |
| z           | str/None    | char\*/NULL    |
| i           | int         | int            |
| l           | long        | long           |
| c           | str         | char           |
| d           | float       | double         |
| D           | complex     | Py_Complex\*   |
| O           | (any)       | PyObject\*     |
| S           | str         | PyStringObject |

``` c
static PyObject* Extest_fac(PyObject *self, PyObject *args)
{
    int num;
    if (!PyArg_ParseTuple(args, "i", &num))
        return NULL;
    return (PyObject *)Py_BuildValue("i", Fac(num));
}
```
> - args是Python传过来的数据
> - PyArg_ParseTuple()中 格式化字符串 "i" 表示期望得到 1 个 int
> - 如果传进来的是 1 个int的话，将args存储到num变量中
> - Py_BuildValue()中 格式化字符串 "i" 表示期望返回 1 个 int
> - 将 Fac(num) 转换为 Python 的整数类型并返回


``` c
static PyObject* Extest_pow(PyObject *self, PyObject *args)
{
    int a, n;
    if (!PyArg_ParseTuple(args, "ii", &a, &n))
        return NULL;
    return (PyObject *)Py_BuildValue("i", Pow(a,n));
}
```
> - PyArg_ParseTuple()中 格式化字符串 “ii” 表示期望得到 2 个 int
> - PyArg_ParseTuple() 失败返回NULL

``` c
static PyObject* Extest_reverse(PyObject *self, PyObject *args)
{
    char *oldstr;
    char *dupstr;
    PyObject *result;
    if (!PyArg_ParseTuple(args, "s", &oldstr))
        return NULL;
    result = (PyObject *)Py_BuildValue("ss", oldstr, dupstr=Reverse(strdup(oldstr)));
    free(dupstr);
    return result;
}
```
> - PyArg_ParseTuple()中 格式化字符串 “s” 表示期望得到 1 个 字符串
> - Py_BuildValue() 中 格式化字符串 “ss” 表示返回包含 2 个字符串的元组
> - free(dupstr) 避免把c语言中泄露内存问题带入Python

### 为每个模块增加一个型如PyMethodDef ModuleMethods[]的数组
``` c
static PyMethodDef ExtestMethods[] = {
    {"fac", Extest_fac, METH_VARARGS},
    {"pow", Extest_pow, METH_VARARGS},
    {"reverse", Extest_reverse, METH_VARARGS},
    {"test", Extest_test, METH_VARARGS},
    {NULL, NULL},
};
```
> 这个数组由多个数组组成。
> 每一个数组包含了函数在Python中的名字，对应的包装函数的名字，METH_VARARGS常量。
> METH_VARARGS 常量表示参数以tuple形式传入。
> 如果我们要使用PyArg_ParseTupleAndKeywords()函数来分析命名参数的话,我们还需要让这个标志常量与METH_KEYWORDS 常量进行逻辑与运算。
> 最后,用两个 NULL 来结束我们的函数信息列表。


### 增加模块初始化函数 void InitModule()
``` c
void initExtest(void)
{
    Py_InitModule("Extest", ExtestMethods);

}
```
> 初始化函数在模块导入的时候被解释器调用。
> Py_InitModule() 函数的第一个参数是我们创建的模块的模块名。
> 第二个参数是模块中的函数与包装函数对应关系的数组。


## 编译,导入和测试

### 创建 setup.py
``` python
#!/usr/bin/env python

from distutils.core import setup, Extension

MOD = 'Extest'
setup(name=MOD,
      version = "1.0"
      description = "This module is my testpackage"
      ext_modules=[Extension(MOD, sources=['Extest.c'])])
```
> 使用distutils可以将编写的python模块或包安装到python目录中去。
> setup() 函数中name是模块在Python中的名字
> sources 是扩展包的源文件

### 通过运行 setup.py 来编译和链接代码
``` sh
$ ./setup.py build
running build
running build_ext
building 'Extest' extension
creating build
creating build/temp.linux-x86_64-2.7
gcc -pthread -fno-strict-aliasing -g -O2 -DNDEBUG -g -fwrapv -O3 -Wall -Wstrict-prototypes -fPIC -I/usr/local/include/python2.7 -c Extest.c -o build/temp.linux-x86_64-2.7/Extest.o
creating build/lib.linux-x86_64-2.7
gcc -pthread -shared build/temp.linux-x86_64-2.7/Extest.o -o build/lib.linux-x86_64-2.7/Extest.so
```

### 从 Python 中导入模块
``` sh
$ sudo ./setup.py install
running install
running build
running build_ext
running install_lib
copying build/lib.linux-x86_64-2.7/Extest.so -> /usr/local/lib/python2.7/site-packages
running install_egg_info
Writing /usr/local/lib/python2.7/site-packages/Extest-1.0-py2.7.egg-info
```

### 测试
将源代码中的main()函数改为test()函数，因为一个系统中只能有一个main()函数.
用Extest_test()函数把test()函数包装起来。

``` c
static PyObject* Extest_test(PyObject *self, PyObject *arg)
{
    test();
    return (PyObject *)Py_BuildValue("");

}
```
> Extest_test()模块函数只负责运行 test()函数,并返回一个空字符串。
> Python 的 None 作为返回值,传给了调用者。

``` sh
$ python
Python 2.7.10 (default, Jul  5 2016, 11:11:20) 
[GCC 4.8.4] on linux2
Type "help", "copyright", "credits" or "license" for more information.
>>> import Extest
>>> Extest.fac(4)
24
>>> Extest.pow(2,3)
8
>>> Extest.reverse('abcdef')
('abcdef', 'fedcba')
>>> Extest.test()
0! = 1
1! = 1
2! = 2
4! = 24
>>> Pow(0,3) = 0
>>> Pow(1,2) = 1
>>> Pow(2,3) = 8
>>> Pow(4,2) = 16
<><> befor: 12345
<><> after: 54321
>>>
```

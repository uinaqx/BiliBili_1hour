# 在真实操作系统里连接 C 调用者

这组三个平台的基础函数都实现 `uint64_t add_two(uint64_t, uint64_t)`，预期输出为 `12`。请选择目标平台匹配的 64 位工具链。它们与 `examples/x86_64`、`examples/aarch64` 中带固定模拟器入口地址的片段分开保存。

## Linux x86-64 / System V AMD64

```sh
nasm -f elf64 x86_64_linux.asm -o add_two.o
gcc -std=c11 -Wall -Wextra driver.c add_two.o -o add_demo
./add_demo
```

## Linux AArch64 / AAPCS64

```sh
gcc -std=c11 -Wall -Wextra driver.c aarch64_linux.s -o add_demo
./add_demo
```

在其他主机交叉编译时，改用对应 AArch64 Linux 工具链，并在适当的目标系统或用户态仿真环境运行。

## Windows x64

使用 Visual Studio x64 开发者命令提示符：

```bat
nasm -f win64 x86_64_windows.asm -o add_two.obj
cl /W4 driver.c add_two.obj /Fe:add_demo.exe
add_demo.exe
```

本例是没有局部栈帧、没有继续调用的叶函数；需要复杂栈帧的 Windows 函数还应按平台规则提供展开信息。

## 本轮实际验证范围

本机已用 NASM 生成 ELF64 与 Win64 目标文件，并核验文件格式。Windows 环境中的现有 GCC 为 32 位工具链；本轮没有使用它链接 64 位目标。原生可执行文件运行留给相应目标环境。视频中的整数行为已通过实际机器码的处理器模拟器执行验证，结果见 `build/examples-verification.json`。

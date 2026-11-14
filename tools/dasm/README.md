# Disassembler (DASM)
*"Disassembly tool to better analyze compiled RISCII images"*

## Purpose

To disassemble RISCII images into "assembly" for 1) testing compiler implementations and 2) easier analysis of low-level code.

## Overview

- [Usage](#usage)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|dasm             |Disassembler program                                |
|image            |binary file representing a RISCII program           |
|word (length)    |16 bits wide                                        |
|text memory      |64 KB address space for instruction storage         |
|data memory      |64 KB address space for data storage + mapping      |
|immediate (value)|constant binary value- often varies in bit width    |

## Referenced Material

|Reference Doc/Path|Reason                                           |
|------------------|-------------------------------------------------|
|PR2000            |basis for translating image                      |

---

## Usage

DASM converts a single RISCII binary image into a ".dasm" file (assembly file prioritizing readability over re-compilability). It is invoked by calling (via Python) `src/main.py` followed by arguments. In input image is required.

```
$ python src/main.py -h
[ERR] Disassembles RISCII image into assembly
[ERR] Usage: (dasm) [options] <input image>
[ERR] Options:
[ERR]   -h          print help menu and exit
[ERR]   -ll   <arg> set log verbosity (choices = ('quiet', 'error', 'warning', 'info', 'debu
[ERR]               g'))
[ERR]   -o    <arg> set output file path/name
[ERR]   -t    <arg> set output type of immediates (choices = ('int', 'uint', 'hex'))
[ERR]   -werr       treat warnings as errors
[ERR]   -addr       print addresses of items
[ERR]   -raw        print raw instructions
```

Optional arguments are used to modify the process and/or output.

|Option|Description                                                                       |
|------|----------------------------------------------------------------------------------|
|h     |prints help menu and exits successfully                                           |
|ll    |controls how much info is printed while running                                   |
|o     |sets the output file- defaults to input file with '.dasm' extension               |
|t     |sets formatting type of integers in the output file                               |
|werr  |allows warnings to act like errors- halting execution and returning a failure code|
|addr  |prints addresses of instructions/data in the output file                          |
|raw   |prints raw values of instructions in the output file next to instructions         |

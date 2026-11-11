# Disassembler (DASM)
*"Disassembly tool to better analyze compiled RISCII images"*

## Purpose

To disassemble RISCII images into "assembly" for 1) testing compiler implementations and 2) easier analysis of low-level code.

## Overview

- TODO

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|dasm             |Disassembler program                                |
|ISA              |instruction set architecture                        |
|word (length)    |16 bits wide                                        |
|text memory      |64 KB address space for instruction storage         |
|data memory      |64 KB address space for data storage + mapping      |
|immediate (value)|constant binary value- often varies in bit width    |

## Referenced Material

|Reference Doc/Path|Reason                                           |
|------------------|-------------------------------------------------|
|PR2000            |basis for translating image                      |

---

## TODO List

- add output functionality
    - warn about overwritting a file
    - ensure file is only output on success- delete if error mid through
- add info summary
- add option to treat warnings as errors
- add option to include addresses in output
- add option to include raw instruction in output
- document usage

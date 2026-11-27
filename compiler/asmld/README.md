# Assembler Linker (asmld)
*"Assembler/Linker program to create RISCII binary images from assembly code"*

## Purpose

To assemble and link assembly files into a unified RISCII binary image (for hardware execution).

## Overview

- [TODO](#todo)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|asmld            |assembler/linker program                            |
|image            |binary file representing a RISCII program           |
|word (length)    |16 bits wide                                        |
|text memory      |64 KB address space for instruction storage         |
|data memory      |64 KB address space for data storage + mapping      |
|immediate (value)|constant binary value- often varies in bit width    |

## Referenced Material

|Reference Doc/Path|Reason                                           |
|------------------|-------------------------------------------------|
|PR2000            |basis for creating binary image                  |
|PR3000            |basis for translating assembly language          |

---

## TODO

general commands

- zbuild: std build, automated versining
- zbuild (ver): use manual version for build
- ztag (ver): add version tag to prior commit (vx.x.x)
- zclean: clean build
- zrun: run built exe

# PR3000: Assembly Language Architecture
*"Language for low level reading/writing of software"*

## Purpose

To layout expectations for how low level software is read, written, and compiled. This document describes a low level "assembly" programming language.

> **Note**: This language is only going to be assembled against the RISCII ISA. In lieu of this, the architecture makes ISA targeted decisions (e.g. max integer lengths) that would usually be made by the compiler implementing the language.

## Overview

- [TODO](#todo)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|assembly         |low level language described by this document       |
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

## TODO

- variable types
    - flags
    - registers
    - immediates (int and hex)
    - labels
    - strings
    - arrays
- statements
    - instruction
    - built-in function
        - _la (load label or immediate)
        - _br (BRC with label or immediate, doesn't adjust if not in BRC range)
    - data init
    - bss reserve
    - label decl (applies to next instr/func/data/bss)
    - label mod (edit to apply to next label decl)
        - global (invert 'scope' rule)
        - weak (invert 'link' rule)
- linkage
    - "scope": labels are implicitly local on decl
    - "link": labels prefer local defs over global defs
    - "start": "__START" label expected to be global declared and tied to instr/func
    - "reserve": several labels are globally reserved and can be referenced
        - __BSS: first addr of bss memory
        - __FREE: first addr of free memory
        - __SIZE: total size of the binary in bytes
- misc
    - comments
- CHANGES
    - add multi-line comment
    - consider fleshing out _br as a generic "jump wherever needed on condition or no condition"
    - consider 'section' for opt removal (ie removal by function ref vs any label any ref)
    - consider edits needed to improve debug (eg to get all labels, blocks of code, named scoped vars)
    - consider edits needed to turn into static lib
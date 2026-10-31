# PR2000: Instruction Set Architecture
*"Common interface between hardware and software"*

## Purpose

To lay out expectations allowing hardware and software to interface with each other. This document describes how to build firmware images and high level hardware.

## Overview

- [Hardware Architecture](#hardware-architecture)
- [Binary Image](#binary-image)
- [Instruction Set](#instruction-set)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|ISA              |Instruction Set Architecture                        |
|word (length)    |16 bits wide                                        |
|text memory      |64 KB address space for instruction storage         |
|data memory      |64 KB address space for data storage + mapping      |
|immediate (value)|constant binary value- often varies in bit width    |
|sext(), zext()   |signed, zero extended value- extended to word length|
|int16            |word length signed integer- usually for interpreting|

---

## Hardware Architecture

### Core Processor

Instructions directly access 8 word-length registers (R0 thru R7) and indirectly affect the program counter (PC) and condition codes (CC).

|Name |Full Name      |Description                                                   |
|-----|---------------|--------------------------------------------------------------|
|R0-R7|register file  |common/direct use registers for program                       |
|PC   |program counter|byte address of the instruction being fetched from text memory|
|CC   |condition codes|flags describing result of previous data operation            |

### Memory

Instructions and data use separate address spaces (text and data memory, respectively). Each space is addressed with word-length addresses (ie 64 KB spaces). Each space is byte addressable, though is accessed by word. As such, addresses are rounded down to the nearest aligned word. Data memory is divided into free/common use memory and memory-mapped peripherals.

**Text Memory**

|Address Range  |Range Name|Access|Description                |
|---------------|----------|------|---------------------------|
|0x0000 - 0xFFFF|program   |Rd    |program's instruction space|

**Data Memory**

|Address Range  |Range Name|Access|Description                |
|---------------|----------|------|---------------------------|
|0x0000 - 0x7FFF|free      |Rd/Wr |program's data space       |
|0x8000 - 0xFFFF|mapped    |Rd/Wr |memory mapped hardware     |

### State Machine

The processor can be put in a paused state, where neither instructions or interrupts are executed. When not paused, the processor executes instructions in either an application or interrupt state. The application state may be preempted by an interrupt, whereas the interrupt state cannot.

|State|Full Name  |Execute Instructions|Allow Pausing|Allow Interrupts|
|-----|-----------|--------------------|-------------|----------------|
|PSE  |pause      |No                  |-            |-               |
|INT  |interrupt  |Yes                 |Yes          |No              |
|APP  |application|Yes                 |Yes          |Yes             |

## Binary Image

Images are organized into two sections (text and data, in that order) of big-endian words. Each section begins with a single header word equal to the number of words in that section (excluding the header word). The total size of the image (both sections, plus their headers) is at most 64 KB. An empty section consists of a header word set to `0x0000`.

The text and data sections are loaded into text and data memory, respectively (starting at `0x0000` in each memory space).

**(Start of Image)**

|Section|Sub-Item|Length (words)|Description                    |
|-------|--------|--------------|-------------------------------|
|text   |header  |1             |number of words in text section|
|       |value   |0-32767       |value of the text memory       |
|data   |header  |1             |number of words in data section|
|       |value   |0-32767       |value of the data memory       |

**(End of Image)**

## Instruction Set


**TODO**
- intro/abbreviations
- summary chart
- detailed (condense?)
- condition codes
- state interactions

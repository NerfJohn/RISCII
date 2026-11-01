# PR2000: Instruction Set Architecture
*"Common interface between hardware and software"*

## Purpose

To lay out expectations allowing hardware and software to interface with each other. This document describes how to build firmware images and high level hardware.

> **Note**: Actual ISAs don't tend to specify the binary image format. I've decided to specify it here to keep hardware/software interfacing in one place. This works as I don't intend supporting many hardware archs.

## Overview

- [Hardware Architecture](#hardware-architecture)
- [Binary Image](#binary-image)
- [Instruction Set](#instruction-set)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|ISA              |instruction set architecture                        |
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

### Bootloader/Interrupt Vector

The first 64 words (`0x0000` - `0x007F`) of text memory is reserved for the interrupt vector- divided into 16 four word chunks. The first chunk (`0x0000` - `0x0007`) is reserved for the bootloader (ie the image begins execution at PC = `0x0000`).

|Address Range  |Range Name|Access|Description                |
|---------------|----------|------|---------------------------|
|0x0000 - 0x0007|bootloader|Rd    |reserved for bootloader    |
|0x0008 - 0x007F|int vector|Rd    |interrupt vectors          |
|0x0080 - 0xFFFF|program   |Rd    |program's instruction space|


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

Instructions are word length and stored in text memory (word aligned). Instructions operate on word length values (registers, addresses, immediates). Below are abbreviations used to refer to common bit fields within instructions.

|Abbreviation       |Description                                      |
|-------------------|-------------------------------------------------|
|DST                |destination register for result of operation     |
|SR1                |source register for first operand of operation   |
|SR2                |source register for second operand of operation  |
|SRC                |source register for value to write to data memory|
|4bIm               |4-bit immediate value                            |
|5bImm              |5-bit immediate value                            |
|6bOfst             |6-bit immediate value                            |
|8bImmVal           |8-bit immediate value                            |
|(lowercase letters)|flags with instruction specific effects          |

### Instructions

|Operation Name           |Abbreviation|Bitwise Layout        |Operation                      |Op Type|Notes            |
|-------------------------|------------|----------------------|-------------------------------|-------|-----------------|
|Bitwise AND (VAR)        |AND         |1111-DST-SR1-000-SR2  |DST = SR1 & SR2                |data   |see footnote A   |
|Bitwise AND (IMM)        |AND         |1111-DST-SR1-1-5bImm  |DST = SR1 & sext(5bImm)        |data   |                 |
|Bitwise OR (VAR)         |ORR         |1110-DST-SR1-000-SR2  |DST = SR1 \| SR2               |data   |                 |
|Bitwise OR (IMM)         |ORR         |1110-DST-SR1-1-5bImm  |DST = SR1 \| sext(5bImm)       |data   |                 |
|Bitwise XOR (VAR)        |XOR         |1011-DST-SR1-000-SR2  |DST = SR1 ^ SR2                |data   |                 |
|Bitwise XOR (IMM)        |XOR         |1011-DST-SR1-1-5bImm  |DST = SR1 ^ sext(5bImm)        |data   |                 |
|Shift Logic Left (VAR)   |SHL         |1100-DST-SR1-000-SR2  |DST = SR1 << SR2               |data   |                 |
|Shift Logic Left (IMM)   |SHL         |1100-DST-SR1-10-4bIm  |DST = SR1 << zext(4bIm)        |data   |                 |
|Shift Right (VAR)        |SHR         |1101-DST-SR1-0-a-0-SR2|DST = SR1 >>a SR2              |data   |see footnote C   |
|Shift Right (IMM)        |SHR         |1101-DST-SR1-1-a-4bIm |DST = SR1 >>a zext(4bIm)       |data   |see footnote C   |
|Arithmetic Add (VAR)     |ADD         |1000-DST-SR1-000-SR2  |DST = SR1 + SR2                |data   |                 |
|Arithmetic Add (IMM)     |ADD         |1000-DST-SR1-1-5bImm  |DST = SR1 + sext(5bImm)        |data   |                 |
|Arithmetic Subtract (VAR)|SUB         |1001-DST-SR1-000-SR2  |DST = SR2 - SR1                |data   |SR1 is subtrahend|
|Arithmetic Subtract (IMM)|SUB         |1001-DST-SR1-1-5bImm  |DST = sext(5bImm) - SR1        |data   |SR1 is subtrahend|
|Load Byte Immediate      |LBI         |1010-DST-s-8bImmVal   |DST = int16(s, DST, 8bImmVal)  |data   |see footnote D   |
|Load Memory Word         |LDR         |0101-DST-SR1-6bOfst   |DST = MEM(addr(SR1, 6bOfst))   |control|see footnote A,B |
|Store Memory Word        |STR         |0100-SRC-SR1-6bOfst   |MEM(addr(SR1, 6bOfst)) = SRC   |control|see footnote B   |
|Swap Register Memory     |SWP         |0001-DST-SR1-6bOfst   |tandem(LDR,STR); rejoin()      |control|see footnote B,E |
|Branch Conditional       |BRC         |0010-nzpc-8bImmVal    |PC = condJump(nzpc, 8bImmVal)  |control|see footnote F   |
|Jump/Link Register       |JLR         |0111-DST-SR1-0-5bImm  |PC = addr(SR1, 5bImm); DST = PC|control|see footnote B   |
|Jump Register            |JPR         |0110-000-SR1-0-5bImm  |PC = addr(SR1, 5bImm)          |control|see footnote B   |
|Return From Interrupt    |RTI         |0110-000-000-1-00000  |revertPC_CC(); setState(APP)   |control|see footnote G   |
|No Operation             |NOP         |0000-000000000000     |spin()                         |control|does nothing     |
|Halt/Pause               |HLT         |0011-000000000000     |setState(PSE)                  |control|enter PSE state  |

**Footnote A: Operation Type**

Instruction are organized into types data and control. Data operations update the `CC` register based on the result written to DST. Control operations explcitly do not update `CC`, but do implicitly shift immediate values left by 1 (after extension; before calculation).

|Op Type|Updates CC|Shifts Immediate|
|-------|----------|----------------|
|data   |yes       |no              |
|control|no        |yes             |

**Footnote B: Address Calculation**

Addresses are calculated between a source register and a signed extended immediate value. Be wary of immediate's original length and operation type for immediate resolution prior to calculation.

```
addr(register, immediate):
    src2 = sext(immediate)
    if (control type)? {src2 <<= 1}
    return register + src2          // subject to word length overflow
```

**Footnote C: Shift Right**

The `a` flag controls whether a shift logic right or shift arithmetic right is performed.

|Flag Value |Operation Name        |
|-----------|----------------------|
|clear (=0) |shift logic right     |
|set (=1)   |shift arithmetic right|

**Footnote D: Load Byte Immediate**

The `s` flag controls how the word is generated. `DST` can be set to the immediate value or have the immediate shifted in.

|Flag Value |Operation Name    |Operation                   |
|-----------|------------------|----------------------------|
|clear (=0) |set as immediate  |DST = sext(8bImmVal)        |
|set (=1)   |shift immediate in|DST = (DST << 8) \| 8bImmVal|

**Footnote E: Swap Register Memory**

SWP switches the values between `DST` and `MEM(addr(SR1, 6bOfst))` within one instruction. Instruction is atomic, though implementation may split up precise load/store operations.

```
swp():
    disable_interrupts()
    loc  = addr(DST, 6bOfst) // see footnote B
    temp = MEM(loc)
    MEM(loc) = DST
    DST  = temp
    enable_interrupts()
```

**Footnote F: Branch Conditional**

Sets `PC` to `PC + 2 + sext(8bImmVal << 1)` if certain conditions are met. If all conditions are not met, instruction has no effect.

The conditions to set the `PC` are as follows:

1. For flags `nzp`, both hardware and instruction have at least one of the same flag both set.
2. If instruction's flag `c` is set, the hardware's flag `c` is also set.

**Footnote G: Return From Interrupt**

Reverts `PC` and `CC` registers to their values prior to entering the `INT` state. Also switches the state from `INT` to `APP`. If the processor is not in `INT` state, instruction has no effect.

```
rti():
    if INT == state:
        PC = savedPC()
        CC = savedCC()
        state = APP
```

### Condition Codes

`CC` flags infer data about the result of the computed value. `CC` is updated after executing a data operation/instruction.

|Flag|Flag Name|Meaning If Set                                      |
|----|---------|----------------------------------------------------|
|n   |negative |Last data operation result, as int16, was negative  |
|z   |zero     |Last data operation result, as int16, was zero      |
|p   |positive |Last data operation result, as int16, was positive  |
|c   |carry    |Last data operation, as subtract, had carry-out     |

When determining if conditions are met, the flags between the BRC instruction and hardware's stored version are compared. The comparision logic is below

```
nzpMatch = (bool)(brcNzp & hardwareNzp)    // BRC and HW must have matching nzp
cMatch   = (bool)(brcC ? hardwareC : true) // if BRC c set, then HW c must be set
COND_MET = nzpMatch & cMatch
```

For convenience, common combinations of condition code flags (and their abstract meaning) are provided in the table below.

|Condition|Last Data Operation|Abstract Meaning                            |
|---------|-------------------|--------------------------------------------|
|n        |B - A              |If A > B (signed)                           |
|p        |B - A              |If A < B (signed)                           |
|nz       |B - A              |If A >= B (signed)                          |
|zp       |B - A              |If A <= B (signed)                          |
|npc      |A - B              |If A > B (unsigned)                         |
|npc      |B - A              |If A < B (unsigned)                         |
|nzpc     |A - B              |If A >= B (unsigned)                        |
|nzpc     |B - A              |If A <= B (unsigned)                        |
|z        |B - A              |A == B                                      |
|np       |B - A              |A != B                                      |
|nzpc     |Arithmetic Subtract|Carry-out occurred                          |
|nzp      |Any Operation      |Instruction Relative Jump                   |

### Implicit Operations

`PC` is expected to be implicitly incremented by 2 (ie one word in byte addressing) after fetching each instruction (unless operated on by an instruction or eternal event).

```
if (noPCInstruction | externalEvt) {PC += 2}
```

When in `APP` mode, the processor may execute an interrupt. Interrupts save the current `PC` and `CC` values, switch the state from `APP` to `INT`, and set the `PC` to an address within the interrupt vector based on the interrupt. New `PC` addresses always align to the start of one of the bootloader/interrupt vector's 16 chunks.

```
interrupt()
    savePC(PC)
    saveCC(CC)
    state = INT
    PC = 8 * intrType() // 4 word (8 byte) chunks
```

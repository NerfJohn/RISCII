# PR3000: Assembly Language Architecture
*"Language for low level reading/writing of software"*

## Purpose

To layout expectations for how low level software is read, written, and compiled. This document describes a low level "assembly" programming language.

> **Note**: Assembly language standards DO tend to be ISA specific. Regardless of this, this standard will make specific decisions (e.g. max integer length) to keep the "assembly to binary" translation notes in one place.

## Overview

- [Variable Arguments](#variable-arguments)
- [TODO](#todo)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|assembly         |low level language described by this document       |
|image            |binary file representing a RISCII program           |
|word (length)    |16 bits wide                                        |
|text memory      |64 KB address space for instruction storage         |
|data memory      |64 KB address space for data storage + mapping      |
|NULL             |0x00 integer value                                  |

## Referenced Material

|Reference Doc/Path|Reason                                           |
|------------------|-------------------------------------------------|
|PR2000            |basis for translating assembly to image          |

---

## Variable Arguments

### Registers

Registers represent the processor's 8 word-length registers- being used to describe instructions. Registers begin with prefix `$` followed by a number (0-7) indicating which register.

```
$0  ; 0th processor word-length register
$4  ; 4th processor word-length register
$7  ; 7th processor word-legnth register
$8  ; INVALID- processor only has 8 word-length registers (0-7)
```

### Flags

Flags represent bit flags present in some instructions. Flags are instruction specific, and their presence indicates setting the flag. Flags begin with prefix `%` followed by instruction specific letters- each letter a unique flag.

```
%a    ; ARITH flag- used by the SHR instruction
%nzpc ; NEG, ZERO, POS, and CARRY flags- used by the BRC instruction
%nz   ; NEG and ZERO flags- POS and CARRY assumed cleared
%q    ; Unknown flag- corresponds to no known instruction
```

### Immediates

Immediates are constant integer values represented as integer or hexadecimal numbers. Sign and size interpretation are context driven- though an immediate will require a minimal number of bits to represent.

```
5      ; decimal value "5"   - uses at least 3 bits
-12    ; decimal value "-12" - uses at least 5 bits
0xA    ; decimal value "10"  - uses at least 4 bits
0x000A ; decimal value "10"  = uses at least 4 bits
```

### Strings

Strings are byte characters enclosed by quotations (with support for some escape chars). Strings are appended/padded with `NULL` as needed to be word aligned. Two chars are stored per word, with the "earlier" char placed in the higher value byte and earlier "2-char words" appearing at lower addresses.

```
"foobar" ; 6 byte char array- stored in word sequence [f,o] [o,b] [a,r]
"pad"    ; 4 byte char array- stored in word sequence [p,a] [d, NULL]
"bad     ; INVALID- quotations do not enclose bytes

         ; \xHH              ; generic escape to represent any char (replace HH with hex values)
         ; \n \r \t \" \\ \0 ; supported common escape shortcuts
```

### Labels

Labels are user defined names used to abstract text/data memory addresses (address resolved during assembly/linking). Labels are alphanumeric tokens (including `_`) that do not begin with a number. Resolved addresses are always word-length.

```
foobar     ; valid label- uses only letters
Connor2    ; valid label- uses letters/numbers
_low_score ; valid label- uses letters/underscore
0Nope      ; INVALID- label cannot begin with a number
```

### Tuple

Tuples are aggregate combos of 0+ immediates, strings, labels, or tuples. Tuples are enclosed with curly brackets- using whitespace to delimit items. Items are first resolved for value/sizing before the tuple is resolved. Items are place in order of appearance, with earlier items appearing at lower addresses.

Within tuples, immediates are always 16-bit "any sign" values.

```
{0x34 'beef' MyLabel}          ; tuple of 3 items- 16-bit value "0x0034" placed in first word (12 bytes total)
{}                             ; empty tuple (0 bytes total)
{"nums" {-32768 -1 0 1 65535}} ; nested tuple- "[n][u]" placed in first word (24 bytes total)
{foo bar                       ; INVALID- tuple not closed
```

## TODO

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
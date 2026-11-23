# PR3000: Assembly Language Architecture
*"Language for low level reading/writing of software"*

## Purpose

To layout expectations for how low level software is read, written, and compiled. This document describes a low level "assembly" programming language.

> **Note**: Assembly language standards DO tend to be ISA specific. Regardless of this, this standard will make specific decisions (e.g. max integer length, compiler-specific feature support) to keep the "assembly to binary" translation notes in one place.

## Overview

- [Variable Arguments](#variable-arguments)
- [Statements](#statements)
- [Linkage Rules](#linkage-rules)
- [Miscellaneous](#miscellaneous)

## Common Terms

|Term             |Description                                         |
|-----------------|----------------------------------------------------|
|assembly         |low level language described by this document       |
|image            |binary file representing a RISCII program           |
|word (length)    |16 bits wide                                        |
|text section     |binary image portion for instructions               |
|data section     |binary image portion for initialized data           |
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

### Tuples

Tuples are aggregate combos of 0+ immediates, strings, labels, or tuples. Tuples are enclosed with curly brackets- using whitespace to delimit items. Items are first resolved for value/sizing before the tuple is resolved (appending `NULL` as needed to be word aligned). Items are place in order of appearance, with earlier items appearing at lower addresses.

Within tuples, immediates are always word-length "any sign" values.

```
{0x34 'beef' MyLabel}          ; tuple of 3 items- 16-bit value "0x0034" placed in first word (12 bytes total)
{}                             ; empty tuple (0 bytes total)
{"nums" {-32768 -1 0 1 65535}} ; nested tuple- "[n][u]" placed in first word (24 bytes total)
{foo bar                       ; INVALID- tuple not closed
```

## Statements

### Instructions

Instruction represent ISA instructions. Instructions are placed in the text section in the order they appear (in a file- arbitrary placement between files). Instructions' grammar are heavily context driven (e.g. immediate sign/sizes based on specific instruction)- see table and examples below.

|Code|Flags |Register|Register|Register|Immediate|Description              |
|----|------|--------|--------|--------|---------|-------------------------|
|AND |      |DST     |SR1     |SR2     |         |Bitwise AND (VAR)        |
|AND |      |DST     |SR1     |        |5bImm    |Bitwise AND (IMM)        |
|ORR |      |DST     |SR1     |SR2     |         |Bitwise ORR (VAR)        |
|ORR |      |DST     |SR1     |        |5bImm    |Bitwise ORR (IMM)        |
|XOR |      |DST     |SR1     |SR2     |         |Bitwise XOR (VAR)        |
|XOR |      |DST     |SR1     |        |5bImm    |Bitwise XOR (IMM)        |
|SHL |      |DST     |SR1     |SR2     |         |Shift Logic Left (VAR)   |
|SHL |      |DST     |SR1     |        |4bIm     |Shift Logic Left (IMM)   |
|SHR |a     |DST     |SR1     |SR2     |         |Shift Right (VAR)        |
|SHR |a     |DST     |SR1     |        |4bIm     |Shift Right (IMM)        |
|ADD |      |DST     |SR1     |SR2     |         |Arithmetic Add (VAR)     |
|ADD |      |DST     |SR1     |        |5bImm    |Arithmetic Add (IMM)     |
|SUB |      |DST     |SR1     |SR2     |         |Arithmetic Subtract (VAR)|
|SUB |      |DST     |SR1     |        |5bImm    |Arithmetic Subtract (IMM)|
|LBI |s     |DST     |        |        |8bImmVal |Load Byte Immediate      |
|LDR |      |DST     |SR1     |        |6bOfst   |Load Memory Word         |
|STR |      |SRC     |SR1     |        |6bOfst   |Store Memory Word        |
|SWP |      |DST     |SR1     |        |6bOfst   |Swap Register Memory     |
|BRC |nzpc\*|        |        |        |8bImmVal |Branch Conditional       |
|JLR |      |DST     |SR1     |        |5bImm    |Jump/Link Register       |
|JPR |      |SR1     |        |        |5bImm    |Jump Register            |
|RTI |      |        |        |        |         |Return From Interrupt    |
|NOP |      |        |        |        |         |No Operation             |
|HLT |      |        |        |        |         |Halt/Pause               |

```
ADD     $1 $4 $5      ; Add registers R4 and R5 and put the result in R1
BRC %nz          1    ; Skip next instruction if prior result (as int16) is negative or zero
LBI     $0       0xFF ; Set R0 to -1
LBI %s  $0       4    ; Set R0 to (R0 << 8) | 0x4
HLT                   ; Enter PSE state- halting instruction execution
```

*\* A no flag `BRC` instruction is treated like an unconditional jump*

### Built-in Functions

Built-in functions act like instructions (grammar, text section placement, etc), though are not directly supported by the ISA. They provide additional functionality to the assembly language.

The `_la` function allows for setting a register to either a word-length "any sign" immediate or label (resolved during assembly/linking). It generates two LBI instructions to set the register.

```
_la    $3 0x8040    ; one load address function...

LBI    $3 0x80      ; ...equivalent two instructions
LBI %s $3 0x40

_la    $4 foo       ; if foo resolves to "0x02A1"...

LBI    $4 0x02      ; ...equivalent two instructions
LBI %s $4 0xA1
```

The `_br` function allows for conditionally jumping to either an unsigned word-length immediate (as an address) or label (resolved during assembly/linking). It generates a 5 instruction "if/else" block- using the register input to temporarily hold the address.

```
_br %n  $2 0x10AA ; jump to fixed address...

BRC %n     1      ; conditional
BRC        3      ; skip 'jump block' on failure
LBI     $2 0x10   ; load fixed address
LBI %s  $2 0xAA
JPR     $2 0      ; jump to fixed address

_br %zp $2 func   ; if 'func' equals 0x0450...

BRC %zp    1      ; conditional
BRC        3      ; skip 'jump block' on failure
LBI     $2 0x04   ; load label address
LBI %s  $2 0x50
JPR     $2 0      ; jump to label
```

### Data Initializations

Data initializations represent initialized data. Initialized data is placed in the data section (in arbitrary order between initializations). An initialization begins with `.data` followed by a word-length "any sign" immediate, string, label, or tuple.

```
.data -5         ; Adds 0xFFFB to data section

.data 0xFFAA     ; Adds 0xFFAA to data section

.data "42"       ; Adds 0x3432 to data section

.data lbl        ; Adds <resolved label address> to data section

.data {-1 2 3 5} ; Adds 0xFFFF000200030005 to data section
```

### BSS Reservations

BSS reservations represent uninitialized data. Uninitialized data is not directly placed in the data section, but influences how the binary image is created (e.g. meta label values). A reservation begins with `.bss` followed by an unsigned word-length immediate. The value indicates the number of bytes to reserve as uninitialized (rounded up as needed for word alignment).

```
.bss 4   ; Reserves 4 bytes of data memory

.bss 0x5 ; Reserves 6 bytes of data memory

.bss -1  ; INVALID- cannot reserve negative amount of memory
```

### Label Declarations

Label declarations create a "named" statement for later reference. The label is tied to the next instruction, built-in function, data initialization, or bss reservation that appears in the file (and is required to be tied to a statement). A declaration consists of a label followed by a `:`.

```
foo:           ; Ties to 'HLT' instruction
HLT

bar1:          ; Ties to '_la' function
bar2:          ; Ties to '_la' function

_la $0 5

dataLabel:     ; Ties to '.data' initialization
.data "string"

.bss 20        ; No labels tied to reservation
```

### Label Modifier

Label modifiers modify how a label's linkage works (or adds additional context). The modifier is tied to the next label declaration that appears in the file (and is required to be tied to a declaration). Modifiers consist of a keyword prefixed with a `.`. See below for valid modifier keywords- and see linkage rules for further information on their effects.

|Keyword|Prerequisites     |Decription                                                          |
|-------|------------------|--------------------------------------------------------------------|
|global |---               |allows label to be reference across files                           |
|weak   |---               |directs in-file references to prefer global declaration if available|
|section|text section label|calls out explicit partitions for optimizing/dead code removal      |
|export |global label      |directs label's global modifier to be preserved in static library   |

## Linkage Rules

### "Scope" Rule

Labels are local by default- they can only be referenced within the file they were declared. A label modified with `.global` can be referenced across all files (including the file the label was declared in).

```
> cat a.s
    .global foo: ; globally declared label
            bar: ; locally declared label
    HLT

> cat b.s
    _la $0 foo   ; references 'foo' in a.s
    _la $0 bar   ; does NOT reference 'bar' in a.s

```

### "Unique" Rule

Label names must be uniquely named. Labels (with the same name) can be declared locally in two different files, but the cannot be declared twice in the same file. Labels modified with `.global` must be uniquely named when compared to other `.global` labels.

```
> cat a.s
            alpha: ; local 'alpha'
    .global beta:  ; local and global 'beta'
    .global gamma: ; local and global 'gamma'
    NOP

> cat b.s
            alpha: ; VALID- local 'alpha' doesn't conflict with a.s local 'alpha'
            beta:  ; VALID- local 'beta' doesn't conflict with a.s local 'beta'
    .global gamma: ; INVALID- global 'gamma' conflicts with a.s global 'gamma'
            alpha: ; INVALID- multiple local 'alpha'
    NOP
```

### "Link" Rule

When resolving label references, local declarations and preferred over gloval declarations. Labels modified with `.weak` direct local references to instead prefer global declarations. References with no matching declaration result in an error.

```
> cat a.s
    .global foo: ; local/global 'foo'
    .global bar: ; local/global 'bar
    NOP

> cat b.s
    .weak foo:   ; local 'foo'- inverted preference
          bar:   ; local 'bar'
    NOP

    _la $0 foo   ; ties to a.s 'foo'
    _la $0 bar   ; ties to b.s 'bar'
    _la $0 cat   ; INVALID- no local/global 'cat'
```

### "Start" Rule

When assembling/linking, one `.global` label named `__START` is expected to be declared and tied to either an instruction or built-in function. This label is used to define which instruction is placed at the start of the text section location (and thus start of the text memory). Failing to declare/locate this label results in an error.

```
_la $0 0x45A1    ; Placed arbitrarily with in program- but not at text address 0x0000
JPR $0           ; Placed just after previous instruction

.global __START: ; (Start of program)
NOP              ; Placed at text address 0x0000
HLT              ; Placed at text address 0x0002
```

### "Meta" Rule

Some labels are reserved for metadata values (auto-generated during assembling/linking). These values are pre-declared and global.

|Label |Description                                          |
|------|-----------------------------------------------------|
|__BSS |First address of uninitialized data (if any)         |
|__FREE|First address of unused/"free" data memory (if any)  |
|__SIZE|Size of the binary image (including headers) in bytes|

## Miscellaneous

### Comments

Comments can be added for human audiences without affecting the output. Comments begin with `;` and take up the rest of the line.

```
; This is a comment
; The presenc/absence of this line does not change the output binary image
```

### Data Memory Layout

The data section (in the binary image) consists only of initialized data, while data memory (in the program- loaded into hardware) includes uninitialized data and free memory. When assembling/linking, the following layout is assumed. This layout primarily affects how `__BSS` and `__FREE` are generated (and how BSS reservations affect both).

**(Start of Data Memory)**

|Area              |Example        |
|------------------|---------------|
|Initialized Data  |.data instances|
|Uninitialized Data|.bss instances | 
|Free Memory       |---            |

**(Rest of Data Memory)**

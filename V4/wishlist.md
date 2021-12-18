## Features

- Static typing
  - Primitive types
    - Int, Float, Bool, Char
  - Composition types
    - Array<...>, List
  - Constants
  - Type aliases
  - Custom/ Structure types

- Functions
  - Export system
  - Descriptive arguments and returns
  - Recursive import
    - Once imported, the function is kept in memory
  - Non-arbitrary number of inputs?

- Operations
  - Comparative
  - Bitwise
  - Mathematical
  - Function Calling

- Simple, assembly-style syntax

- Variables
  - Symbol table which stores variables and their mapping separate
    - Allow aliasing
    - Variables have an id, which matches between assignment and variable name
  - At compile, use constant folding
  - Maintain most recent value of var (whether constant or variable)
  - Global and local scope
    - Entering scope is different from global scope (global is -1 and entering file is 0)
  - Ability to differentiate value and reference variables

- Labels
  - Simplified syntax
  - Precompute arrow jump locations

- Precompute system
  - A system executed at the end of every parsed line to update any values which might not make sense
  - Jumps

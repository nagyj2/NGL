## **NGL 3.0 Bytecode Documentation**
<!-- Last edit Mar 2/21 -->

### _Introduction_

Not-Gonna-Lie (NGL) is a beginner's interpreted programming language designed to emulate the features of assembly languages without requiring complicated software or code set-ups. NGL is strongly typed without automatic type conversions and gives freedom to the programmer to write code however they would like. The goal of NGL is to introduce programmers to a more assembly-like experience without exposing them to all the quirks and difficulties of full-on assembly programming. The language is also intended to be the target language for other compiler projects. With this in mind, the language is intended to offer as many features as possible. This is the 3rd version of the NGL and features a completely reimagined scanner, symbol table and type system.

### _Features_

NGL features components similar to assembly languages, but also incorporates a few higher level features into the language. The biggest differences from a true assembly language is the possibility of arbitrarily long statements and native collection types. NGL does not feature dead code removal, garbage collection or other features of high level languages.

#### _Basics_

NGL source code is written in a text editor and then written to a .ngl file. Since NGL uses an interpreter, the source code does not need to be compiled. The .ngl files are formatted as a series of commands separated by newlines and/or semicolons. NGL source code always executes starting on the first line and then descending downwards. NGL makes use of jumps for control flow.

#### _Structures_

In NGL, data can be stored in multiple ways. Being an assembly language, there are only a handful of native representations of data: 6 primitives and 2 collection types. Using these types together can create larger structures, but NGL is not not specifically designed for this.

In NGL, identifiers can be used to store and use data in a variety of situations. Variables can be declared, assigned, and deleted with corresponding commands. They can also be declared as constants which will disallow any form of modification to their value. All identifiers can only hold one type of data and cannot be reassigned without first deleting the old variable.

##### _Types_

The 6 primitives are integer (`int`), float (`float`), strings (`str`), booleans (`bool`), functions (`func`) and labels (`label`). Integers are any positive or negative whole number whereas floats are any positive or negative decimal. The whole numbers can be represented as integers or floats. Strings are a sequence of characters and are delimited by quotes. Booleans represent a binary value. Functions refer to other NGL source files outside the main executing script. They can be called with optional arguments to run other pieces of code and then optionally return a value. Labels represent positions in the code which can be jumped to using control flow statements. Each of these types cannot be broken down any further, although integers, floats and strings can be indexed to attain certain information about the data, such as digits or characters at a specific point.

The two collection types allow fo other pieces of data to be stored within them. To access data within them, they can be indexed for individual values. Collection types have indexes starting at 0 and increasing. The first collection type is an array (`array`). Arrays have a fixed type, called a subtype, and they can hold an arbitrary amount of values of their subtype. Attempting to add anything other than values of the subtype type will result in an error. The other collection type is a list (`list`), which do not have a subtype and therefore do not have any restrictions on the types that can reside within them.

##### _Literals_

To denote values of the aforementioned types, there must be a way to write a corresponding literal. Integers are the easiest, with an integer being represented by a sequence of numbers optionally started with a minus sign. Floats are similar, but the primary difference is that they can either have a period between two sequences of numbers or an 'f' placed after the last number in a single sequence. Strings are denoted with either single or double quotes around a sequence of characters. Booleans are the simplest, being represented by either 'true' or 'false'. The last two primitive types cannot be declared directly. Function values can only be created through an include statement (refer to _Extensibility_) as they are represented by other files. Labels can only be created though labels written into the source code (refer to _Flow_).

Collection types, being composites of other pieces of data, are more complex, but still follow simple rules. Arrays are denoted by curly braces followed by a primitive data type (subtype), which will be held within the array, and then a colon. There are then two options, first is two integers separated by another colon (range declaration) or a set of values of the array type separated by commas (value declaration). Culminating is another curly brace. The range declaration states that the variable has a certain amount of empty slots within it. The values which reside in these empty slots varies depending on the subtype. The comma declaration will simply create a set of values from the evaluated expressions. Lists are similar in creation except they use square brackets, do not allow for a subtype and can only allow value declaration.

#### _Operations_

NGL is different from other assembly languages in that expressions are constructed like how they would be done in a high level programming language. Registers or a stack are not implemented in NGL, so instead operator precedence is used to determine the order of operations without the use of parentheses. During the execution of an expression, an intermediate representation of the expression is kept internally and after all operations have been executed, that representation is returned. NGL is unique in the way it handles functions since they are handled as a primitive data type. Instead of using parentheses or a specific function, the 'function call' (`@`) operator is used followed by parameter markers (`,`). Below is a table of all operators sorted in decreasing precedence along with their symbol.

| No.  | Operation Name (Descending Precedence)   | Display character(s) |
|------|------------------------------------------|----------------------|
| 12   | Indexing                                 | `[ ]`                |
| 11   | Type Casting                             | `::`                 |
| 10   | Unary Addition/ Subtraction, Logical NOT | `+`, `-`, `!`        |
| 09   | Exponentiation                           | `^`                  |
| 08   | Multiplicative Operations                | `*`, `/`, `\`, `%`   |
| 07   | Additive Operations                      | `+`, `-`             |
| 06   | Inequality                               | `<`, `>`             |
| 05   | Equality                                 | `=`, `<>`, ::=       |
| 04.5 | Intersection                             | `&&`                 |
| 04   | Union                                    | `\|\|`               |
| 03.5 | Logical AND                              | `&`                  |
| 03   | Logical OR                               | `\|`                 |
| 02   | Function call                            | `@` and `,`          |
| 01   | Equation NOT                             | `><`                 |

###### Indexing
Data types can be indexed to collect a portion of data from it. Integers and floats can be indexed to determine the digit at a certain location and strings can be indexed to determine a character. However, indexing is most often used with collection data type. Each position in a collection can hold an entire child data literal. Indexing can only be done for spots that exist within a collection.

###### Type Casting
In NGL, there is an intentional lack of automatic type casting, so the type casting operator is quite valuable. It is used by placing the operator with a value to be casted to the left and the type to be casted to on the right.

###### Unary Addition/ Subtraction and Logical NOT
Unary addition (`+`) and subtraction (`-`) are for use with integers and floats. Unary subtraction can be used to denote a negative value. Logical NOT (`!`) is used to invert the value of a boolean value.

###### Exponentiation
Exponentiation will raise some integer or float to the power of another integer or float.

###### Multiplicative Operators
These operators are mostly used with integer or float values. the multiplication operator (`*`) will multiply two numbers whereas the division operator (`/`) will divide two numbers. The integer division operator (`\`) will divide two numbers but return only the whole integer result. The modulo operator (`%`) will divide two numbers and return the remainder.

###### Additive Operators
Like their unary contemporaries, the additive operator will add two numbers together and the subtractive operator will find the difference between two operators.

###### Inequalities
The inequality operator will compare two values and return a boolean result depending if the left argument is greater or lesser than the right argument. A sequence of inequality operations will combine together into one large comparison. For example, the operation `a < b > c < d` will evaluate as `a < b & b > c & c < d`.

###### Equalities
Equalities will check if the two arguments have the same values. Similar to inequalities, equalities can be string into one large comparison.

###### Intersection
###### Union
###### Logical AND
###### Logical OR
###### Expression NOT

#### _Flow_

#### _Extensibility_

#### _Comments_

### _Statements_

#### _Identifier Operations_

#### _Control Flow_

#### _Input/ Output_

#### _Utility_

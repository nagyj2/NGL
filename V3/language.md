## **NGL 3.0 Bytecode Documentation**
<!-- Last edit Mar 2/21 -->

### _Introduction_

Not-Gonna-Lie (NGL) is a beginner's interpreted programming language designed to emulate the features of assembly languages without requiring complicated software or code set-ups. NGL is strongly typed without automatic type conversions and gives freedom to the programmer to write code however they would like. The goal of NGL is to introduce programmers to a more assembly-like experience without exposing them to all the quirks and difficulties of full-on assembly programming. The language is also intended to be the target language for other compiler projects. With this in mind, the language is intended to offer as many features as possible. This is the 3rd version of the NGL and features a completely reimagined scanner, symbol table and type system.

### _Features_

NGL features components similar to assembly languages, but also incorporates a few higher level features into the language. The biggest differences from a true assembly language is the possibility of arbitrarily long statements and native collection types. NGL does not feature dead code removal, garbage collection or other features of high level languages.

#### _Basics_

NGL source code is written in a text editor and then written to a .ngl file. Since NGL uses an interpreter, the source code does not need to be compiled. The .ngl files are formatted as a series of commands separated by newlines and/or semicolons. NGL source code always executes starting on the first line and then descending downwards. NGL makes use of jumps for control flow. Identifiers are statically typed and there is a deliberate lack of type conversion.

#### _Identifiers_

In NGL, data can be stored in multiple ways. Being an assembly language, there are only a handful of native representations of data: 6 primitives and 2 collection types. Using these types together can create larger structures, but NGL is not not specifically designed for this. Identifiers are passed by value, not reference, so there are no side effects of identifier usage since the identifier is clone on each usage. This choice may only apply to collection types in the future. As a byproduct of this, aliasing is not possible.

Identifiers are used to store pieces of data for use in other expressions. In NGL, variables can be declared, assigned, and deleted with corresponding commands. However, the most important function of an identifier is to be used within expressions for evaluation. Identifiers can also be declared as constants which will disallow any form of modification to their value, but they can still be used in expression. All identifiers can only hold one type of data and cannot be reassigned without first deleting the old identifier.

In NGL, there are a handful of special identifiers which are filled on program start. The first is `__file` which contains a string representation of the current file. The second is the boolean `__main` and contains a boolean value depending on whether or not the current executing instance is the main function being called. The boolean constants `true` and `false` are also technically identifiers which contain the boolean literals. The `argv` identifier is a list which contains all input arguments to the script currently being executed and `retv` is the return values from the currently executing script.

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
| 11   | Indexing                                 | `[ ]`                |
| 10   | Type Casting                             | `::`                 |
| 09   | Unary Addition/ Subtraction, Logical NOT | `+`, `-`, `!`        |
| 08   | Exponentiation                           | `**`                 |
| 07   | Multiplicative Operations                | `*`, `/`, `\`, `%`   |
| 06   | Additive Operations                      | `+`, `-`             |
| 05   | Inequality                               | `<`, `>`             |
| 04   | Equality                                 | `=`, `<>`, `::=`     |
| 03   | Logical AND and intersection             | `&`, `&&`            |
| 02   | Logical OR and union                     | `\|, \|\|`           |
| 01   | Equation NOT                             | `><`                 |

###### Indexing
Data types can be indexed to collect a portion of data from it. Integers and floats can be indexed to determine the digit at a certain location and strings can be indexed to determine a character. However, indexing is most often used with collection data type. Each position in a collection can hold an entire child data literal. Indexing can only be done for spots that exist within a collection.

###### Type Casting
In NGL, there is an intentional lack of automatic type casting, so the type casting operator is quite valuable. It is used by placing the operator with a value to be casted to the left and the type to be casted to on the right.

###### Unary Addition/ Subtraction and Logical NOT
Unary addition (`+`) and subtraction (`-`) are for use with integers and floats. Unary subtraction can be used to denote a negative value. Logical NOT (`!`) is used to invert the value of a boolean value.

###### Exponentiation
Exponentiation will raise some integer or float to the power of another integer or float. This operation will always return a float.

###### Multiplicative Operators
These operators are mostly used with integer or float values. the multiplication operator (`*`) will multiply two numbers whereas the division operator (`/`) will divide two numbers. The integer division operator (`\`) will divide two numbers but return only the whole integer result. The modulo operator (`%`) will divide two numbers and return the remainder.

###### Additive Operators
Like their unary contemporaries, the additive operator will add two numbers together and the subtractive operator will find the difference between two operators. The additive operator can also be used to combine two strings.

###### Inequalities
The inequality operator will compare two values and return a boolean result depending if the left argument is greater or lesser than the right argument. A sequence of inequality operations will combine together into one large comparison. For example, the operation `a < b > c < d` will evaluate as `a < b & b > c & c < d`.

###### Equalities
Equalities will check if the two arguments have the same values. Similar to inequalities, equalities can be string into one large comparison.

###### Logical AND and Intersection
Logical AND takes two boolean arguments and returns true if both arguments are true. Otherwise it returns false. Intersection is used to combining elements of arrays and lists together. The operation compares the two arguments and creates a new data structure of all the elements they share. If the two arguments are array types of the same subtype, the output is an array of that subtype. Otherwise, the output is a list.

###### Logical OR and Union
Logical OR takes two boolean arguments and returns true if either argument is true. Otherwise it returns false. Union is similar to intersection but instead it creates a new data structure of all the elements in either argument. If both inputs are array of the same subtype, the output is the same. Otherwise it is a list.

###### Expression NOT
Expression NOT is the lowest precedence and has the function of negating the result of the entire expression. In if statements, jumps are executed on true, so the intention of the expression NOT is to have an easily identifiable and writable method of modifying if statements so they instead jump on a false value.

#### _Control Flow_

Control flow in NGL is handled by jumps to predefined labels. Certain statements require labels as their arguments and will dictate where the statement will move control to. There are two types of labels in NGL: literals and arrows. Literals, the simpler labels, are identifiers placed at the beginning of a line as have a colon immediately after them. Only one label can be placed on a line. Labels share the namespace of variables and can be referenced in expressions and assigned to other variables.

The other type of labels, arrows, have the form `->`, `=>`, `<-`, `<=` and are handled specially by the interpreter. Arrows do not require a colon, an arbitrary amount can be placed on one line and can even be placed before a literal label. To jump to an arrow, a statement can take an arrow label as an argument and when executed, it will jump to the next instance of the other pointing direction but same arrow shaft. For example, a `->` jump will match with the next `<-`. Arrow jumps can also be performed backwards, with a destination `<=` matching to the previous `=>`. As an argument of a statement, the arrow shaft can be extended with a tilde to skip a number of potential matches which is equal to the number of tildes. These arrows are primarily meant for short hops when a named literal consuming the identifier namespace is not desirable.

#### _Extensibility_

To extend code in NGL, there is a dedicated include command which will read a source code and allow it to be called as a function. This is the primary way to create function literals. There is no limit on the amount of files which can be included into any instance of NGL and it is **planned** that a function called NGL file can call other NGL files. An additional planned feature is declaration of functions within a file and anonymous functions.

<!-- Functions can accept arguments and return values. There are three special identifiers related to functions. The first is the list _argv_ which contains the input arguments which are passed the the function currently being executed. It is available in any NGL file. For an example, the code in the master file `@myFunc #param1 #param2` will evaluate in the function file as `argv = [param1, param2]`. The other two identifiers relate to return values. The first is the _reti_ variable which is filled out by the expression immediately after the `retn` statement in the function file. This is the value which is returned to the master file's function call. The other is the _retv_ list. The _retv_ list is available within any NGL file and silently replaces the _retv_ variable in the master file. -->

#### _Interaction_

To handle input and output with the user, NGL has two dedicated commands. The first takes input from the user. The input command takes command line input from the user and either stores it in an existing variable or creates a new variable. The command is capable of automatically determining the type of the input text or the variable can be cast to take in data as a specific type. The output command simply prints data to the console screen for the user. The last output command is a logging command which outputs text to a specific log file for debugging. Both output command log not do automatic type conversion and therefore expect a string as output.

#### _Comments_

Comments in NGL follow in C style, with single line comments as `//` and multiline comments being delimited by `/*` and `*/`.

### _Statements_

NGL statements consist of two main parts, the keyword and arguments. Below, the statements are broken up into categories based on their function. Each statement will contain all the details about that statement's operation and intended usage.

#### _Identifier Operations_

###### Variable Declaration
`var IDENT TYPE [EXPR]`

Creates a variable of specified type and can optionally assign a default value to it. Variable names are unique and therefore only one instance of a given variable can be used at a time. The namespace is shared with literal labels and functions. Variables are statically types and there is no way to change the type of a variable after creation. Variable names can contain all uppercase letters, lowercase letters and underscores. When executed, the identifier is checked to ensure the name is not already used and then type checking occurs. If a default value is identified, the type of the expression is compared to the declared type and an error is thrown if they are not the same. If an expression is not provided, a default value is given to the identifier depending on the declared type.

###### Constant Declaration
`const IDENT TYPE EXPR`

Constants are similar to variable identifiers except that they cannot have their value modified. They otherwise function like variable identifiers in every other way. Constants must be given an expression value when declared. Collection type constants restrict modification of all contents and prevent additions or removal from the collection.

###### Variable Assignment
`set IDENT EXPR`

If a variable has already been created, any value reassignment must be done using the variable assignment command. Any variable type can be used with the `set` command as long as the expression being assigned must match the identifier. This command first verifies that the variable exists and is not a constant and then type checks the identifier and expression. After these checks clear, the identifier is assigned a new value. The old value of the identifier can be used in the expression.

###### Variable Deletion
`del IDENT {IDENT}`

The variable deletion command unassigns values to the corresponding identifier. If the identifier does not contain a value, an error is thrown. The original type of the identifier does not matter. Once deleted, an identifier can be used for functions, labels or its type and value reassigned. One or more identifiers can be deleted at a time.

#### _Control Flow_

###### Unconditional Jump
`goto LABEL`

The most basic control flow statement is the traditional goto. The single argument is the destination that will be jumped to. The label can either be a arrow or an identifier. If an arrow is used, tildes can be used to skip additional arrows, as described in _Control Flow_.

###### Conditional Jump
`if EXPR LABEL`

The one of two conditional statements, the `if` statement will jump to the argument label only if the expression evaluates to true. The expression must evaluate to a boolean, but there are no restrictions on types prior to final evaluation. All operators can be used in the expression argument.

###### Try/ Catch
`try STMT LABEL`

The second conditional statement is a statement which will only jump on error. A `try` statement will execute another statement and if there is an error, it will jump to the argument label. If there is no error, the statement within the `try` is executed to completion.

###### Execute
`cmp EXPR`

The execute command will compute the result of an expression but not do anything with the result. It can be used with `try` to test for an error without performing any other action on success.

#### _Input/ Output_

###### Log Output
`incl IDENT {IDENT}`

Include statements will import a NGL file and make it runnable as a function. All NGL are capable of being imported because the _argv_ and _retv_ lists are always available.

###### Console Input
`in EXPR_L9`

The input statement takes an identifier as an argument and will store whatever is inputted into the argument identifier. The identifier can use indexing and be cast to ensure the type of the input text. If the variable does not exist, it will be created.

###### Console Output
`out EXPR`

The output statement will display a string to standard output.

#### _Utility_

###### Function Return
`retn`
<!-- `retn EXPR` -->

The return statement will display return control to a caller file. It will stop execution of the current file. If the current file is the master file,

###### Parse Quit
`quit`

The quit statement will stop all execution.

###### Log Output
`log EXPR`

The log statement will write text to a specific log file.
<!-- Write to a file specified as an argument -->

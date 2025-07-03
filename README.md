## Basic Syntax
    
    procedures:
        pro >> define name
        ret >> return value
        ! >> call procedure

    tatic memory:
        mem >> define name
        { >> left brace
        } >> right brace
    
    pointers:
        [ >> left bracket
        ] >> right bracket
    
    unconditional jump:
        jump
    
    conditional jumps:
        jil >> less than
        jile >> less than or equal to
        jie >> equal to
        jin >> not equal to
        jige >> greater than or equal to
        jig >> greater than
    
    assignment:
        = >> set a variable 
    
    unary operators:
        not >> logical not
    
    binary operators:
        or >> logical or
        and >> logical and
        xor >> logical exclusive or
        add >> add integers
        sub >> subtract integers
        mul >> multiply integers
        div >> divide integers
        mod >> modulus of integers

## Code Examples

```
    pro simple_inc x0
        x1 = add x0 1
        ret x1

    pro simple_inc_test x0
        x1 = simple_inc x0
        ret x1

    pro swap_chars x0 x1
        x2 = [x0]
        x3 = [x1]
        [x0] = x3b
        [x1] = x2b
        ret 0

    pro reverse_char_array x0 x1
        @begin
        jige x0 x1 @end
        x2 = [x0]
        x3 = [x1]
        [x0] = x3b
        [x1] = x2b
        x0 = add x0 1
        x1 = sub x1 1
        jump @begin
        @end
        ret 0

    mem internal_ar {1 2 3}

    pro sum_internal_ar x0
        x1 = internal_ar
        x2 = add x1 16
        x3 = 0
        @begin
        jig x1 x2 @end
        x4 = [x1]
        x3 = add x3 x4
        x1 = add x1 8
        jump @begin
        @end
        ret x3
```
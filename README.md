# Algebra Solver

Hobby project, not fit for production use, messy code. No guarantees of correctness.

Does not support divsion for now.

## Usage

Call `parse_and_solve_equation`.

Example: `parse_and_solve_equation("(3x)(2)(9) = 27", "x")`

## "Architecture"

In reverse order:
  - `solve_for_var_name` takes a left-hand side list of terms, and a right-hand side list of terms, and isolates (solves for) the chosen variable.
  - various `TermNode` subclasses can produce the lists of terms with the method `produce_term_list`
  - `parse_expression` returns a tree of `TermNode`s.
  - `parse_and_solve_equation` - calls `parse_expression` and then `solve_for_var_name`
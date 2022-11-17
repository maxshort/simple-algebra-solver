# Algebra Solver

Hobby project, not fit for production use, messy code. No guarantees of correctness.

Parses simple expression, solves some algebra equations. Eventual goal is parse+solve.

Does not support divsion for now.

## Usage

For now, produce a lhs and rhs with `parse_expression`, then pass `lhs.produce_term_list` and `rhs.produce_term_list` to `solve_for_var_name`

## "Architecture"

In reverse order:
  - `solve_for_var_name` takes a left-hand side list of terms, and a right-hand side list of terms, and isolates (solves for) the chosen variable.
  - various `TermNode` subclasses can produce the lists of terms with the method `produce_term_list`
  - `parse_expression` returns a tree of `TermNode`s.
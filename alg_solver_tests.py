from alg_solver import *
import unittest

# TODO: Not well organized, no "strategy" just copied all built-up existing
# manual test notes. Could maybe test only @ equation once equation ready.
# TODO: Property testing?

class TestLowLevelSolving(unittest.TestCase):
    # Var names...
    def test_solve_for_var_name(self):
        actual = solve_for_var_name([Term(1, 'x')], [Term(5)], 'x')
        self.assertEqual(actual[0].coeff, 5.0)

    def test_solve_for_var_name2(self):
        actual = solve_for_var_name([Term(1, 'x'), Term(5)], [Term(7)], 'x')
        self.assertEqual(actual[0].coeff, 2.0)

    def test_solve_for_varname_neg_var(self):
        actual = solve_for_var_name([Term(-1, 'x'), Term(5)], [Term(7)], 'x')
        self.assertEqual(actual[0].coeff, -2.0)

    def test_solve_for_varname_neg_coeff(self):
        actual = solve_for_var_name([Term(1, 'x'), Term(-5)], [Term(7)], 'x')
        self.assertEqual(actual[0].coeff, 12.0)

    def test_solve_for_var_name3(self):
        actual = solve_for_var_name([Term(2, 'x'), Term(5)], [Term(7)], 'x')
        self.assertEqual(actual[0].coeff, 1.0)

    def test_solve_for_var_name_both_sides_eq(self):
        actual = solve_for_var_name([Term(7, 'x'), Term(2)], [Term(5, 'x'), Term(3)], 'x')
        self.assertEqual(actual[0].coeff, 0.5)

    def test_solve_for_var_name_both_sides_eq2(self):
        actual = solve_for_var_name([Term(7, 'x'), Term(2), Term(3)], [Term(5, 'x'), Term(3), Term(3)], 'x')
        self.assertEqual(actual[0].coeff, 0.5)

class TestMultiplication(unittest.TestCase):
    def test_mult_numbers(self):
        actual = Term(3) * Term(4)
        self.assertEqual(actual, Term(12))

    def test_mult_numbers2(self):
        actual = Term(3) * Term(-1)
        self.assertEqual(actual, Term(-3))
    
    def test_multiplication_var(self):
        actual = Term(3, "x") * Term(4)
        self.assertEqual(actual, Term(12, "x"))

    def test_multiplication_multi_var(self):
        actual = Term(3, "x") * Term(4, "y")
        self.assertEqual(actual, Term(12, "xy"))

    def test_errors_on_exponents(self):
        with self.assertRaises(ValueError):
            Term(3, "x") * Term(4, "x")

class TestParseAndSolve(unittest.TestCase):
    def test1(self):
        lhs = parse_expression("34.96885x + 36.96590 * (1 - x)")
        rhs = parse_expression("35.453")
        actual = solve_for_var_name(lhs.produce_term_list(), rhs.produce_term_list(), 'x')
        self.assertEqual(actual[0].coeff, 0.7575674119326001)

    def test2(self):
        lhs = parse_expression("(3x)(2)(9)")
        rhs = parse_expression("27")
        actual = solve_for_var_name(lhs.produce_term_list(), rhs.produce_term_list(), 'x')
        self.assertEqual(actual[0].coeff, 0.5)

    @unittest.skip(
        "Known failure -- probably need to not consume parens 2x in consume_term")
    def test_only_var_in_paren(self):
        lhs = parse_expression("3(x)")
        rhs = parse_expression("6")
        actual = solve_for_var_name(lhs.produce_term_list(), rhs.produce_term_list(), "x")
        self.assertEqual(actual[0].coeff, 2)

unittest.main()

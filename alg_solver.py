import collections
import re

class Term:
    def __init__(self, coeff, var_name=None):
        self.coeff = coeff
        self.var_name = var_name

    def like_term(self, other_term):
        return self.var_name == other.var_name

    def as_negated(self):
        return Term(self.coeff * -1, self.var_name)

    def __mul__(self, other):
        new_coeff = self.coeff * other.coeff
        if self.var_name is None:
            # 2 numbers
            if other.var_name is None:
                new_var_name = None
            else:
                new_var_name = other.var_name
        else:
            if other.var_name is None:
                new_var_name = self.var_name
            else:
                # We currently only want unique variable names -- squaring not supported.
                self_var_num = len(self.var_name)
                other_var_num = len(other.var_name)
                combined_vars = set(self.var_name).union(set(other.var_name))
                if len(combined_vars) < self_var_num + other_var_num:
                    #TODO: Give actual vars attempted.
                    raise ValueError("Attempting to combine same vars via multiplication. Squaring is not supported")
                new_vars = list(combined_vars)
                new_vars.sort()
                new_var_name = "".join(new_vars)
        return Term(new_coeff, new_var_name)

    def __eq__(self, other):
        return (self.coeff == other.coeff) and (self.var_name == other.var_name)

    def __repr__(self):
        #TODO: Replace with better str format
        var_s = self.var_name if self.var_name is not None else ""
        return str(self.coeff) + var_s

# Convenience for shell testing...
def tn(coeff, var_name=None):
    return TermNode(Term(coeff, var_name))

# Leaf term node -- no children.
class TermNode:
    def __init__(self, term):
        
        self.term = term

    def produce_term_list(self):
        return [self.term]

# "Abstract"
class OperationTermNode:
    def __init__(self, left_child, right_child):
        self.left_child = left_child
        self.right_child = right_child

class AddingTermNode(OperationTermNode):
    def produce_term_list(self):
        # TODO: Probably don't actually need defensive copy -- particularly
        # if we consider node stuff to be self-contained. Applies to other node
        # methods.
        left_terms = list(self.left_child.produce_term_list())
        right_terms = list(self.right_child.produce_term_list())
        left_terms.extend(right_terms)
        return left_terms

class SubtractingTermNode(OperationTermNode):
    def produce_term_list(self):
        left_terms = list(self.left_child.produce_term_list())
        right_terms = list(self.right_child.produce_term_list())
        right_terms = map(lambda t: t.as_negated(), right_terms)
        left_terms.extend(right_terms)
        return left_terms

class MultiplyingTermNode(OperationTermNode):
    def produce_term_list(self):
        left_terms = list(self.left_child.produce_term_list())
        right_terms = list(self.right_child.produce_term_list())
        # We're going to have to go pairwise on everything...
        ret = []
        for lt in left_terms:
            for rt in right_terms:
                ret.append(lt * rt)
        return ret

# NOTE: Purposely leaving out division -- adding that may require rewriting/
# rethinking stuff.

# # Roughly:
# 1. Get all "term vars" on one side & everything else on the other...
# 0. Combine like terms on both sides
# ^ Going to have to do that @ some point whether doing @ beginning or end.
# 2. If combined single term on LHS does not have coeff of 1, divide everything on other side by 0.

# TODO: We seem to be drifting towards a model where
#   a subtract sign is just included in the term.
# [terms] -> terms
def combine_like_terms(terms):
    # map of coeff to their summed values...
    combined_coeff = collections.defaultdict(lambda: 0)
    for term in terms:
        combined_coeff[term.var_name] += term.coeff
    return [Term(coeff, name) for name, coeff in combined_coeff.items()]

#TODO: Assuming like terms have been combined on LHS / RHS...
#TODO: Does not work in many cases with > 1 var. For example can't
# separate out 3xy... to get x = ...
#TODO: Modifies stuff passed in etc.
def solve_for_var_name(lhs, rhs, var_name):
    #TODO: Assuming one variable equations, both should have just
    # 1 ribght...?
    # We want 1 term of var_name on the lhs.
    # Convenion:
    # 1. We'll start with these non-transformed
    # 2. Remove them from lhs
    # 3. After transforming, add to rhs.
    terms_to_rhs = []
    # Same convention as above
    terms_to_lhs = []

    for term in lhs:
        if term.var_name != var_name:
            terms_to_rhs.append(term)
    # Not sure if it would be harmful to remove from the collection while
    # iterating so to be safe doing that here.
    for term in terms_to_rhs:
        lhs.remove(term)
        rhs.append(term.as_negated())
    for term in rhs:
        if term.var_name == var_name:
            terms_to_lhs.append(term)
    for term in terms_to_lhs:
        rhs.remove(term)
        lhs.append(term.as_negated())

    lhs = combine_like_terms(lhs)
    rhs = combine_like_terms(rhs)
        
    #TODO: Ignoring div by 0 for now...
    # For 1 var equations, this should always be just 1 term
    for i in range(len(rhs)):
        # Going to divide whether coeff is 1 or not b/c divide by 1 is a no-op.

        rhs[i].coeff /= lhs[0].coeff
        
    return rhs

# Returns lhs, rhs MAYBE ALSO RETURNS "vars" ???
# Only doing actual equations right now...not pure expressions...
def parse_equation(s):
    # Check for 1 equals, after that we defer to parse_expr
    pass

def _break_out_match(m, orig_string):
    return (orig_string[m.start():m.end()],
            # Exclusive end of match, rest of string if any.
            # Fine if this happends to be end of string.
            orig_string[m.span()[1]:])

#TODO: (minor) Docs say this could match "many other digit chars". Do we just want 0-9?
INT_NUM = re.compile(r"\d+")
FLOAT_NUM=re.compile(r"\d+\.\d+")
# Returns (<python_number>, rest_of_raw)
def consume_number(raw):
    # Doing float first to avoid grabbing 'int' of float. (instead of negative lookahead)
    float_match = FLOAT_NUM.match(raw)
    if float_match is not None:
        matched, rest = _break_out_match(float_match, raw)
        return (float(matched), rest)
    
    int_match = INT_NUM.match(raw)
    if int_match is not None:
        matched, rest = _break_out_match(int_match, raw)
        return (int(matched), rest)

    # No floats or ints found, nothing produced.
    return (None, raw)

VARS = re.compile(r"[a-z]+")
# Only handles lowercase
# Returns, (<var_string>, rest_of_raw)
def consume_vars(raw):
    vars_match = VARS.match(raw)
    if vars_match is not None:
        # matched_str, rest
        return _break_out_match(vars_match, raw)
    return (None, raw)

# This will just return a string until it finds the balancing parens or error if no balance found.
# Returns (<balance_paren_str>, rest_of_raw.
def consume_parenthesized(raw):
    if len(raw) == 0 or raw[0] != "(":
        return (None, raw)
    balanced_at = -1
    parens_count = 0
    for idx, val in enumerate(raw):
        if val == "(":
            parens_count += 1
        elif val == ")":
            parens_count -= 1
            if parens_count == 0:
                balanced_at = idx
                break
    if balanced_at == -1:
        raise ValueError("Parens did not balance: " + str(raw))
    return (raw[:balanced_at + 1], raw[balanced_at+1:])

# Expects no whitespace.
# Could consume parenthesized expression by recursively calling parse_expression.
# This handles any parentheses next to each other...e.g. (3)(4)(5) is one term.
# Returns (TermNode, rest_of_raw)
# rest_of_raw should either start with an operator or be an empty string
def consume_term(raw):
    parens_contents, rest = consume_parenthesized(raw)
    if parens_contents is not None:
        node_first_part = parse_expression(parens_contents[1:-1])
        # Check if there's another term -- it will recursively get
        # any terms to the right until it hits end of string or non-term.
        right_term_part, rest_of_s = consume_term(rest)
        return (
            MultiplyingTermNode(node_first_part, right_term_part),
            rest_of_s)
    number_contents, after_number = consume_number(raw)
    if number_contents is None:
        number_contents = 1
    var_contents, after_var = consume_vars(after_number)
    later_parens_node, after_later = consume_parenthesized(after_var)

    initial_term = TermNode(Term(number_contents, var_contents))
    if later_parens_node is None:
        # after_later should be same as after_var
        return (initial_term, after_later)
    else:
        return (
            MultiplyingTermNode(initial_term, later_parens_node),
            after_later)

OPS = ["+", "-", "*", "/"]
def is_valid_operator(maybe_op):
    return OPS.count(maybe_op) > 0

# "Internal" -- call parse_expression instead...
# Returns just actual node -- no tuple
#TODO: rerturns not right...also, see where this is used
def parse_to_node_op_list(s):
    terms_and_operators = []
    # Otherwise, expect operator.
    expect_term = True
    remaining = s
    while len(remaining) > 0:
        if expect_term:
            term_node, remaining = consume_term(remaining)
            if term_node is None:
                raise ValueError("Could not parse: " + str(remaining))
            terms_and_operators.append(term_node)
            expect_term = False
        else:
            if is_valid_operator(remaining[0]):
                terms_and_operators.append(remaining[0])
                expect_term = True
                remaining = remaining[1:]
            else:
                raise ValueError("Expected operator: " + str(remaining))
    if len(remaining) != 0:
        raise ValueError("Couldn't handle: " + remaining)
    return terms_and_operators

# Expects term, (op, term)+
# Returns a similar list but with all mult ops (+operands) replaced with MultiplyingTermNodes
def reduce_all_mult_terms(terms_and_ops):
    try:
        mult_sign_idx = terms_and_ops.index("*")
        # TODO: Assumes there's no trailing signs...(conseqeuence
        # would just be a cryptic error message).
        before_idx = mult_sign_idx - 1
        after_idx = mult_sign_idx + 1
        new_term = MultiplyingTermNode(
            terms_and_ops[before_idx],
            terms_and_ops[after_idx])
        before_new_term = terms_and_ops[:before_idx]
        after_new_term = terms_and_ops[after_idx + 1:]
        new_list = before_new_term
        new_list.append(new_term)
        new_list.extend(after_new_term)
        return reduce_all_mult_terms(new_list)
    # No more mult signs -- we're done.
    except ValueError:
        return terms_and_ops

# Should return a single termnode.
# We'll make it a list for consistency.
def reduce_all_addsub_terms(terms_and_ops):
    if len(terms_and_ops) == 1:
        return terms_and_ops
    term_factory = None
    op = terms_and_ops[1]
    if op == "+":
        term_factory = AddingTermNode
    elif op == "-":
        term_factory = SubtractingTermNode
    else:
        raise ValueError("Could not recognize operator: " + str(op) +"whole list: "+ str(terms_and_ops))
    new_term = term_factory(terms_and_ops[0], terms_and_ops[2])
    new_list = [new_term] + terms_and_ops[3:]
    return reduce_all_addsub_terms(new_list)

#TODO: No equals sign...returns a list of terms...
# Does not tolerate stray plus signs.
def parse_expression(s):
    # Assuming spaces is the only whitespace we get.
    stripped = s.replace(" ", "")

    terms_and_operators = parse_to_node_op_list(stripped)
    terms_and_operators = reduce_all_mult_terms(terms_and_operators)
    terms_and_operators = reduce_all_addsub_terms(terms_and_operators)
    return terms_and_operators[0]

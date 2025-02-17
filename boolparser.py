"""
Grammer:

Expression --> AndTerm { OR AndTerm}+
AndTerm --> Condition { AND Condition}+
Condition --> Terminal (>,<,>=,<=,==) Terminal | (Expression)
Terminal --> Number or String or Variable

Usage:
from boolparser import *
p = BooleanParser('<expression text>')
p.evaluate(variable_dict) # variable_dict is a dictionary providing values for variables that appear in <expression text>
"""


class TokenType:
    NUM, STR, VAR, GT, GTE, LT, LTE, EQ, NEQ, LP, RP, AND, OR, STRWITH = range(14)


class TreeNode:
    tokenType = None
    value = None
    left = None
    right = None

    def __init__(self, tokenType):
        self.tokenType = tokenType


class Tokenizer:
    expression = None
    tokens = None
    tokenTypes = None
    i = 0

    def __init__(self, exp):
        self.expression = exp

    def next(self):
        self.i += 1
        return self.tokens[self.i - 1]

    def peek(self):
        return self.tokens[self.i]

    def hasNext(self):
        return self.i < len(self.tokens)

    def nextTokenType(self):
        return self.tokenTypes[self.i]

    def nextTokenTypeIsOperator(self):
        t = self.tokenTypes[self.i]
        return (
                t == TokenType.GT
                or t == TokenType.GTE
                or t == TokenType.LT
                or t == TokenType.LTE
                or t == TokenType.EQ
                or t == TokenType.NEQ
                or t == TokenType.STRWITH
        )

    def tokenize(self):
        import re

        reg = re.compile(r"(\band\b|\bor\b|!=|==|<=|>=|<|>|\(|\)|\.\*)")
        self.tokens = reg.split(self.expression)
        self.tokens = [t.strip() for t in self.tokens if t.strip() != ""]

        self.tokenTypes = []
        for t in self.tokens:
            if t == "and":
                self.tokenTypes.append(TokenType.AND)
            elif t == "or":
                self.tokenTypes.append(TokenType.OR)
            elif t == "(":
                self.tokenTypes.append(TokenType.LP)
            elif t == ")":
                self.tokenTypes.append(TokenType.RP)
            elif t == "<":
                self.tokenTypes.append(TokenType.LT)
            elif t == "<=":
                self.tokenTypes.append(TokenType.LTE)
            elif t == ">":
                self.tokenTypes.append(TokenType.GT)
            elif t == ">=":
                self.tokenTypes.append(TokenType.GTE)
            elif t == "==":
                self.tokenTypes.append(TokenType.EQ)
            elif t == "!=":
                self.tokenTypes.append(TokenType.NEQ)
            elif t == ".*":
                self.tokenTypes.append(TokenType.STRWITH)
            else:
                # number of string or variable
                if t[0] == t[-1] == '"' or t[0] == t[-1] == "'":
                    self.tokenTypes.append(TokenType.STR)
                else:
                    try:
                        number = float(t)
                        self.tokenTypes.append(TokenType.NUM)
                    except:
                        # Kinda broken
                        if re.search("^[-!a-zA-Z0-9_]+$", t):
                            self.tokenTypes.append(TokenType.VAR)
                        else:
                            self.tokenTypes.append(None)


class BooleanParser:
    tokenizer = None
    root = None

    def __init__(self, exp):
        self.tokenizer = Tokenizer(exp)
        self.tokenizer.tokenize()
        self.parse()

    def parse(self):
        self.root = self.parseExpression()

    def parseExpression(self):
        andTerm1 = self.parseAndTerm()
        while (
                self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.OR
        ):
            self.tokenizer.next()
            andTermX = self.parseAndTerm()
            andTerm = TreeNode(TokenType.OR)
            andTerm.left = andTerm1
            andTerm.right = andTermX
            andTerm1 = andTerm
        return andTerm1

    def parseAndTerm(self):
        condition1 = self.parseCondition()
        while (
                self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.AND
        ):
            self.tokenizer.next()
            conditionX = self.parseCondition()
            condition = TreeNode(TokenType.AND)
            condition.left = condition1
            condition.right = conditionX
            condition1 = condition
        return condition1

    def parseCondition(self):
        if self.tokenizer.hasNext() and self.tokenizer.nextTokenType() == TokenType.LP:
            self.tokenizer.next()
            expression = self.parseExpression()
            if (
                    self.tokenizer.hasNext()
                    and self.tokenizer.nextTokenType() == TokenType.RP
            ):
                self.tokenizer.next()
                return expression
            else:
                raise Exception("Closing ) expected, but got " + self.tokenizer.next())

        terminal1 = self.parseTerminal()
        if self.tokenizer.hasNext():
            if self.tokenizer.nextTokenTypeIsOperator():
                condition = TreeNode(self.tokenizer.nextTokenType())
                self.tokenizer.next()
                terminal2 = self.parseTerminal()
                condition.left = terminal1
                condition.right = terminal2
                return condition
            else:
                return terminal1
                raise Exception("Operator expected, but got " + self.tokenizer.next())
        else:
            return terminal1
            raise Exception("Operator expected, but got nothing")

    def parseTerminal(self):
        if self.tokenizer.hasNext():
            tokenType = self.tokenizer.nextTokenType()
            if tokenType == TokenType.NUM:
                n = TreeNode(tokenType)
                n.value = float(self.tokenizer.next())
                return n
            elif tokenType == TokenType.VAR:
                n = TreeNode(tokenType)
                n.value = self.tokenizer.next()
                return n
            elif tokenType == TokenType.STR:
                n = TreeNode(tokenType)
                n.value = self.tokenizer.next()[1:-1]
                return n
            else:
                raise Exception(
                    "NUM, STR, or VAR expected, but got " + self.tokenizer.next()
                )

        else:
            raise Exception(
                "NUM, STR, or VAR expected, but got " + self.tokenizer.next()
            )

    def evaluate(self, variable_dict):
        return self.evaluateRecursive(self.root, variable_dict)

    def evaluateRecursive(self, treeNode, variable_dict):
        if treeNode.tokenType == TokenType.NUM or treeNode.tokenType == TokenType.STR:
            return treeNode.value
        if treeNode.tokenType == TokenType.VAR:
            variable = treeNode.value
            negate = False
            if variable.startswith("!"):
                negate = True
                variable = variable[1:]
            value = variable_dict.get(variable, False)
            return not value if negate else value

        left = self.evaluateRecursive(treeNode.left, variable_dict)
        right = self.evaluateRecursive(treeNode.right, variable_dict)
        if treeNode.tokenType == TokenType.GT:
            return left > right
        elif treeNode.tokenType == TokenType.GTE:
            return left >= right
        elif treeNode.tokenType == TokenType.LT:
            return left < right
        elif treeNode.tokenType == TokenType.LTE:
            return left <= right
        elif treeNode.tokenType == TokenType.EQ:
            return left == right
        elif treeNode.tokenType == TokenType.NEQ:
            return left != right
        elif treeNode.tokenType == TokenType.AND:
            return left and right
        elif treeNode.tokenType == TokenType.OR:
            return left or right
        elif treeNode.tokenType == TokenType.STRWITH:
            return left.startswith(right)
        else:
            raise Exception("Unexpected type " + str(treeNode.tokenType))


if __name__ == "__main__":
    # Added .startswith operator
    p = BooleanParser('account_number .* "abc"')
    assert p.evaluate({'account_number': 'abc123'}) == True
    assert p.evaluate({'account_number': '1abc123'}) == False

    # Bug fix in matching string + Include both "<double quoted>" and '<single quoted>' string
    double_quoted_p = BooleanParser('account_number == "abc"')
    assert p.evaluate({'account_number': 'abc'}) == True

    single_quoted_p = BooleanParser("account_number == 'abc'")
    assert p.evaluate({'account_number': 'abc'}) == True
    assert p.evaluate({'account_number': "abc"}) == True

from dataclasses import dataclass
from typing import List, Tuple

@dataclass(frozen=True)
class Term:
    """
    A logical term.
    Can be a variable, a contradiction symbol, or an implication operator.
    Can also be a metavariable (only used internally).
    """
    def meta_replace(self, value: int, term: "Term") -> "Term":
        """Replaces a metavariable with another term."""
        if isinstance(self, (Var, Cont)):
            return self
        if isinstance(self, Imply):
            return Imply(
                self.premise.meta_replace(value, term),
                self.conclusion.meta_replace(value, term),
            )
        if isinstance(self, MetaVar):
            if self.value == value:
                return term
            else:
                return self
        #What
        raise ValueError("Impossible")

@dataclass(frozen=True)
class Var(Term):
    """A variable."""
    value: int
    def __str__(self):
        return "v{}".format(self.value)

@dataclass(frozen=True)
class Cont(Term):
    """A contradiction symbol. Infers anything."""
    def __str__(self):
        return "!"

@dataclass(frozen=True)
class Imply(Term):
    """An implication operator. If P -> Q and P is true, Q is true."""
    premise: Term
    conclusion: Term
    def __str__(self):
        return "({}) -> {}".format(str(self.premise), str(self.conclusion))

@dataclass(frozen=True)
class MetaVar(Term):
    """A metavariable. Represents any term."""
    value: int
    def __str__(self):
        return "V{}".format(self.value)

def parse(term: str) -> Term:
    """
    Converts string into term.
    Implication is > (prefix operator).
    Contradiction is !.
    Variables are a, b, c...
    Metavars are A, B, C...
    """
    def chew(term: str) -> Tuple[Term, str]:
        init, els = term[0], term[1:]
        if init == "!":
            return (Cont, els)
        if init.isalpha() and init.islower():
            return (Var(ord(init)), els)
        if init.isalpha() and init.isupper():
            return (MetaVar(ord(init)), els)
        # Implication
        a, els = chew(els)
        b, els = chew(els)
        return (Imply(a, b), els)
    res = chew(term)
    if res[1]:
        raise ValueError("Redundant string: {}".format(res[1]))
    return res[0]
p = parse

axioms = (
    parse(">A>BA"),
    parse(">>A>BC>>AB>AC"),
    parse(">>>ABAA"),
    parse(">!A")
)

@dataclass
class Infer:
    """An inference element. Used in Proof."""

@dataclass
class AxiomI(Infer):
    """Represents an axiom. Three custom terms."""
    index: int
    terms: Tuple[Term, Term, Term]

@dataclass
class ModI(Infer):
    """Represents modus ponens. Takes two values (in index): P -> Q and P."""
    implication: int
    premise: int


@dataclass
class Proof:
    """A proof."""
    goal: Term
    inferences: List[Infer]

    def verify(self) -> bool:
        """Verifies proof if it follows syntax and actually deduces the goal."""
        res = []
        for inf in self.inferences:
            if isinstance(inf, AxiomI):
                ress = axioms[inf.index]
                ress = ress.meta_replace(ord("A"), inf.terms[0])
                ress = ress.meta_replace(ord("B"), inf.terms[1])
                ress = ress.meta_replace(ord("C"), inf.terms[2])
                res.append(ress)
            elif isinstance(inf, ModI):
                if inf.premise >= len(res) or inf.implication >= len(res):
                    return False
                a = res[inf.implication]
                b = res[inf.premise]
                if not isinstance(a, Imply):
                    return False
                if a.premise != b:
                    return False
                res.append(a.conclusion)
            else:
                #What
                raise ValueError("Impossible")
        return self.goal in res

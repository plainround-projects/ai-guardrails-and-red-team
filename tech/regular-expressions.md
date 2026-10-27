# Regular expressions

## What it is

A **regular expression** (regex) is a short text that describes a pattern of characters, such as "two digits, a dash, two digits". A regex engine can test whether a text contains the pattern, find all the places where it occurs, cut out parts of the match, or replace it. Python's engine is the standard-library module `re`; Java's is `java.util.regex`.

## Why this repository uses it

The program reads free text from models and from users and must pick facts out of it: an order id, a refund amount, a label like `A` or `B`, a citation such as `[kb-12]`, an e-mail address to hide, or a phrase such as "ignore previous instructions". Regular expressions do this in one line each, and the same pattern can be written in the Java port.

## Where it appears

| File | What it does with this technology |
| --- | --- |
| `src/guard_redteam/application/assistant.py` | 1 regular expression(s) |
| `src/guard_redteam/application/templates.py` | 1 regular expression(s) |
| `src/guard_redteam/domain/redaction.py` | 4 regular expression(s) |
| `src/guard_redteam/domain/rules.py` | 12 regular expression(s) |
| `java/src/main/java/dev/plainround/guard/application/Assistant.java` | Java port of the patterns (`java.util.regex`). |
| `java/src/main/java/dev/plainround/guard/application/Templates.java` | Java port of the patterns (`java.util.regex`). |
| `java/src/main/java/dev/plainround/guard/domain/Guarding.java` | Java port of the patterns (`java.util.regex`). |
| `src/guard_redteam/application/templates.py` | The `{{name}}` placeholder pattern. |


## How it works underneath

A regex is built from a few pieces.

- **Literal characters** match themselves. `refund` matches the text `refund`.
- **Classes**: `[abc]` any one of a, b or c; `[0-9]` a digit; `[^x]` anything except x. Shortcuts: `\d` digit, `\w` letter/digit/underscore, `\s` whitespace; capital letters mean the opposite. `.` is any character except newline.
- **Quantifiers** say how often the previous piece repeats: `*` zero or more, `+` one or more, `?` zero or one, `{2,4}` two to four. They are *greedy* (take as much as possible); a following `?` makes them *lazy*.
- **Anchors** match positions, not characters: `^` start, `$` end, `\b` the boundary between a word character and a non-word character.
- **Groups**: `( ... )` groups and *captures*; `(?: ... )` groups without capturing; `|` means or.
- **Look-around**: `(?<=x)` and `(?<!x)` look backward, `(?=x)` and `(?!x)` look forward; they test the surroundings without consuming them.
- **Flags**: `(?i)` ignore case, `(?m)` make `^`/`$` work per line.

How the engine works: it tries to match the pattern at the first position of the text, then at the next, until it succeeds or the text ends. At each step it follows the pattern; when a choice (an alternative or a quantifier) fails later, it **backtracks** and tries another choice. A badly written pattern can backtrack an enormous number of times on some inputs, which is why patterns here are short and anchored on word boundaries.

In Python: `re.compile(p)` prepares a pattern once; `.search(text)` finds the first match anywhere; `.fullmatch` must match the whole text; `.findall` returns all matches; `.sub(repl, text)` replaces; `.split` cuts. Use **raw strings** (`r"..."`) so that `\d` is not read as an escape by Python itself.

## Walkthrough of this repository's use

### The placeholder pattern

`src/guard_redteam/application/templates.py`

<!-- fmt: off -->
```python
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")
```
<!-- fmt: on -->

`PLACEHOLDER` finds `{{name}}` in a template: `\{\{` and `\}\}` are the literal braces, `(` ... `)` captures the name, `[a-z_]+` is one or more lowercase letters or underscores. The `r` before the quote makes it a **raw string**: backslashes are kept as they are, which regular expressions need.

### Every pattern in the Python source

Each table reads the pattern from left to right, in the order the engine meets the pieces. A piece with a quantifier is shown with it.

#### `src/guard_redteam/application/assistant.py` line 20

<!-- fmt: off -->
```python
ORDER_ID = re.compile(r"\bPR-\d+\b")
```
<!-- fmt: on -->

The pattern, as text: `\bPR-\d+\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `PR-` | the literal text |
| `\d+` | a digit 0-9, one or more times |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/application/templates.py` line 7

<!-- fmt: off -->
```python
PLACEHOLDER = re.compile(r"\{\{([a-z_]+)\}\}")
```
<!-- fmt: on -->

The pattern, as text: `\{\{([a-z_]+)\}\}`

| Part | Meaning |
| --- | --- |
| `\{` | the character `{` itself |
| `\{` | the character `{` itself |
| `(` | start of a capturing group (its match can be read afterwards) |
| `[a-z_]+` | any one of `a` to `z`, `_`, one or more times |
| `)` | end of the group |
| `\}` | the character `}` itself |
| `\}` | the character `}` itself |

#### `src/guard_redteam/domain/redaction.py` line 13

<!-- fmt: off -->
```python
PLACEHOLDER = re.compile(r"<(?:EMAIL|CARD|PHONE)_\d+>")
```
<!-- fmt: on -->

The pattern, as text: `<(?:EMAIL|CARD|PHONE)_\d+>`

| Part | Meaning |
| --- | --- |
| `<` | the literal text |
| `(?:` | start of a group that is not captured |
| `EMAIL` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `CARD` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `PHONE` | the literal text |
| `)` | end of the group |
| `_` | the literal text |
| `\d+` | a digit 0-9, one or more times |
| `>` | the literal text |

#### `src/guard_redteam/domain/redaction.py` line 9

<!-- fmt: off -->
```python
"EMAIL": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"),
```
<!-- fmt: on -->

The pattern, as text: `[\w.+-]+@[\w-]+\.[\w.]+`

| Part | Meaning |
| --- | --- |
| `[\w.+-]+` | any one of a letter, digit or underscore, `.`, `+`, `-`, one or more times |
| `@` | the literal text |
| `[\w-]+` | any one of a letter, digit or underscore, `-`, one or more times |
| `\.` | the character `.` itself |
| `[\w.]+` | any one of a letter, digit or underscore, `.`, one or more times |

#### `src/guard_redteam/domain/redaction.py` line 10

<!-- fmt: off -->
```python
"CARD": re.compile(r"\b(?:\d[ -]?){13,16}\b"),
```
<!-- fmt: on -->

The pattern, as text: `\b(?:\d[ -]?){13,16}\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `\d` | a digit 0-9 |
| `[ -]?` | any one of a space, `-`, optional (zero or one time) |
| `){13,16}` | end of the group; the whole group is repeated: 13 to 16 times |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/redaction.py` line 11

<!-- fmt: off -->
```python
"PHONE": re.compile(r"\+?\d[\d ()-]{8,}\d"),
```
<!-- fmt: on -->

The pattern, as text: `\+?\d[\d ()-]{8,}\d`

| Part | Meaning |
| --- | --- |
| `\+?` | the character `+` itself, optional (zero or one time) |
| `\d` | a digit 0-9 |
| `[\d ()-]{8,}` | any one of a digit 0-9, a space, `(`, `)`, `-`, 8 or more times |
| `\d` | a digit 0-9 |

#### `src/guard_redteam/domain/rules.py` line 57

<!-- fmt: off -->
```python
SOFT_SIGNALS = re.compile(
```
<!-- fmt: on -->

The pattern, as text: `\b(?:ignore|disregard|forget|system|internal|instructions?|token|secret|prompt|override|pretend|role-?play|developer|admin|rules|verbatim|repeat|act as)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `ignore` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `disregard` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `forget` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `system` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `internal` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `instruction` | the literal text |
| `s?` | the character `s`, optional (zero or one time) |
| `\|` | or: either what is on the left or what is on the right |
| `token` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `secret` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `prompt` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `override` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `pretend` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `role` | the literal text |
| `-?` | the character `-`, optional (zero or one time) |
| `play` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `developer` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `admin` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `rules` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `verbatim` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `repeat` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `act as` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 11

<!-- fmt: off -->
```python
re.compile(r"\b(?:ignore|disregard|forget)\b[^.\n]{0,40}\b(?:instructions|rules)\b", re.I),
```
<!-- fmt: on -->

The pattern, as text: `\b(?:ignore|disregard|forget)\b[^.\n]{0,40}\b(?:instructions|rules)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `ignore` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `disregard` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `forget` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |
| `[^.\n]{0,40}` | any one character except `.`, a newline, 0 to 40 times |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `instructions` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `rules` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 13

<!-- fmt: off -->
```python
("forget_everything", re.compile(r"\bforget everything\b", re.I)),
```
<!-- fmt: on -->

The pattern, as text: `\bforget everything\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `forget everything` | the literal text |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 14

<!-- fmt: off -->
```python
("stop_following", re.compile(r"\bstop following (?:your|the) (?:instructions|rules)\b", re.I)),
```
<!-- fmt: on -->

The pattern, as text: `\bstop following (?:your|the) (?:instructions|rules)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `stop following ` | the literal text |
| `(?:` | start of a group that is not captured |
| `your` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `the` | the literal text |
| `)` | end of the group |
| ` ` | the literal text |
| `(?:` | start of a group that is not captured |
| `instructions` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `rules` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 18

<!-- fmt: off -->
```python
re.compile(r"\b(?:SYSTEM|ADMIN)\s+(?:OVERRIDE|NOTICE)\b|\[(?:system|admin)\]"),
```
<!-- fmt: on -->

The pattern, as text: `\b(?:SYSTEM|ADMIN)\s+(?:OVERRIDE|NOTICE)\b|\[(?:system|admin)\]`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `SYSTEM` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `ADMIN` | the literal text |
| `)` | end of the group |
| `\s+` | whitespace (space, tab, newline), one or more times |
| `(?:` | start of a group that is not captured |
| `OVERRIDE` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `NOTICE` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |
| `\|` | or: either what is on the left or what is on the right |
| `\[` | the character `[` itself |
| `(?:` | start of a group that is not captured |
| `system` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `admin` | the literal text |
| `)` | end of the group |
| `\]` | the character `]` itself |

#### `src/guard_redteam/domain/rules.py` line 22

<!-- fmt: off -->
```python
re.compile(r"\bnew (?:instructions?|policy)\b[^.\n]{0,60}\b(?:assistant|ignore|reveal|token)\b", re.I),
```
<!-- fmt: on -->

The pattern, as text: `\bnew (?:instructions?|policy)\b[^.\n]{0,60}\b(?:assistant|ignore|reveal|token)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `new ` | the literal text |
| `(?:` | start of a group that is not captured |
| `instruction` | the literal text |
| `s?` | the character `s`, optional (zero or one time) |
| `\|` | or: either what is on the left or what is on the right |
| `policy` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |
| `[^.\n]{0,60}` | any one character except `.`, a newline, 0 to 60 times |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `assistant` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `ignore` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `reveal` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `token` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 26

<!-- fmt: off -->
```python
re.compile(
```
<!-- fmt: on -->

The pattern, as text: `\b(?:reveal|print|output|show|read me|echo)\b[^.\n]{0,50}\b(?:reference token|internal token|the token|secret|system prompt|configuration)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `reveal` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `print` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `output` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `show` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `read me` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `echo` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |
| `[^.\n]{0,50}` | any one character except `.`, a newline, 0 to 50 times |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `reference token` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `internal token` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `the token` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `secret` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `system prompt` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `configuration` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 34

<!-- fmt: off -->
```python
re.compile(r"\b(?:system prompt|initial instructions|everything above|your instructions|verbatim)\b", re.I),
```
<!-- fmt: on -->

The pattern, as text: `\b(?:system prompt|initial instructions|everything above|your instructions|verbatim)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `system prompt` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `initial instructions` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `everything above` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `your instructions` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `verbatim` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 38

<!-- fmt: off -->
```python
re.compile(
```
<!-- fmt: on -->

The pattern, as text: `\b(?:you are now|dan\b|debugbot|developer mode|maintenance mode|unfiltered|no rules|compromised bot)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `you are now` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `dan` | the literal text |
| `\b` | a backspace (only inside a class) |
| `\|` | or: either what is on the left or what is on the right |
| `debugbot` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `developer mode` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `maintenance mode` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `unfiltered` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `no rules` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `compromised bot` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 45

<!-- fmt: off -->
```python
re.compile(
```
<!-- fmt: on -->

The pattern, as text: `\b(?:pretend you are|roleplay as|let's play a game|simulate a terminal|imagine your rules)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `pretend you are` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `roleplay as` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `let's play a game` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `simulate a terminal` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `imagine your rules` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 51

<!-- fmt: off -->
```python
re.compile(r"\b(?:note to assistant|dear assistant|attention ai|hidden instruction|end of data)\b", re.I),
```
<!-- fmt: on -->

The pattern, as text: `\b(?:note to assistant|dear assistant|attention ai|hidden instruction|end of data)\b`

| Part | Meaning |
| --- | --- |
| `\b` | a backspace (only inside a class) |
| `(?:` | start of a group that is not captured |
| `note to assistant` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `dear assistant` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `attention ai` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `hidden instruction` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `end of data` | the literal text |
| `)` | end of the group |
| `\b` | a backspace (only inside a class) |

#### `src/guard_redteam/domain/rules.py` line 53

<!-- fmt: off -->
```python
("assistant_command", re.compile(r"</?instructions>|\bassistant:\s", re.I)),
```
<!-- fmt: on -->

The pattern, as text: `</?instructions>|\bassistant:\s`

| Part | Meaning |
| --- | --- |
| `<` | the literal text |
| `/?` | the character `/`, optional (zero or one time) |
| `instructions>` | the literal text |
| `\|` | or: either what is on the left or what is on the right |
| `\b` | a backspace (only inside a class) |
| `assistant:` | the literal text |
| `\s` | whitespace (space, tab, newline) |

### Java

These Java files use `Pattern` or `String.matches`/`replaceAll`. The syntax is the same for everything above, except that a backslash must be doubled inside a Java string (`"\\d"` is the pattern `\d`), and flags can be written as `Pattern.CASE_INSENSITIVE`.

- `java/src/main/java/dev/plainround/guard/application/Assistant.java`
- `java/src/main/java/dev/plainround/guard/application/Templates.java`
- `java/src/main/java/dev/plainround/guard/domain/Guarding.java`

## Try it yourself

1. `python3 -c "import re; print(re.findall(r'\bPR-\d{6}\b', 'orders PR-123456 and PR-99'))"` prints `['PR-123456']`: the second does not have six digits.
2. `python3 -c "import re; print(re.sub(r'\s+', ' ', 'a   b \n c'))"` prints `a b c`.
3. `python3 -c "import re; m = re.search(r'(\d+)-(\d+)', 'pages 10-20'); print(m.group(0), m.group(1), m.group(2))"` prints `10-20 10 20`.
4. `python3 -c "import re; print(re.findall(r'a.*b', 'a1b2b'), re.findall(r'a.*?b', 'a1b2b'))"` prints `['a1b2b'] ['a1b']`: greedy against lazy.
5. Open https://regex101.com in a browser, choose the Python flavor and paste one of the patterns above; it draws the same explanation.

## Mistakes people make

- **Forgetting the raw-string prefix** so `\b` becomes a backspace character.
- **Unescaped dots**: `PR-12.34` also matches `PR-12x34`. Use `\.`.
- **Greedy matching across too much text** (`.*`); use a class that excludes the end character, or a lazy quantifier.
- **No anchors**: `\d{6}` also matches inside a longer number; `\b` stops that.
- **Parsing nested structure** (HTML, JSON) with a regex. Use a parser.
- **Trusting a regex as security**: the guardrail rules are a first filter, which the red-team suite measures; they are not a guarantee.

## Check yourself

1. **What does `\b` match?**  
   A boundary between a word character and a non-word character; it consumes no text.
2. **What is the difference between `(...)` and `(?:...)`?**  
   The first captures its match for later reading; the second only groups.
3. **What does a trailing `?` after `*` change?**  
   It makes the repetition lazy: as few characters as possible.
4. **Why use raw strings for patterns in Python?**  
   So backslashes reach the regex engine unchanged.
5. **What does `re.search` return when nothing matches?**  
   `None`.

## Further reading

Python `re` module and the regex HOWTO: https://docs.python.org/3/library/re.html , https://docs.python.org/3/howto/regex.html . Java `java.util.regex.Pattern`: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/java/util/regex/Pattern.html

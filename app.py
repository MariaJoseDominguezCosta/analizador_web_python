import re
from flask import Flask, render_template, request
from fuzzywuzzy import fuzz

app = Flask(__name__)

reserved_words = {
    "for",
    "do",
    "while",
    "if",
    "int",
    "else",
    "printf",
    "end",
    "read",
    "programa",
}
symbols = {";", '"', "+", "=", ",", "(", ")", "{", "}"}
identifiers = {"a", "b", "c", "la", "suma", "es"}


def analyze_code(code):
    lines = code.split("\n")
    tokens = []
    errors = []

    for i, line in enumerate(lines, start=1):
        words = re.findall(r'\b\w+\b|[\(\){};"+=,]', line)
        for word in words:
            if word in reserved_words:
                reserved = "x"
            else:
                reserved = ""
            if (
                word not in reserved_words
                and word not in symbols
                and not word.isdigit()
                and word not in identifiers
            ):
                max_ratio = 0
                suggested_word = ""
                for rword in reserved_words:
                    ratio = fuzz.ratio(word.lower(), rword.lower())
                    if ratio > max_ratio:
                        max_ratio = ratio
                        suggested_word = rword
                errors.append(
                    {"token": word, "line": i, "suggested_word": suggested_word}
                )
            token = {
                "token": word,
                "line": i,
                "reserved": reserved,
                "symbol": "x" if word in symbols else "",
                "comma": "x" if word == "," else "",
                "semicolon": "x" if word == ";" else "",
                "left_paren": "x" if word == "(" else "",
                "right_paren": "x" if word == ")" else "",
                "left_brace": "x" if word == "{" else "",
                "right_brace": "x" if word == "}" else "",
                "number": "x" if word.isdigit() else "",
                "identifier": "x" if word in identifiers else "",
            }
            tokens.append(token)

    total_counts = {
        key: sum(1 for token in tokens if token[key] == "x")
        for key in tokens[0].keys()
        if key != "token"
    }
    tokens.append(total_counts)

    return tokens, errors


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        code = request.form['code']
        tokens, errors = analyze_code(code)
        return render_template('index.html', tokens=tokens, code=code, errors=errors)
    return render_template('index.html', tokens=[], code='', errors=[])


if __name__ == "__main__":
    app.run(debug=True)

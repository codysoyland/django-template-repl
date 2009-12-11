import os
import sys
import atexit
import readline
import traceback
from copy import deepcopy
from django.template import Parser, Lexer, Context, TemplateSyntaxError

def run_shell(context=Context()):
    goodbye = lambda: sys.stderr.write('\nkthxbai!\n')
    while True:
        try:
            for node in input_node_generator():
                sys.stdout.write(node.render(context))
            print
        except KeyboardInterrupt:
            goodbye()
            break
        except EOFError:
            goodbye()
            break
        except Exception, e:
            traceback.print_exc()

def input_node_generator(prompt='>>> ', leading_tokens=None, input_source=raw_input):
    input = False
    while not input:
        input = input_source(prompt)
    input = input + '\n'
    tokens = Lexer(input, None).tokenize()
    if leading_tokens:
        tokens = leading_tokens + tokens
    initial_tokens = deepcopy(tokens)
    try:
        for node in Parser(tokens).parse():
            yield node
    except TemplateSyntaxError, e:
        if e.args[0].startswith('Unclosed tags'):
            for node in input_node_generator('... ', initial_tokens):
                yield node
        else:
            raise

def setup_readline_history():
    history_path = os.path.join(os.getenv('HOME'), '.django-template-repl-history')

    # load history file
    if os.path.exists(history_path):
        readline.read_history_file(history_path)

    # register callback to write history file when exiting
    atexit.register(lambda: readline.write_history_file(history_path))

if __name__ == "__main__":
    main()

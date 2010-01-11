import os
import sys
import atexit
import readline
import code
from django.template import Parser, Lexer, Context, TemplateSyntaxError
from template_repl import get_version

class TemplateREPL(code.InteractiveConsole):
    def __init__(self, parser=None, context=None, output=None):
        self.context = context or Context()
        self.parser = parser or Parser([])
        self.output = output or sys.stdout
        code.InteractiveConsole.__init__(self)

    def runsource(self, source, filename="<input>", symbol="single"):
        if not source:
            return False
        tokens = Lexer(source, None).tokenize()
        self.parser.tokens = tokens
        nodes = []
        try:
            try:
                for node in self.parser.parse():
                    nodes.append(node)
            except TemplateSyntaxError, e:
                if e.args[0].startswith('Unclosed tags'):
                    # inside block, so ask for more input
                    return True
                else:
                    raise
        except:
            self.showtraceback()
            return False
        else:
            for node in nodes:
                self.output.write('%s' % (node.render(self.context),))
            self.output.write('\n')
            return False

def run_shell(context=Context()):
    setup_readline_history()
    console = TemplateREPL(context=context)
    console.interact('django-template-repl %s' % get_version())
    sys.stderr.write('\nkthxbai!\n')

def setup_readline_history():
    history_path = os.path.join(os.getenv('HOME'), '.django-template-repl-history')

    # load history file
    if os.path.exists(history_path):
        readline.read_history_file(history_path)

    # register callback to write history file when exiting
    atexit.register(lambda: readline.write_history_file(history_path))

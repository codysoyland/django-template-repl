import re
import os
import sys
import atexit
import readline
import code
from django.template import Parser, Lexer, Context, TemplateSyntaxError, TOKEN_TEXT
from template_repl import get_version

class ExitREPL(Exception):
    pass

class TemplateREPL(code.InteractiveConsole, object):
    def __init__(self, parser=None, context=None, output=None):
        self.context = context or Context()
        self.parser = parser or Parser([])
        self.output = output or sys.stdout
        self.completion_matches = []

        code.InteractiveConsole.__init__(self)

    def _get_completion_ppp(self, text):
        """
        Return tuple containing
            - `prefix`
            - `pivot`
            - `partial`
        Eg:
            If text is '{{ var }}{% get_', the output is:
            ('{{ var }}{', '%', ' get_')

        How it works:
        1. Tokenize text, add first n-1 tokens to "prefix".
        2. Split on final "|%{:". Call it "pivot".
        3. Any text after pivot is called the "partial".
            -"Partial" means any completion must start with it.
        4. Text prior to the pivot but after the first n-1 tokens
           is appended to the prefix.

        Completion handlers are chosen based on pivot character:
            | - filter
            % - tag
            { - variable
            : - variable
        """
        if len(text) == 0:
            return ('', '', '')

        prefix = ''
        partial = ''
        pivot = ''

        tokens = Lexer(text, None).tokenize()

        if tokens[-1].token_type != TOKEN_TEXT:
            return (text, '', '')

        prefix_tokens = tokens[:-1]
        working_area = tokens[-1].contents

        prefix = text[:-len(working_area)]

        # Iterate backwards through string, finding the first
        # occurrence of any of the chars "|%{:". Call it the pivot.
        for index, char in list(enumerate(working_area))[::-1]:
            if char == ' ':
                if ' ' in working_area[:index]:
                    pivot = char
                    break
            if char in '|%{:':
                pivot = char
                break

        # No pivot was found
        if len(pivot) == 0:
            return (text, '', '')

        pieces = working_area.split(pivot)

        prefix += pivot.join(pieces[:-1])
        partial = pieces[-1]

        return (prefix, pivot, partial)

    def get_completion_matches(self, text):
        """
        Return list of completion matches given the input `text`.
        """
        vars = self.context.dicts[0].keys()
        filters = self.parser.filters.keys()
        tags = self.parser.tags.keys()
        tags.extend(['endif', 'endifequal', 'endfor', 'endwhile', 'endfilter', 'endcomment'])

        (prefix, pivot, partial) = self._get_completion_ppp(text)

        if pivot == '{':
            possibilities = [' %s' % var for var in vars]
        elif pivot in ' :':
            possibilities = ['%s' % var for var in vars]
        elif pivot == '%':
            possibilities = [' %s' % tag for tag in tags]
        elif pivot == '|':
            possibilities = ['%s' % filt for filt in filters]

        # Filter out possibilites that do not start with the text in the partial
        possibilities = filter(
            lambda poss: poss.startswith(partial),
            possibilities)

        return [(prefix + pivot + poss) for poss in possibilities]

    def complete(self, text, state):
        if not self.completion_matches and state == 0:
            self.completion_matches = self.get_completion_matches(text)
        try:
            return self.completion_matches.pop()
        except IndexError:
            return None

    def interact(self, banner=None):
        try:
            code.InteractiveConsole.interact(self, banner)
        except ExitREPL:
            pass

    def runsource(self, source, filename="<input>", symbol="single"):
        if source == 'exit':
            raise ExitREPL()
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

    def raw_input(self, prompt):
        orig_delims = readline.get_completer_delims()
        orig_completer = readline.get_completer()

        readline.set_completer(self.complete)
        readline.set_completer_delims('')

        output = super(TemplateREPL, self).raw_input(prompt)

        readline.set_completer(orig_completer)
        readline.set_completer_delims(orig_delims)

        return output

def run_shell(context=Context()):
    setup_readline_history()
    console = TemplateREPL(context=context)
    console.interact('\033[92mdjango-template-repl %s\033[0m' % get_version())
    sys.stderr.write('\nkthxbai!\n')

def setup_readline_history():
    history_path = os.path.expanduser('~/.django-template-repl-history')

    # load history file
    if os.path.exists(history_path):
        readline.read_history_file(history_path)

    # register callback to write history file when exiting
    atexit.register(lambda: readline.write_history_file(history_path))

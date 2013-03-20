import re
import sys
import code
import readline
from django.template import Parser, Lexer, Context, TemplateSyntaxError
from template_repl import get_version
from template_repl.completion import Completer

class TemplateREPL(code.InteractiveConsole, object):
    def __init__(self, parser=None, context=None, output=None):
        """
        The template REPL object has a single parser and context instance
        that persist for the length of the shell session.
        """
        super(TemplateREPL, self).__init__()

        self.context = context or Context()
        self.parser = parser or Parser([])
        self.output = output or sys.stdout
        self.completer = Completer(context = self.context, parser = self.parser)

    def interact(self, banner=None):
        try:
            super(TemplateREPL, self).interact(banner)
        except ExitREPL:
            # Fail silently. This exception is just meant to break
            # out of the interact() call.
            pass

    def runsource(self, source, filename="<input>", symbol="single"):
        """
        readline calls this method with the current source buffer. This method
        can return True to instruct readline to capture another line of input
        using the "..." prompt or return False to tell readline to clear the
        source buffer and capture a new phrase.

        How it works:
        1. Tokenize input.
        2. Load parser with tokens.
        3. Attempt to parse, loading a list with nodes.
        4. If unclosed tag exception is raised, get more user input.
        5. If everything went smoothly, print output, otherwise print exception.
        """
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
            except TemplateSyntaxError as e:
                if e.args[0].startswith('Unclosed tags'):
                    # inside block, so ask for more input
                    return True
                else:
                    raise
            for node in nodes:
                self.output.write('%s' % (node.render(self.context),))
            self.output.write('\n')
            return False
        except:
            self.showtraceback()
            return False

    def raw_input(self, prompt):
        """
        I'm overloading raw_input here so that I can swap out the completer
        before and after each line of input. This is because the completer
        is global. There might be a better way of doing this.

        TODO: I think I need to do a similar hack to fix readline history,
        as history currently gets munged between PDB and template-repl.
        """
        orig_delims = readline.get_completer_delims()
        orig_completer = readline.get_completer()

        readline.set_completer(self.completer.complete)
        readline.set_completer_delims('')

        output = super(TemplateREPL, self).raw_input(prompt)

        readline.set_completer(orig_completer)
        readline.set_completer_delims(orig_delims)

        return output

class ExitREPL(Exception):
    pass

__version__ = '0.3.0'

def get_version():
    return __version__

import os
import sys
import readline
from django.template import Context

def run_shell(context=Context(), history_file=os.path.expanduser('~/.django-template-repl-history')):
    from template_repl.repl import TemplateREPL

    if os.path.exists(history_file):
        readline.read_history_file(history_file)
    console = TemplateREPL(context=context)
    console.interact('\033[92mdjango-template-repl %s\033[0m' % get_version())
    sys.stderr.write('\nkthxbai!\n')
    readline.write_history_file(history_file)

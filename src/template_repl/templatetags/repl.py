from template_repl import run_shell
from django.template import Node, Library
from template_repl.utils import pdb_with_context
from django.template import TemplateSyntaxError

register = Library()

class REPLNode(Node):
    def __init__(self, use_pdb, *args, **kwargs):
        self.use_pdb = use_pdb
        return super(REPLNode, self).__init__(*args, **kwargs)
    def render(self, context):
        if self.use_pdb:
            pdb_with_context(context)
        else:
            run_shell(context)
        return ''

@register.tag
def repl(parser, token):
    use_pdb = False
    bits = token.contents.split()
    if len(bits) > 1:
        if bits[1] == 'pdb':
            use_pdb = True
        else:
            raise TemplateSyntaxError('The second argument to the "repl" tag, if present, must be "pdb".')
    return REPLNode(use_pdb)

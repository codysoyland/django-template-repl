from template_repl.repl import setup_readline_history, run_shell
from django.template import Node, Library

register = Library()

class REPLNode(Node):
    def render(self, context):
        setup_readline_history()
        run_shell(context)
        return ''

@register.tag
def repl(parser, token):
    return REPLNode()

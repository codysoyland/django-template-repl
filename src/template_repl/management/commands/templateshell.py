from django.core.management.base import BaseCommand
from django.test.utils import setup_test_environment
from django.test.client import Client
from django.template.context import Context
from optparse import make_option
from template_repl import run_shell
from template_repl.utils import pdb_with_context

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('-u', '--url', dest='url', help='Preload context from given URL (just the path, such as "/admin/").', default=None),
        make_option('-c', '--context', dest='context', help='Supply context as dictionary. Note: This gets evaled.', default=None),
        make_option('--pdb', dest='use_pdb', action='store_true', help='Use the template context provided by -u or -c in a pdb shell instead of a template shell.', default=False),
    )
    help = 'Shell to interact with the template language. Context can be loaded by passing a URL with -u.'

    def handle(self, url, context, use_pdb, *args, **kwargs):
        if context:
            context_dict = eval(context)
        else:
            context_dict = {}
        context = Context(context_dict)
        if url is not None:
            setup_test_environment()
            client = Client()
            response = client.get(url)
            if not response.context:
                print 'Response for given URL contains no context (code %s).' % response.status_code
            else:
                if isinstance(response.context, Context):
                    context = response.context
                elif type(response.context) == list:
                    context = response.context[0]
                else:
                    try:
                        from django.test.utils import ContextList
                    except ImportError:
                        pass
                    else:
                        if isinstance(response.context, ContextList):
                            # TODO: probably should try to merge all contexts
                            context = response.context[0]
        if use_pdb:
            pdb_with_context(context)
        else:
            run_shell(context)

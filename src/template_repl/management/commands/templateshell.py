from django.core.management.base import BaseCommand
from template_repl.repl import setup_readline_history, run_shell
from optparse import make_option
from django.test.client import Client
from django.test.utils import ContextList
from django.template.context import Context

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option("-u", "--url", dest="url", help='Preloads context from a given URL.', default=None),
    )
    help = 'Shell to interact with the template language. Context can be loaded by passing a URL with -u.'

    def handle(self, url, *args, **kwargs):
        context = Context()
        if url is not None:
            from django.test.utils import setup_test_environment
            setup_test_environment()
            client = Client()
            response = client.get(url)
            if not response.context:
                print 'Response for given URL contains no context (code %s).' % response.status_code
            else:
                if isinstance(response.context, Context):
                    context = response.context
                elif isinstance(response.context, ContextList):
                    # TODO: probably should try to merge all contexts
                    context = response.context[0]
        setup_readline_history()
        run_shell(context)

from django.core.management.base import BaseCommand
from template_repl.repl import setup_readline_history, run_shell

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        setup_readline_history()
        run_shell()

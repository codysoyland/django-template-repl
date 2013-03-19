import os, sys
from django.conf import settings

DIRNAME = os.path.dirname(__file__)
sys.path.append(os.path.join(DIRNAME, 'src'))
settings.configure(
    DEBUG=True,
    DATABASES={
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
        }
    },
    ROOT_URLCONF='template_repl.urls',
    INSTALLED_APPS=(
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'template_repl',
    )
)

from django.test.simple import DjangoTestSuiteRunner
test_runner = DjangoTestSuiteRunner(verbosity=1)
failures = test_runner.run_tests(['template_repl', ])
if failures:
    sys.exit(failures)

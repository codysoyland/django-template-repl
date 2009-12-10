import os
from distutils.core import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='django-template-repl',
    version='0.1',
    description="A readline shell for the Django template language.",
    long_description=read('README'),
    author='Cody Soyland',
    author_email='codysoyland@gmail.com',
    license='BSD',
    url='http://github.com/codysoyland/django-template-repl/',
    package_dir = {'': 'src'},
    packages=[
        'template_repl',
        'template_repl.templatetags',
        'template_repl.management',
        'template_repl.management.commands',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
    zip_safe=False,
)

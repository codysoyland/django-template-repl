import unittest
from template_repl.repl import TemplateREPL
from django.template import Context
from StringIO import StringIO

# Very basic tests here. Need more!!!

def mock_interaction(commands, context={}):
    context = Context(context)
    output = ''
    output_buffer = StringIO()
    console = TemplateREPL(output=output_buffer, context=context)
    for command in commands:
        console.push(command)
    output_buffer.seek(0)
    output = output_buffer.read()
    return output

class TestREPL(unittest.TestCase):
    def test_simple(self):
        output = mock_interaction(['textnode'])
        self.assertEqual(output, 'textnode\n')
    def test_var(self):
        output = mock_interaction(['{{ a }}'], {'a': 'testvar'})
        self.assertEqual(output, 'testvar\n')
    def test_loop(self):
        output = mock_interaction(
            ['{% for thing in things %}', '{{ thing }}', '{% endfor %}'],
            {'things': ['one', 'two', 'three']}
        )
        self.assertEqual(output, '\none\n\ntwo\n\nthree\n\n')

if __name__ == '__main__':
    unittest.main()

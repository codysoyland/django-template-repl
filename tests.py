import unittest
from template_repl.repl import input_node_generator
from django.template import Context

# Very basic tests here. Need more!!!

def mock_interaction_parser(commands):
    def mock_raw_input(prompt):
        try:
            return commands.pop(0)
        except IndexError:
            raise Exception('raw_input called more than expected')
    return input_node_generator(input_source=mock_raw_input)

def mock_interaction(commands, context={}):
    context = Context(context)
    output = ''
    for node in mock_interaction_parser(commands):
        output += node.render(context)
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

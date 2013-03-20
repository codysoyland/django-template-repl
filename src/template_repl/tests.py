from template_repl.repl import TemplateREPL
from django.template import Context
from django.test import TestCase
from io import StringIO

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

class TestREPL(TestCase):
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

class TestCompletion(TestCase):
    def setUp(self):
        self.repl = TemplateREPL(
            context = Context({
                'food': ['tacos', 'ice cream', 'sushi'],
                'folly': 'fail',
                'banana': 'nomnom!banana!',
            })
        )

    def assertExactCompletion(self, text, completion):
        """Assert set in `completion` to be identical to completion set"""
        matches = self.repl.completer.get_completion_matches(text)
        self.assertEqual(set(matches), set(completion))

    def assertInCompletion(self, text, completion):
        """Assert all items in `completion` are in the completion set"""
        matches = self.repl.completer.get_completion_matches(text)
        for item in completion:
            self.assert_(item in matches)

    def assertNonCompletion(self, text, completion):
        """Assert all items in `completion` are not in the completion set"""
        matches = self.repl.completer.get_completion_matches(text)
        for item in completion:
            self.assert_(item not in matches)

    def test_variables(self):
        self.assertExactCompletion('{{', ['{{ food', '{{ folly', '{{ banana', '{{ True', '{{ False', '{{ None'])
        self.assertExactCompletion('{{ ', ['{{ food', '{{ folly', '{{ banana', '{{ True', '{{ False', '{{ None'])
        self.assertExactCompletion('{{ T', ['{{ True'])
        self.assertExactCompletion('{{ fo', ['{{ food', '{{ folly'])
        self.assertExactCompletion('{{ foo', ['{{ food'])

    def test_tags(self):
        self.assertInCompletion('{%', ['{% if', '{% for'])
        self.assertInCompletion('{% ', ['{% if', '{% for'])
        self.assertExactCompletion('{% if', ['{% ifequal', '{% if', '{% ifnotequal', '{% ifchanged'])

    # TODO: test filters, space separated variables, and longer expressions with more tokens

    def test_ppp(self):
        """
        Tests for _get_completion_ppp() function which returns the
        "ppp" (Prefix, Pivot, and Partial) for a given input
        """
        self.assertEqual(
            self.repl.completer._get_completion_ppp('{{'),
            ('{', '{', ''))

        self.assertEqual(
            self.repl.completer._get_completion_ppp('{{ var }}{% get_'),
            ('{{ var }}{', '%', ' get_'))

        self.assertEqual(
            self.repl.completer._get_completion_ppp('{% tag %}{{ this|m'),
            ('{% tag %}{{ this', '|', 'm'))

        self.assertEqual(
            self.repl.completer._get_completion_ppp('{{ this|m:'),
            ('{{ this|m', ':', ''))

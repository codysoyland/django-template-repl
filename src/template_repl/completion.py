from django.template import Lexer, TOKEN_TEXT

class Completer(object):
    """
    Provides command-line completion compatible with readline
    using the `complete` method.

    Completion works by splitting text into three segments, a
    `prefix`, a `pivot`, and a `partial`.

    The prefix is the first part of the line, which does not affect
    guessed completions.

    The pivot is the metacharacter which affects completion. There
    are 4 metacharacters. Each has a separate handler to guess input.

        PIVOT   HANDLER
        -----   -------
        |       filter
        %       tag
        {       variable
        :       variable

    The partial is the third segment. It is used to filter guesses
    provided by the pivot handler. For example, if the pivot is a pipe,
    the pivot handler would guess a list of filters and remove elements
    from the list that don't start with the text in the partial.
    """
    def __init__(self, context, parser):
        self.completion_matches = []
        self.context = context
        self.parser = parser

    def complete(self, text, state):
        """
        This hackjob is the result of how readline calls the completer.
        It calls this method with the same text but an increasing "state"
        value and wants you to return guesses, one at a time, ending with
        None, telling readline you have no more guesses. I'm just using it
        as a kind of wrapper for get_completion_matches().
        """
        if not self.completion_matches and state == 0:
            self.completion_matches = self.get_completion_matches(text)
        try:
            return self.completion_matches.pop()
        except IndexError:
            return None

    def get_completion_matches(self, text):
        """
        Return list of completion matches given the input `text`.
        """
        vars = set()
        for dct in self.context.dicts:
            vars.update(dct.keys())
        vars = list(vars)
        filters = self.parser.filters.keys()
        tags = list(self.parser.tags.keys())
        tags.extend(['endif', 'endifequal', 'endfor', 'endwhile', 'endfilter', 'endcomment'])

        (prefix, pivot, partial) = self._get_completion_ppp(text)

        if pivot == '{':
            possibilities = [' %s' % var for var in vars]
        elif pivot in ' :':
            possibilities = ['%s' % var for var in vars]
        elif pivot == '%':
            possibilities = [' %s' % tag for tag in tags]
        elif pivot == '|':
            possibilities = ['%s' % filt for filt in filters]

        # Filter out possibilites that do not start with the text in the partial
        possibilities = filter(
            lambda poss: poss.startswith(partial),
            possibilities)

        return [(prefix + pivot + poss) for poss in possibilities]

    def _get_completion_ppp(self, text):
        """
        Return tuple containing the prefix, pivot, and partial
        of the current line of input.

            >>> completer._get_completion_ppp('{{')
            ('{', '{', '')
            >>> completer._get_completion_ppp('{{ var }}{% get_')
            ('{{ var }}{', '%', ' get_')

        How it works:
        1. Tokenize text, add first n-1 tokens to "prefix".
        2. Split on final "|%{:". Call it "pivot".
        3. Any text after pivot is called the "partial".
        4. Text prior to the pivot but after the first n-1 tokens
           is appended to the prefix.
        """
        if len(text) == 0:
            return ('', '', '')

        prefix = ''
        partial = ''
        pivot = ''

        tokens = Lexer(text, None).tokenize()

        if tokens[-1].token_type != TOKEN_TEXT:
            return (text, '', '')

        prefix_tokens = tokens[:-1]
        working_area = tokens[-1].contents

        prefix = text[:-len(working_area)]

        # Iterate backwards through string, finding the first
        # occurrence of any of the chars "|%{:". Call it the pivot.
        for index, char in list(enumerate(working_area))[::-1]:
            if char == ' ':
                if ' ' in working_area[:index]:
                    pivot = char
                    break
            if char in '|%{:':
                pivot = char
                break

        # No pivot was found
        if len(pivot) == 0:
            return (text, '', '')

        pieces = working_area.split(pivot)

        prefix += pivot.join(pieces[:-1])
        partial = pieces[-1]

        return (prefix, pivot, partial)

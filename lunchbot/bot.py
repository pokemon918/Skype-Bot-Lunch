"""
Bot's knowledge data base.

:copyright: (c) 2017 by Serhii Shvorob.
:license: MIT, see LICENSE for more details.
"""
import random

DEFAULT_RULE = '$default'
GREETING_RULE = '$greeting'


class Command(object):

    """Base class for commands."""

    def __init__(self, parent):
        self.parent = parent
        self.parameters = []

    def process(self, context):
        raise NotImplementedError


class EchoCommand(Command):

    """@echo command."""

    def process(self, context):
        return ['\n'.join(param.format_map(context) for param in self.parameters)]


class RedirectCommand(Command):

    """@redirect command."""

    def process(self, context):
        result = []
        for param in self.parameters:
            processed_param = param.format_map(context)
            if processed_param:
                result.extend(self.parent.query(processed_param, context))
        return result


class RandomCommand(Command):

    """@random command."""

    def process(self, context):
        options = [param for param in self.parameters if param]
        choice = random.choice(options)

        processed_param = choice.format_map(context)
        return self.parent.query(processed_param, context)


class Rule(object):

    """Rule class."""

    def __init__(self, parent):
        self.parent = parent

        self.commands = []

    def process(self, context):
        result = []
        for cmd in self.commands:
            result.extend(cmd.process(context))
        return result


class BotDb(object):

    """Bot's knowledge DB."""

    def __init__(self, db_file):
        self.rules = {}

        self._load_db(db_file)

    def _load_db(self, db_file):
        with open(db_file, 'r', encoding='utf-8') as f:
            rule = None
            cmd = None
            for line in f:
                line = line.strip()
                if line.startswith('#'):
                    # Comment
                    continue
                elif line.startswith('%'):
                    # Rule
                    rule = Rule(self)
                    for pattern in line.lower()[1:].split(','):
                        self.rules[pattern.strip()] = rule
                elif line.startswith('@'):
                    # Command
                    if line == '@echo':
                        cmd = EchoCommand(self)
                    elif line == '@redirect':
                        cmd = RedirectCommand(self)
                    elif line == '@random':
                        cmd = RandomCommand(self)
                    else:
                        raise ValueError('Unknown command: {}'.format(line))

                    rule.commands.append(cmd)
                else:
                    if not cmd:
                        continue
                    cmd.parameters.append(line)

    def query(self, message, context=None):
        """Performs search in knowledge DB of specified message.

        Context is a dict of variables and their values can be used during response rendering.
        """
        if message:
            request = message.splitlines()[0].strip().lower()
        else:
            return []

        if context:
            query_context = context.copy()
        else:
            query_context = {}
        query_context.update(message=message, request=request)

        rule = self.rules.get(request)
        if not rule:
            rule = self.rules.get(DEFAULT_RULE)
        if not rule:
            return []

        return rule.process(query_context)

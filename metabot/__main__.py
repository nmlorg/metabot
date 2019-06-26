"""Modularized, multi-account bot."""

import logging

from metabot.modules import admin
from metabot import multibot
from metabot.util import humanize
from metabot.util import modutil


def main():  # pylint: disable=missing-docstring
    logging.basicConfig(format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s] %(message)s',
                        level=logging.INFO)

    mybot = multibot.MultiBot(modutil.load_modules('metabot.modules'), confdir='config')
    if not mybot.conf['bots']:
        print()
        print("Hi! Before I can start, I need at least one bot's Telegram token. If you don't have "
              'one already, follow the instructions at:')
        print()
        print('    https://core.telegram.org/bots#creating-a-new-bot')
        print()
        print('At the end, BotFather will send you a message starting with "Use this token" '
              'followed by a line starting with a number. Copy the full line starting with the '
              'number and paste it here:')
        print()
        while not mybot.conf['bots']:
            initial_token = input('Telegram token: ')
            try:
                username = mybot.add_bot(initial_token)
            except AssertionError:
                print()
                print("That doesn't look quite right. Look for a message from BotFather starting "
                      'with "Use this token" followed by a line starting with a number. Copy the '
                      'full line starting with the number and paste it here:')
                print()
            except Exception as exc:  # pylint: disable=broad-except
                print()
                print('Woops, that generated: %r', exc)
            else:
                mybot.run_bot(username)
    unconfigured = sorted(username for username, botconf in mybot.conf['bots'].items()
                          if not botconf['issue37']['admin'].get('admins'))
    if unconfigured:
        print()
        print('To configure %s, open a chat with:' % humanize.list(unconfigured))
        print()
        for username in unconfigured:
            print('    https://t.me/%s' % username)
        print()
        print('and type:')
        print()
        print('    /_bootstrap %s' % admin.BOOTSTRAP_TOKEN)
        print()
    mybot.run()


if __name__ == '__main__':
    main()

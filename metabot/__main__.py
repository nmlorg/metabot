"""Modularized, multi-account bot."""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging

from metabot.modules import admin
from metabot.modules import newbot
from metabot import multibot

try:
    raw_input
except NameError:
    raw_input = input  # pylint: disable=invalid-name,redefined-builtin


def main():  # pylint: disable=missing-docstring
    logging.basicConfig(
        format='%(asctime)s %(levelname)s %(filename)s:%(lineno)s] %(message)s', level=logging.INFO)

    mybot = multibot.MultiBot({admin, newbot}, fname='config/multibot.json')
    if not mybot.bots:
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
        while not mybot.bots:
            initial_token = raw_input('Telegram token: ')
            if initial_token.count(':') != 1 or not initial_token.split(':')[0].isdigit():
                print()
                print("That doesn't look quite right. Look for a message from BotFather starting "
                      'with "Use this token" followed by a line starting with a number. Copy the '
                      'full line starting with the number and paste it here:')
                print()
            else:
                try:
                    username = mybot.add_bot(initial_token)
                except Exception as exc:  # pylint: disable=broad-except
                    print()
                    print('Woops, that generated: %r', exc)
                else:
                    mybot.enable_module(username, 'newbot')
                    mybot.run_bot(username)
    mybot.run()


if __name__ == '__main__':
    main()

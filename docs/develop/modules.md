```shell
MODULENAME=somethingcool
python3 -m venv metabot.modules.${MODULENAME}
cd metabot.modules.${MODULENAME}
source bin/activate
mkdir -p metabot/modules
for i in metabot metabot/modules; do
  echo "__import__('pkg_resources').declare_namespace(__name__)" > ${i}/__init__.py
done
cat >setup.py <<EOF
import setuptools


setuptools.setup(
    name='metabot.modules.${MODULENAME}',
    version='0.0.1',
    packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    namespace_packages=setuptools.find_packages(include=('metabot', 'metabot.*')),
    install_requires=['metabot'])
EOF
pip install -e .
cat >metabot/modules/${MODULENAME}.py <<EOF
"""Do something cool!"""

from __future__ import absolute_import, division, print_function, unicode_literals


def modhelp(unused_ctx, unused_modconf, sections):
    sections['commands'].add('/${MODULENAME} - Do something cool!')


def moddispatch(ctx, msg, unused_modconf):
    if ctx.type in ('message', 'callback_query') and ctx.command == '${MODULENAME}':
        return ${MODULENAME}(ctx, msg)

    return False


def ${MODULENAME}(ctx, msg):
    msg.add('Your user id is %s!', ctx.user['id'])
EOF
metabot
```

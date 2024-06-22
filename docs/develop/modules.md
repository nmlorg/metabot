```shell
MODULENAME=somethingcool
python3 -m venv metabot.modules.${MODULENAME}/.venv --prompt=${MODULENAME}
cd metabot.modules.${MODULENAME}
source .venv/bin/activate
mkdir -p metabot/modules
cat >pyproject.toml <<EOF
[project]
name = 'metabot.modules.${MODULENAME}'
version = '0.0.1'
dependencies = [
    'metabot',
]

[tool.setuptools.packages.find]
include = ['metabot', 'metabot.*']
EOF
pip install -e .
cat >metabot/modules/${MODULENAME}.py <<EOF
"""Do something cool!"""


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

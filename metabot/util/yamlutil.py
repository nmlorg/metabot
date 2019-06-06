"""Simplified interface to https://pyyaml.org/wiki/PyYAMLDocumentation."""

import yaml


def load(fname):
    """Load fname as a YAML file, silently returning None on any error."""

    try:
        data = open(fname, 'rb').read()
    except IOError:
        return

    try:
        return yaml.safe_load(data)
    except yaml.error.YAMLError:
        pass


def dump(fname, obj):
    """Save obj as a YAML file to fname."""

    data = yaml.dump_all([obj], indent=4, width=200, Dumper=_SimplifyingDumper).encode('ascii')
    with open(fname, 'wb') as fobj:
        fobj.write(data)
    return obj


class _SimplifyingRepresenter(yaml.representer.SafeRepresenter):
    yaml_multi_representers = {
        dict: yaml.representer.SafeRepresenter.represent_dict,
        list: yaml.representer.SafeRepresenter.represent_list,
    }


# pylint: disable=too-many-ancestors
class _SimplifyingDumper(yaml.emitter.Emitter, yaml.serializer.Serializer, _SimplifyingRepresenter,
                         yaml.resolver.Resolver):

    # pylint: disable=too-many-arguments,too-many-locals
    def __init__(self,
                 stream,
                 default_style=None,
                 default_flow_style=False,
                 canonical=None,
                 indent=None,
                 width=None,
                 allow_unicode=None,
                 line_break=None,
                 encoding=None,
                 explicit_start=None,
                 explicit_end=None,
                 version=None,
                 tags=None,
                 sort_keys=True):
        yaml.emitter.Emitter.__init__(self,
                                      stream,
                                      canonical=canonical,
                                      indent=indent,
                                      width=width,
                                      allow_unicode=allow_unicode,
                                      line_break=line_break)
        yaml.serializer.Serializer.__init__(self,
                                            encoding=encoding,
                                            explicit_start=explicit_start,
                                            explicit_end=explicit_end,
                                            version=version,
                                            tags=tags)
        _SimplifyingRepresenter.__init__(self,
                                         default_style=default_style,
                                         default_flow_style=default_flow_style,
                                         sort_keys=sort_keys)
        yaml.resolver.Resolver.__init__(self)


from application.configuration import ConfigSection, ConfigSetting
from sipsimple.configuration.datatypes import Port

from op2d import cfg_filename


class Configuration(ConfigSection):
    __cfgfile__ = cfg_filename
    __section__ = 'op2d'

    hal_backend = ConfigSetting(type=str, value=None)
    web_port    = ConfigSetting(type=Port, value=8088)


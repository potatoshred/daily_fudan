VERSION = "0.0.0"

import os

_CONFIG_PATH = "../config.ini"
if os.path.exists(_CONFIG_PATH):
    import configparser

    config = configparser.ConfigParser()
    config.read(_CONFIG_PATH)
    LOG_LEVEL = config.get("log", "LOG_LEVEL")
    if LOG_LEVEL:
        try:
            LOG_LEVEL = int(LOG_LEVEL)
        except ValueError:
            print("配置文件⑧太行")
    else:
        print("👎配置文件⑧行")

else:
    LOG_LEVEL = 1
    with open(_CONFIG_PATH, "w", encoding="utf-8") as fo:
        fo.write("[log]\n"
                 "LOG_LEVEL=1\n"
                 )

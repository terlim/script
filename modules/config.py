import logging
from pathlib import Path
from configparser import ConfigParser as CP, MissingSectionHeaderError,\
    DuplicateOptionError, DuplicateSectionError


def check_config_file(fileName: Path, cfg: CP) -> bool:
    """ Checking config file """
    try:
        cfg.read(fileName)
    except MissingSectionHeaderError as err:
        logging.getLogger("app.check_config").error(err)
        return False

    except DuplicateSectionError as err:
        logging.getLogger("app.check_config").error(err)
        return False

    except DuplicateOptionError as err:
        logging.getLogger("app.check_config").error(err)
        return False

    else:
        return True

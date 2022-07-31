import logging
import shutil
import datetime
from pathlib import Path
from configparser import ConfigParser as CP


from modules.init_logger import init_logger
from modules.cliparam import cliparam
from modules.config import *
from modules.unit import Unit
from modules.ziplog import ziplog
from modules.sendreport import send_report


def clear_logs(logFile: Path()):
    dir = logFile.resolve()
    if dir.exists():
        shutil.rmtree(dir)
        dir.mkdir()
    else:
        dir.mkdir()


def main():

    # Get CLI param
    args = cliparam()

    DEFAULT_CONFIG = Path.cwd().joinpath("settings.ini")
    LOG_FILE = Path.cwd().joinpath("log/")
    CONFIG_FILE = Path.cwd().joinpath(args.config)
    WITH_PROGRESS = args.log_mode
    NAME_APP = "app"
    FILE_TO_BODY = LOG_FILE.joinpath(NAME_APP + ".log")
    clear_logs(LOG_FILE)

    logger = init_logger(LOG_FILE, NAME_APP)
    cfg = CP()
    logging.getLogger("app").info("START")
    if CONFIG_FILE.exists():
        if check_config_file(CONFIG_FILE, cfg):
            if (len(cfg.sections())) > 0:
                for unitName in cfg.sections():
                    unit = Unit(unitName, cfg)
                    logging.getLogger("app").info(f'start "{unit.name}"')
                    if unit.check_source():
                        if unit.check_dst():
                            if unit.check_rotation():
                                logger = init_logger(LOG_FILE, unit.name, mode=WITH_PROGRESS)
                                if unit.copy_unit(WITH_PROGRESS):
                                    unit.copy_chmod()
                                    unit.del_copies()
                            else:
                                logging.getLogger("app").info(f'No rotation \
copy today "{unit.name}"')
                        else:
                            if unit.create_dst():
                                if unit.check_rotation():
                                    logger = init_logger(LOG_FILE, unit.name, mode=WITH_PROGRESS)
                                    if unit.copy_unit(WITH_PROGRESS):
                                        unit.copy_chmod()
                                        unit.del_copies()
                                else:
                                    logging.getLogger("app").info(f'No \
rotation copy today "{unit.name}"')
                            else:
                                exit()
                    logging.getLogger("app").info(f'end "{unit.name}"')
            else:
                logger.error(f'{CONFIG_FILE} is empty!')
    else:
        logger.error(f'{CONFIG_FILE} not found!')

    ziplog(LOG_FILE)

    mail_settings = {}
    mail_settings["mailto"] = cfg.get("DEFAULT", "mailto")
    mail_settings["mailfrom"] = cfg.get("DEFAULT", "mailfrom")
    mail_settings["mailpassword"] = cfg.get("DEFAULT", "mailpass")
    mail_settings["smtpserver"] = cfg.get("DEFAULT", "smtpserver")
    mail_settings["smtpport"] = cfg.get("DEFAULT", "smtpport")
    mail_settings["today"] = str(datetime.date.today())

    logging.getLogger("app").info("Send report")
    send_report(FILE_TO_BODY, mail_settings)

    logging.getLogger("app").info("END")


if __name__ == "__main__":
    main()

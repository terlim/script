import shutil
import os
import stat
import sys
import fnmatch
import datetime
import logging
from pathlib import Path
from tqdm import tqdm

from configparser import ConfigParser as CP, NoOptionError, NoSectionError


def is_date(str_item: str) -> bool:
    try:
        datetime.datetime.strptime(str_item, '%Y-%m-%d').date()
        return True
    except ValueError as err:
        logging.getLogger("app.Unit").error(err)
        return False


class Unit:

    def __init__(self, name: str, cfg: CP):
        self.name = name
        self.today = ""
        self.src = ""
        self.dst = ""
        self.ignored = ""
        self.rotation = ""
        self.copies = ""
        self.mailto = ""
        self.mailfrom = ""
        self.mailuser = ""
        self.mailpass = ""
        self.smtpserver = ""
        self.smtpport = ""

        if not self.__setprop(self.name, cfg):
            logging.getLogger("app.Unit").critical("Program aborted!")

    def __setprop(self, name: str, cfg: CP) -> bool:
        for prop in vars(self):
            if not prop == "name" and not prop == "today":
                try:
                    value = cfg.get(name, prop)
                    if prop == "ignored":
                        value = self.__set_ignored(value, cfg)
                    if prop == "dst":
                        value = self.__set_destination(value, name)
                    self.__setattr__(prop, value)
                except NoOptionError as err:
                    logging.getLogger("app.Unit").error(err)
                    return False
            if prop == "today":
                self.today = str(datetime.date.today())
        return True

    def __set_destination(self, item: str, name: str) -> str:
        dest = Path(item).resolve() / name
        return dest

    def __set_ignored(self, item: str, cfg: CP) -> list:
        res = []
        res.extend(str(cfg.get("DEFAULT", "ignored")).split(','))
        res.extend(item.split(','))
        res = list(set(res))
        res = list(filter(None, res))
        return res

    def __match(self, file_path: Path, patterns: tuple) -> bool:
        strfile = str(file_path)
        for pattern in patterns:
            if fnmatch.fnmatch(strfile, pattern):
                return True
        return False

    def __calc_files(self, src) -> int:
        calc = 0
        for file_path in Path(src).rglob('*'):
            if self.__match(file_path, self.ignored):
                continue
            elif file_path.is_dir():
                continue
            calc += 1
        return calc

    def __copy_with_progress(self, src, dst, *, folow_symlinks=True):
        if Path(dst).is_dir():
            dst = Path(dst).joinpath(Path(src).name)
        shutil.copyfile(src, dst, follow_symlinks=folow_symlinks)
#       shutil.copymode(src, dst, follow_symlinks=folow_symlinks)
        self.__bar.update()
        logging.getLogger(self.name).info(f'{Path(dst).resolve()}')
        return dst

    def __copy_with_logging(self, src, dst, *, folow_symlinks=True):
        if Path(dst).is_dir():
            dst = Path(dst).joinpath(Path(src).name)
        shutil.copyfile(src, dst, follow_symlinks=folow_symlinks)
#        shutil.copymode(src, dst, follow_symlinks=folow_symlinks)
        logging.getLogger(self.name).info(f'{Path(dst).resolve()}')
        return dst

    def check_source(self) -> bool:
        src = Path(self.src).resolve()
        try:
            src.exists()
            logging.getLogger("app.Unit").info(f'"{self.name}" - source \
 "{src}" - OK')
            return True
        except Exception as err:
            logging.getLogger("app.Unit").error(err)
            return False

    def check_dst(self) -> bool:
        dst = Path(self.dst).resolve()
        if dst.exists():
            logging.getLogger("app.Unit").info(f'"{self.name}" - destination \
"{dst}" - OK')
            return True
        else:
            logging.getLogger("app.Unit").error(f'"{self.name}" - destination \
"{dst}" - NOT EXIST')

    def create_dst(self) -> bool:
        try:
            Path(self.dst).mkdir(parents=True)
            logging.getLogger("app.Unit").info(f'"{self.name}" - destination \
create OK')
            return True
        except Exception as err:
            logging.getLogger("app.Unit").error(err)
            return False

    def check_rotation(self) -> bool:
        todayDir = datetime.datetime.strptime(self.today, '%Y-%m-%d').date()
        dirs = [dir.name for dir in Path(self.dst).iterdir() if dir.is_dir()]
        if not len(dirs) == 0:
            dirs = list(filter(is_date, dirs))
            dirs.sort(reverse=True)

            itemDir = datetime.datetime.strptime(dirs[0], '%Y-%m-%d').date()
            if (todayDir - itemDir).days >= int(self.rotation):
                return True
            else:
                return False
        return True

    def copy_unit(self, mode: int) -> bool:
        dst = Path(self.dst) / self.today
        src = Path(self.src)
        if mode == 0:
            calc = self.__calc_files(src)
            logging.getLogger("app.Unit").info(f'Source files - "{calc}"')
            try:
                shutil.copytree(src,
                                dst,
                                copy_function=self.__copy_with_logging,
                                ignore=shutil.ignore_patterns(*list(self.ignored)))
                logging.getLogger("app.Unit").info("copy success")
                calc = self.__calc_files(dst)
                logging.getLogger("app.Unit").info(f'Dest files - "{calc}"')
                return True
            except Exception as err:
                logging.getLogger("app.Unit").error(err)
                return False
        elif mode == 1:
            logging.getLogger("app.Unit").info(f'calculating...')
            calc = self.__calc_files(src)
            self.__bar = tqdm(total=calc)
            try:
                shutil.copytree(src,
                                dst,
                                copy_function=self.__copy_with_progress,
                                ignore=shutil.ignore_patterns(*list(self.ignored)))
                self.__bar.close()
                logging.getLogger("app.Unit").info("copy success")
                return True
            except Exception as err:
                logging.getLogger("app.Unit").error(err)
                return False

    def del_copies(self):
        todayDir = datetime.datetime.strptime(self.today, '%Y-%m-%d').date()
        dst = Path(self.dst)
        dirs = [dir.name for dir in Path(self.dst).iterdir() if dir.is_dir()]
        if not len(dirs) == 0:
            dirs = list(filter(is_date, dirs))
            dirs.sort(reverse=True)
            del dirs[0: int(self.copies)]
            for item in dirs:
                item_path = dst.joinpath(item)
                shutil.rmtree(item_path)
                logging.getLogger("app.Unit").info(f'"{item}" in \
"{self.name}" - has been deleted')

    def __change_permission_recursive(self, path, mode):
        for root, dirs, files in os.walk(path, topdown=False):
            for dir in [os.path.join(root, d) for d in dirs]:
                os.chmod(dir, mode)
        for file in [os.path.join(root, f) for f in files]:
            os.chmod(file, mode)

    def copy_chmod(self):
        dst = Path(self.dst) / self.today
        logging.getLogger("app.Unit").info(f'chmod (0755) - "{dst}" ')
        self.__change_permission_recursive(dst, 0o777)
        logging.getLogger("app.Unit").info(f'chmod "{dst}" - done ')

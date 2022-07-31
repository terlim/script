import argparse


def cliparam():
    cliParser = argparse.ArgumentParser(
        description='Script for automatic file copying')
    cliParser.add_argument('-lm', '--log_mode', type=int, default=0,
                           help='Trace log mode. Provide an integer \
                               (default: 0) 1 - progressbar, 0 - stdout')
    cliParser.add_argument('-cfg', '--config', type=str,
                           default='settings.ini', help='Set INI settings\
                               file. Provide an string\
                                   (default: settings.ini)')
    return(cliParser.parse_args())

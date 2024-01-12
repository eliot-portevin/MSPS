import os
import sys


def progressbar(it, prefix="Calculating", out=sys.stdout):
    count = len(it)

    # Calculate the size of the progress bar
    try:
        size = abs(os.get_terminal_size().columns - len(prefix) - 20)
    except OSError:
        size = 50

    def show(j):
        x = int(size * j / count)
        print(f"{prefix}[{u'█' * x}{('.' * (size - x))}] {j}/{count}", end='\r', file=out, flush=True)

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    print("\n", flush=True, file=out)


def print_console_title(title: str):
    print('##########################\n' +
          title.upper() + '\n'
                          '##########################\n')


def format_track_name(title, artist):
    return artist + " - " + title

def get_app_title():
    return "" \
           "\n.-.   .-. .----. .----..----. " \
           "\n|  `.'  |{ {__  { {__  | {}  }" \
           "\n| |\ /| |.-._} }.-._} }| .--' " \
           "\n`-' ` `-'`----' `----' `-'    " \
           "\n"

def print_message(message: str):
    print(get_app_title())
    print(message)
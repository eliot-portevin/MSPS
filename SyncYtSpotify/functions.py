import os
import sys


def progressbar(it, prefix="Calculating", out=sys.stdout):
    count = len(it)

    # Calculate size of progress bar
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


def get_search_string(item):
    return item['artist'] + " - " + item['song']

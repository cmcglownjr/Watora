import argparse
import logging
import sys
import pathlib
import subprocess
from tempfile import TemporaryFile
import asyncio

try:
    import uvloop
except ImportError:
    pass
else:
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

loop = asyncio.get_event_loop()


def setup_logging():
    log = logging.getLogger('launcher')
    log.setLevel(logging.DEBUG)

    sh = logging.StreamHandler(stream=sys.stdout)
    sh.setFormatter(logging.Formatter(fmt="[%(asctime)s] - %(levelname)s: %(message)s"))
    sh.setLevel(logging.INFO)
    log.addHandler(sh)

    tfh = logging.StreamHandler(stream=TemporaryFile('w+', encoding='utf8'))
    tfh.setFormatter(logging.Formatter(fmt="[%(asctime)s] - %(levelname)s - %(name)s: %(message)s"))
    tfh.setLevel(logging.DEBUG)
    log.addHandler(tfh)


def check_dependencies():
    try:
        import discord
        import lavalink
        import listenmoe
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])


def create_watora_instance(shard_count=None, shard_ids=None):
    from bot import Watora
    return Watora(shard_count=shard_count, shard_ids=shard_ids)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-checks', action='store_true')
    args = parser.parse_args()

    setup_logging()

    check_dependencies()

    shard_count = 30
    shard_per_instance = 10
    instance_count = shard_count // shard_per_instance

    selection = -1
    if not args.no_checks:
        selection = int(input('Enter instance number (between 0 and {}): '.format(instance_count - 1)))

    start = selection * shard_per_instance
    end = start + shard_per_instance

    shard_ids = list(range(start, end))

    m = create_watora_instance(shard_count=shard_count, shard_ids=shard_ids)

    try:
        sh.terminator = ''
        log.info("Connecting\n")
        sh.terminator = '\n'

        m.run()

    except KeyboardInterrupt:
        log.info("Shutting down gracefully...")

    except Exception as e:
        log.warning("Error starting Watora")
        log.warning(e)

    finally:
        loop.close()

    log.info("All done.")


if __name__ == '__main__':
    main()

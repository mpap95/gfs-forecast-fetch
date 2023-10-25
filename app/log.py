import logging

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)
log = logging.getLogger()


def set_log_level_debug():
    log.setLevel(logging.debug())

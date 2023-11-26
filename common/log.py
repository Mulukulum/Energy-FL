import logging
from .configuration import DEVICE_USERNAME, IP_CLIENTS, LOGGING_LEVEL

if DEVICE_USERNAME in IP_CLIENTS:
    IP_SELF = IP_CLIENTS[DEVICE_USERNAME]
else:
    IP_SELF = DEVICE_USERNAME

logging.basicConfig(
    format=rf"%(asctime)s | %(levelname)s | [%(filename)s:%(lineno)d] {IP_SELF} | %(message)s",
    level=LOGGING_LEVEL,
    datefmt=r"%d %b %Y %H:%M:%S",
)

energy_fl_logger = logging.getLogger(name="Energy-FL")
energy_fl_logger.info("Logger Started!")

import pyorthanc

from . import config

client = pyorthanc.Orthanc(
    url=config.ORTHANC_URL,
    username=config.ORTHANC_USERNAME,
    password=config.ORTHANC_PASSWORD,
    timeout=300
)

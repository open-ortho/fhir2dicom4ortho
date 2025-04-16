""" Configuration and variables.

Class to get options from env variables.

Argparse support was purposely removed, because it was creating too much trouble
with unittests, and too much overhead. Arguments can be just as easily passed as
env vars, and since this is a server, not a tool to be used every day, arguments
should not be necessary anyways.

"""
import os
from typing import Optional


def strtobool(value):
    """ Convert a string to a boolean value. """
    return value.lower() in ('yes', 'true', 't', '1')


class Namespace:
    """ Namespace class to hold arguments. """
    # Variables used in load_arguments
    verbosity: int
    fhir_api: bool
    fhir_listen: str
    fhir_port: int
    pacs_send_method: str
    pacs_wado_url: str
    pacs_wado_username: str
    pacs_wado_password: str
    pacs_dimse_aet: str
    pacs_dimse_hostname: str
    pacs_dimse_port: int
    tasks_db_url: Optional[str]

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class ArgsCache:
    """ Cache for arguments. """
    _args = None

    @staticmethod
    def get_arguments(test_args=None):
        """ Get the arguments from the cache or load them from the environment. """
        if test_args is not None:
            return Namespace(**test_args)
        if ArgsCache._args is None:
            ArgsCache._args = ArgsCache.load_arguments()
        return ArgsCache._args

    @staticmethod
    def load_arguments():
        """ Load the arguments from the environment """
        # Create an object similar to argparse.Namespace
        tasks_db_url = os.getenv('F2D4O_TASKS_DB_FILENAME', None)
        if tasks_db_url is not None:
            tasks_db_url = f"sqlite:///{tasks_db_url}"
        verbosity = os.getenv('F2D4O_VERBOSITY', str(0))
        return Namespace(
            # The path of the SQLite DB file for the local mapping.
            verbosity=int(verbosity),

            # FHIR API server IP and port.
            fhir_api=bool(strtobool(os.getenv('F2D4O_FHIR_API', 'True'))),
            fhir_listen=os.getenv('F2D4O_FHIR_LISTEN', '*'),
            fhir_port=int(os.getenv('F2D4O_FHIR_PORT', '8000')),

            pacs_send_method=os.getenv('F2D4O_PACS_SEND_METHOD', 'dimse'),

            # DICOM PACS destination WADO coordinates.
            pacs_wado_url=os.getenv('F2D4O_PACS_WADO_URL', ''),
            pacs_wado_username=os.getenv('F2D4O_PACS_WADO_USERNAME', ''),
            pacs_wado_password=os.getenv('F2D4O_PACS_WADO_PASSWORD', ''),

            # DICOM PACS destination DIMSE coordinates.
            pacs_dimse_aet=os.getenv('F2D4O_PACS_DIMSE_AET', ''),
            pacs_dimse_hostname=os.getenv('F2D4O_PACS_DIMSE_IP', ''),
            pacs_dimse_port=int(os.getenv('F2D4O_PACS_DIMSE_PORT', '104')),

            # The path of the SQLite DB file for the local mapping. e.g.: 'sqlite:////app/tasks.db'
            tasks_db_url=tasks_db_url
        )

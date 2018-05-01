import os
from ftplib import FTP, socket


class DbgapFtp(object):

    ERROR_STUDY_VALUE = 'study accession must be an integer > 0'
    ERROR_STUDY_VERSION_VALUE = 'study version must be an integer > 0'

    def __init__(self, server='ftp.ncbi.nlm.nih.gov'):
        """Create a new instance of the object and open an ftp connection."""
        self.ftp = FTP(server, timeout=10)
        self.ftp.login()

    def __del__(self):
        """Close any open ftp connections."""
        try:
            self.ftp.close()
        except AttributeError:
            pass

    def _get_base_study_directory(self, accession):
        """Return the expected directory for a study on the dbGaP ftp server."""
        if accession <= 0:
            raise ValueError(self.ERROR_STUDY_VALUE)
        return '/dbgap/studies/phs{accession:06d}'.format(accession=accession)
        

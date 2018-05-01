import os
from ftplib import FTP, socket


class DbgapFtp(object):

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

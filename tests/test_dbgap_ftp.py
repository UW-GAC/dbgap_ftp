from unittest import TestCase
import tempfile
from ftplib import FTP
import socket
import shutil
import os.path

from dbgap_ftp import dbgap_ftp

KNOWN_PHS = 16


class DbgapFtpTest(TestCase):

    def setUp(self):
        self.cnx = dbgap_ftp.DbgapFtp()

    def test_init_creates_ftp_connection(self):
        """Creates an ftp connection and stores it as an attribute."""
        self.assertIsInstance(self.cnx.ftp, FTP)

    def test_init_fails_with_nonexistent_server(self):
        """Fails with proper error if non-existent server is requested."""
        with self.assertRaisesRegex(socket.gaierror, '[Errno 8]'):
            dbgap_ftp.DbgapFtp(server='foo')

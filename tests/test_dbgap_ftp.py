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

    def test_get_base_study_directory_works_with_positive_integer(self):
        self.assertIsInstance(self.cnx._get_base_study_directory(KNOWN_PHS), str)

    def test_get_base_study_directory_fails_with_negative_number(self):
        with self.assertRaisesRegex(ValueError, dbgap_ftp.DbgapFtp.ERROR_STUDY_VALUE):
            self.cnx._get_base_study_directory(-1)

    def test_get_base_study_directory_fails_with_zero(self):
        with self.assertRaisesRegex(ValueError, dbgap_ftp.DbgapFtp.ERROR_STUDY_VALUE):
            self.cnx._get_base_study_directory(0)

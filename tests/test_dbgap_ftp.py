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
        self.object = dbgap_ftp.DbgapFtp()

    def test_init_creates_ftp_connection(self):
        """Creates an ftp connection and stores it as an attribute."""
        self.assertIsInstance(self.object.ftp, FTP)

    def test_init_fails_with_nonexistent_server(self):
        """Fails with proper error if non-existent server is requested."""
        with self.assertRaisesRegex(socket.gaierror, '[Errno 8]'):
            dbgap_ftp.DbgapFtp(server='foo')

    def test_get_base_study_directory_works_with_positive_integer(self):
        self.assertIsInstance(self.object._get_base_study_directory(KNOWN_PHS), str)

    def test_get_base_study_directory_fails_with_negative_number(self):
        with self.assertRaisesRegex(ValueError, dbgap_ftp.DbgapFtp.ERROR_STUDY_VALUE):
            self.object._get_base_study_directory(-1)

    def test_get_base_study_directory_fails_with_zero(self):
        with self.assertRaisesRegex(ValueError, dbgap_ftp.DbgapFtp.ERROR_STUDY_VALUE):
            self.object._get_base_study_directory(0)

    def test_get_study_version_strings_works_with_correct_input(self):
        study_dir = self.object._get_base_study_directory(KNOWN_PHS)
        versions = self.object._get_study_version_strings(KNOWN_PHS)
        for v in versions:
            self.assertTrue(v.startswith('phs'), msg='version {} does not match expected pattern'.format(v))

    def test_get_highest_study_version_works_with_correct_input(self):
        study_dir = self.object._get_base_study_directory(KNOWN_PHS)
        versions = self.object.ftp.nlst(study_dir)
        versions = [v for v in versions if v.startswith(os.path.join(study_dir, 'phs'))]
        most_recent_version = self.object.get_highest_study_version(KNOWN_PHS)
        self.assertIsInstance(most_recent_version, int)
        self.assertEqual(most_recent_version, len(versions))

    def test_get_highest_study_version_string_fails_with_zero_accession(self):
        with self.assertRaises(ValueError):
            self.object.get_highest_study_version(0)

    def test_get_highest_study_version_string_fails_with_negative_accession(self):
        with self.assertRaises(ValueError):
            self.object.get_highest_study_version(-1)

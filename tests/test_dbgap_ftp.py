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
        self.temp_dir = tempfile.mkdtemp()

    def test_init_creates_ftp_connection(self):
        """Creates an ftp connection and stores it as an attribute."""
        self.assertIsInstance(self.object.ftp, FTP)
        shutil.rmtree(self.temp_dir)

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

    def test_get_study_version_directory_works_as_expected(self):
        directory = self.object._get_study_version_directory(KNOWN_PHS, 1)
        self.assertIsInstance(directory, str)
        # Make sure it exists.
        tmp = self.object.ftp.pwd()
        self.object.ftp.cwd(directory)
        # And change back to the original directory.
        self.object.ftp.cwd(tmp)

    def test_get_study_version_directory_fails_with_nonexistent_version(self):
        with self.assertRaisesRegex(RuntimeError, 'does not exist'):
            self.object._get_study_version_directory(KNOWN_PHS, 999)

    def test_get_study_version_directory_fails_with_zero_version(self):
        with self.assertRaisesRegex(ValueError, dbgap_ftp.DbgapFtp.ERROR_STUDY_VERSION_VALUE):
            self.object._get_study_version_directory(KNOWN_PHS, 0)

    def test_get_study_version_directory_fails_with_negative_version(self):
        with self.assertRaisesRegex(ValueError, dbgap_ftp.DbgapFtp.ERROR_STUDY_VERSION_VALUE):
            self.object._get_study_version_directory(KNOWN_PHS, -1)

    def test_get_data_dictionaries_works_as_expected(self):
        dds = self.object.get_data_dictionaries(KNOWN_PHS, 1)
        self.assertIsInstance(dds, list)
        self.assertTrue(len(dds) > 0)
        for dd in dds:
            self.assertTrue(dd.endswith('.xml'),
                            msg='data dictionary {} does not end with xml'.format(dd))

    def test_download_file_works_as_expected(self):
        dds = self.object.get_data_dictionaries(KNOWN_PHS, 1)
        filename = dds[0]
        local_file = self.object._download_file(filename, self.temp_dir)
        self.assertEqual(local_file, os.path.join(self.temp_dir, os.path.basename(filename)))
        self.assertTrue(os.path.exists(local_file))

    def test_download_files(self):
        requested_files = self.object.get_data_dictionaries(KNOWN_PHS, 1)
        downloaded_files, failed = self.object.download_files(requested_files, self.temp_dir, silent=True)
        # Did you get the right number of files returned?
        self.assertEqual(len(requested_files), len(downloaded_files) + len(failed))
        # Get only the basenames of all processed files.
        processed_files = downloaded_files + failed
        processed_files = [os.path.basename(x) for x in processed_files]
        # Does each file exist in the local directory?
        for requested_file in requested_files:
            self.assertTrue(os.path.basename(requested_file) in processed_files)

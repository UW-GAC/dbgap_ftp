import os
from ftplib import FTP, socket
import re

class DbgapFtp(object):

    ERROR_STUDY_VALUE = 'study accession must be an integer > 0'
    ERROR_STUDY_VERSION_VALUE = 'study version must be an integer > 0'
    REGEX_STUDY_VERSION = re.compile(r'^phs(\d{6})\.v(\d+)\.p(\d+)$')

    def __init__(self, server='ftp.ncbi.nlm.nih.gov'):
        """Create a new instance of the object and open an ftp connection."""
        self.ftp = FTP(server, timeout=10)
        self.ftp.login()
        self.n_attempts = 5

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

    def _get_study_version_strings(self, accession):
        directory = self._get_base_study_directory(accession)
        subdirs = self.ftp.nlst(directory)
        subdirs = [os.path.basename(x) for x in subdirs]
        study_versions = [x for x in subdirs if self.REGEX_STUDY_VERSION.match(x)]
        study_versions.sort()
        return study_versions

    def get_highest_study_version(self, accession):
        study_versions = self._get_study_version_strings(accession)
        versions = [int(self.REGEX_STUDY_VERSION.search(v).group(2)) for v in study_versions]
        return max(versions)

    def _get_study_version_directory(self, accession, version):
        if version <= 0:
            raise ValueError(self.ERROR_STUDY_VERSION_VALUE)
        study_directory = self._get_base_study_directory(accession)
        study_versions = self._get_study_version_strings(accession)
        expected_prefix = 'phs{:06d}.v{}.p'.format(accession, version)
        matching_versions = [x for x in study_versions if x.startswith(expected_prefix)]
        if len(matching_versions) == 0:
            raise RuntimeError('phs{:06d}.v{} does not exist'.format(accession, version))
        assert len(matching_versions) == 1
        return os.path.join(study_directory, matching_versions[0])

    def get_data_dictionaries(self, accession, version):
        study_version_directory = self._get_study_version_directory(accession, version)
        dd_directory = os.path.join(study_version_directory, 'pheno_variable_summaries/')
        files = self.ftp.nlst(dd_directory)
        files = [os.path.basename(x) for x in files if 'data_dict' in x and x.endswith('xml')]
        files = [os.path.join(dd_directory, x) for x in files if x.endswith('xml')]
        return files

    def _download_file(self, filename, local_directory):
        base = os.path.basename(filename)
        local_file = os.path.join(local_directory, base)
        # Attempt to download the file, retrying if necessary.
        i = 0
        done = False
        while not done:
            try:
                with open(local_file, 'wb') as f:
                    # Use recommended 32MB for buffer size.
                    self.ftp.retrbinary('RETR {}'.format(filename), f.write, 33554432)
                done = True
            except TimeoutError:
                i += 1
                if i >= self.n_attempts:
                    raise
        return local_file

    def download_files(self, filenames, local_directory, silent=False):
        downloaded_files = []
        failed = []
        for filename in filenames:
            try:
                local_file = self._download_file(filename, local_directory)
                downloaded_files.append(local_file)
            except TimeoutError:
                failed.append(filename)
        if not silent:
            if len(failed > 0):
                print('{} failed files:'.format(len(failed)))
                for failed_file in failed:
                    print('  {}'.format(failed_file))
            print('done!')
        return downloaded_files, failed

import os
from ftplib import FTP
import re


class DbgapFtp(object):

    ERROR_STUDY_VALUE = 'study accession must be an integer > 0'
    ERROR_STUDY_VERSION_VALUE = 'study version must be an integer > 0'
    REGEX_STUDY_VERSION = re.compile(r'^phs(\d{6})\.v(\d+)\.p(\d+)$')

    def __init__(self, server='ftp.ncbi.nlm.nih.gov'):
        """Create a new instance of the object and open an ftp connection.

        Keyword arguments:
        server -- the path to the ftp server
        """
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
        """Return the study version accession strings associated with a given study."""
        directory = self._get_base_study_directory(accession)
        subdirs = self.ftp.nlst(directory)
        subdirs = [os.path.basename(x) for x in subdirs]
        study_versions = [x for x in subdirs if self.REGEX_STUDY_VERSION.match(x)]
        study_versions.sort()
        return study_versions

    def _get_study_versions(self, accession):
        """Return the integer versions associated with a given study."""
        version_directories = self._get_study_version_strings(accession)
        versions = [int(self.REGEX_STUDY_VERSION.search(v).group(2)) for v in version_directories]
        versions.sort()
        return versions

    def get_highest_study_version(self, accession):
        """Return the highest version of a study.

        Arguments:
        accession -- the study accession integer (e.g., 7)

        Returns:
        the maximum study version on the ftp server, as an integer (e.g., 29)

        """
        versions = self._get_study_versions(accession)
        return max(versions)

    def _get_study_version_directory(self, accession, version):
        """Return the ftp directory for a given study version."""
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
        """Return the data dictionary filenames for a study version on the ftp server.

        Arguments:
        accession -- the study accession integer (e.g., 7)
        version -- the study version integer (e.g, 29)

        Returns:
        a list of paths to data dictionary files on the ftp server.

        """
        study_version_directory = self._get_study_version_directory(accession, version)
        dd_directory = os.path.join(study_version_directory, 'pheno_variable_summaries/')
        files = self.ftp.nlst(dd_directory)
        files = [os.path.basename(x) for x in files if 'data_dict' in x and x.endswith('xml')]
        files = [os.path.join(dd_directory, x) for x in files if x.endswith('xml')]
        return files

    def _download_file(self, filename, local_directory):
        """Download a file from the dbGaP server."""
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
        """Download a set of files from the dbGaP server.

        Arguments:
        filenames -- the path to the files on the ftp server to download
        local_directory -- the local directory into which to download the files

        Keyword arguments:
        silent -- operate in silent mode?

        Returns:
        a tuple of lists, where the first element is the local path to the
        downloaded files, and the second element is a list of files that failed
        to download.

        """
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

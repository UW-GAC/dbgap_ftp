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

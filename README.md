# dbgap-ftp

This python package provides a class to retrieve information and download files from dbGaP's ftp server.
At this point, it is not a comprehensive package and insteads provides only specific functionality!

## Example usage:

Instantiate a new connection object:
```python
from dbgap_ftp import dbgap_ftp

con = dbgap_ftp.DbgapFtp()
```

Retrieve the highest version associated with a given study accesion:
```python
# For the Framingham Heart Study, phs000007:
accession = 7
con.get_highest_study_version(7)
```

Retrieve a list of data dictionaries associated with a version of study:
```python
accession = 7
version = 29
dds = con.get_data_dictionaries(7, 29)
# Show only the first five data dictionaries.
dds[:5]
```

Download a list of files from the dbGaP ftp server:
```python
local_path = '/my/local/directory/'
downlaoded, failed = con.download_files(dds, local_path)
```

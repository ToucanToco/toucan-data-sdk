import io
import tempfile
import zipfile

import os
import pandas as pd
from pandas import DataFrame


DF = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
DF2 = pd.DataFrame({'a': ['a', 'b'], 'b': ['c', 'd']})


def default_zip_file(df, df2):
    # type: (DataFrame, DataFrame) -> bytes
    """Return zip file with two DF saved using feather."""
    with io.BytesIO() as memory_file:
        with zipfile.ZipFile(memory_file, mode='w') as zfile:
            tmp = tempfile.NamedTemporaryFile()
            with open(tmp.name, mode='wb'):
                df.to_feather(tmp.name)
            with open(tmp.name, mode='rb') as f:
                content = f.read()
                zfile.writestr('df', content)
            tmp.close()

            tmp2 = tempfile.NamedTemporaryFile()
            with open(tmp2.name, mode='wb'):
                df2.to_feather(tmp2.name)
            with open(tmp2.name, mode='rb') as f:
                content = f.read()
                zfile.writestr('df2', content)
            tmp2.close()
        memory_file.seek(0)
        return memory_file.getvalue()


def default_hdf_store_content():
    with tempfile.NamedTemporaryFile() as tmp_file:
        with pd.HDFStore(tmp_file.name) as store:
            store['df'] = DF.copy()
            store['df2'] = DF2.copy()
        tmp_file.flush()
        tmp_file.seek(0)
        return tmp_file.read()

import io
import tempfile
import zipfile

from pandas import DataFrame


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

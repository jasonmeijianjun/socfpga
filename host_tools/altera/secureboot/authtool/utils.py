import tempfile
from shutil import rmtree

def new_tempfile():
    if not tempfile.tempdir:
        tempfile.tempdir = tempfile.mkdtemp()

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        return temp.name
    
def string_to_tempfile(filedata):
    if not tempfile.tempdir:
        tempfile.tempdir = tempfile.mkdtemp()

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.writelines(filedata)
        return temp.name

def delete_tempfiles():
    if tempfile.tempdir:
        rmtree(tempfile.tempdir)
        tempfile.tempdir = None

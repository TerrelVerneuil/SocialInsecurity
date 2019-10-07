import os
import hashlib
import errno
from werkzeug.utils import secure_filename
from flask import send_from_directory

upload_folder = 'files/uploaded'  # temporary path
max_file_size = 50000000
banned_extensions = []


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() not in banned_extensions


def secure_fn(fname):
    conv = fname.encode('utf-8')
    sec = hashlib.sha224(conv)
    return sec.hexdigest()


def save_file(file, eid, chid=None):
    if file.filename == "":
        return None
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    if file_length > max_file_size:
        return None
    if file and allowed_file(file.filename):
        fpath = '{}/{}'.format(upload_folder, eid)
        if chid:
            fpath = '{}/{}'.format(fpath, chid)
        if not os.path.exists(fpath):
            try:
                os.makedirs(fpath)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
        filename = secure_filename(file.filename)
        file.seek(0)
        file.save(os.path.join(fpath, filename))
        return filename
    else:
        return None


def load_file(filename, eid, chid=None):
    fpath = '{}/{}'.format(upload_folder, eid)
    if chid:
        fpath = '{}/{}'.format(fpath, chid)
    return send_from_directory(fpath, filename)
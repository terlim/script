import zipfile
import os


def ziplog(dir: str):
    zipFile = zipfile.ZipFile('logs.zip', 'w', zipfile.ZIP_DEFLATED)
    for root, dirs, files in os.walk(dir):
        for ffile in files:
            zipFile.write(os.path.join(root, ffile), ffile)
    zipFile.close

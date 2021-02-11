from zipfile import *
import os
import time

class ByteZipInfo(ZipInfo):

    @classmethod
    def from_byte(cls, bytes_stream, file_full_path):
        """
        os.stat_result(st_mode=33188, st_ino=18409616, st_dev=16777221, st_nlink=1, st_uid=501, st_gid=20, st_size=412, st_atime=1611462518, st_mtime=1611462516, st_ctime=1611462516)
        (33279 & 0xFFFF) << 16 中的33279是unix的文件权限,默认是777,对应的os.st_mode
        """
        file_time = time.localtime()
        date_time = file_time[0:6]
        file_full_path = os.path.normpath(os.path.splitdrive(file_full_path)[1])
        while file_full_path[0] in (os.sep, os.altsep):
            file_full_path = file_full_path[1:]
        z_info = cls(file_full_path, date_time)
        z_info.external_attr = (33279 & 0xFFFF) << 16
        z_info.file_size = len(bytes_stream)

        return z_info

class ByteZipFile(ZipFile):

    def write_bytes(self, byte_stream, file_full_path,):
        if not self.fp:
            raise ValueError(
                "Attempt to write to ZIP archive that was already closed")
        if self._writing:
            raise ValueError(
                "Can't write to ZIP archive while an open writing handle exists"
            )
        z_info = ByteZipInfo.from_byte(byte_stream, file_full_path)
        with self.open(z_info, "w") as target:
            target.write(byte_stream)
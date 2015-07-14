# __CR__
# Copyright (c) 2008-2015 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.
# __CR__

'''
Author: Rubicon ISE team
'''

import os
import random
import uuid
import struct
import hashlib

def generate_tmp_file(size, pathfn=None):
    '''Generate a file with given size.
    The content is read from /dev/urandom.
    If the pathfn is not specified, generate it.
    Return the file name.
    '''
    if pathfn == None:
        pathfn = 'tmpfile.' + str(random.randint(0, 10000))

    with open(pathfn, 'wb') as f:
        buff = None
        while size > 0:
            readsize = min(size, 1024*1024)
            if buff == None:
                with open('/dev/urandom', 'rb') as sf:
                    buff = sf.read(readsize)
            else:
                buff = buff[0:readsize]

            f.write(buff)
            size -= readsize

    return pathfn

def get_file_range(offset, readsize, filepath):
    """
    Get range from local file and
    save as another temp file
    """
    filesize = os.path.getsize(filepath)
    end = offset + readsize - 1
    if offset < 0 or readsize <= 0 or end > filesize:
        raise Exception("Request invalid range from file %s, offset:%d " \
            "readsize:%d filesize:%d" % (filepath, offset, readsize, filesize))
    temp_file = "%s_%s_%s" % (filepath, offset, end)
    with open(filepath, 'rb') as f:
        f.seek(offset)
        buff = f.read(readsize)
        with open(temp_file, 'wb') as tf:
            tf.write(buff)
    return temp_file

def get_unique_tmpfile(prefix='tmpfile-'):
    '''
    Only get a unique temp file name
    with a string prefix and a uuid suffix
    '''
    return prefix + str(uuid.uuid4())

# For long-term solution, inherited from file object
# and implement most common methods to act as a file object
# but without real file
class PseudoFile(object):
    '''
    This is to generate huge size data for upload
    without too many local resources requirements.
    '''
    def __init__(self, filesize):
        self.__bsize = 4096
        self.__offset = 0
        self.__data = None
        self.filesize = filesize
        self.md5_digest = None

    def _gen_block(self, blknum):
        unit = struct.pack("I", blknum)
        data = unit * ((self.__bsize - 16)/len(unit))
        chksum = hashlib.md5()
        chksum.update(data)
        data = data + chksum.digest()
        return data

    def read(self):
        if self.filesize < self.__bsize:
            self.__bsize = self.filesize
        length = self.filesize
        data = ''
        while length > 0:
            used = self.__offset % self.__bsize
            if used == 0:
                blknum = self.__offset / self.__bsize
                self.__data = self._gen_block(blknum)

            remain = self.__bsize - used
            transfer = min(length, remain)
            data += self.__data[0:transfer]
            self.__offset += transfer
            length -= transfer

        return data

    def send(self, http_conn):
        if self.filesize < self.__bsize:
            self.__bsize = self.filesize
        length = self.filesize
        data = ''
        self.md5_digest = hashlib.md5()
        while length > 0:
            used = self.__offset % self.__bsize
            if used == 0:
                blknum = self.__offset / self.__bsize
                self.__data = self._gen_block(blknum)

            remain = self.__bsize - used
            transfer = min(length, remain)
            data = self.__data[0:transfer]

            self.md5_digest.update(data)

            self.__offset += transfer
            length -= transfer

            # Send the data immediately once it is generated
            # to avoid memory overflow when generate huge size data
            http_conn.send(data)

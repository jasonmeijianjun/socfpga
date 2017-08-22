#!/usr/bin/env python
# $Header: //acds/rel/17.0std/embedded/host_tools/altera/diskutils/alt_boot_disk_util.py#1 $
#############################################################################
##  alt_boot_disk_util.py
##
##  SOCEDS SD Card Boot Utility
##
##  ALTERA LEGAL NOTICE
##
##  This script is  pursuant to the following license agreement
##  (BY VIEWING AND USING THIS SCRIPT, YOU AGREE TO THE
##  FOLLOWING): Copyright (c) 2013-2014 Altera Corporation, San Jose,
##  California, USA.  Permission is hereby granted, free of
##  charge, to any person obtaining a copy of this software and
##  associated documentation files (the "Software"), to deal in
##  the Software without restriction, including without limitation
##  the rights to use, copy, modify, merge, publish, distribute,
##  sublicense, and/or sell copies of the Software, and to permit
##  persons to whom the Software is furnished to do so, subject to
##  the following conditions:
##
##  The above copyright notice and this permission notice shall be
##  included in all copies or substantial portions of the Software.
##
##  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
##  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
##  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
##  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
##  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
##  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
##  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
##  OTHER DEALINGS IN THE SOFTWARE.
##
##  This agreement shall be governed in all respects by the laws of
##  the State of California and by the laws of the United States of
##  America.
##
##
##  CONTACTING ALTERA
##
##  You can contact Altera through one of the following ways:
##
##  Mail:
##     Altera Corporation
##     Applications Department
##     101 Innovation Drive
##     San Jose, CA 95134
##
##  Altera Website:
##     www.altera.com
##
##  Online Support:
##     www.altera.com/mysupport
##
##  Troubleshooters Website:
##     www.altera.com/support/kdb/troubleshooter
##
##  Technical Support Hotline:
##     (800) 800-EPLD or (800) 800-3753
##        7:00 a.m. to 5:00 p.m. Pacific Time, M-F
##     (408) 544-7000
##        7:00 a.m. to 5:00 p.m. Pacific Time, M-F
##
##     From other locations, call (408) 544-7000 or your local
##     Altera distributor.
##
##  The mySupport web site allows you to submit technical service
##  requests and to monitor the status of all of your requests
##  online, regardless of whether they were submitted via the
##  mySupport web site or the Technical Support Hotline. In order to
##  use the mySupport web site, you must first register for an
##  Altera.com account on the mySupport web site.
##
##  The Troubleshooters web site provides interactive tools to
##  troubleshoot and solve common technical problems.

"""
WARNING!  THIS SCRIPT CAN WRITE DIRECTLY TO YOUR DISK DRIVE AND CAUSE DATA LOSS.  
USE AT YOUR OWN RISK!

This script validates a disk image partition table and then writes the preloader 
and/or bootloader to the a2 partition of the image

Script usage:
alt-boot-disk-util -p preloader -a write disk_file  #writes PREloader to disk
alt-boot-disk-util -b bootloader -a write disk_file  #writes BOOTloader to disk
alt-boot-disk-util -B a10bootloader -a write disk_file #writes a10bootloader to disk

alt-boot-disk-util -p preloader -b bootloader -a write disk_file  #writes BOOTloader and PREloader to disk

alt-boot-disk-util -b bootloader -a write \\.\physicaldrive2  #writes BOOTloader to windows physical disk number 2
#for windows cygwin, you must put \\.\physicaldrive2 in single quotes like this '\\.\physicaldrive2'


This script contains unit tests.  To run them, type:
    python -m unittest discover -p *.py
"""

__version__ = "$Revision: #1 $"
__date__ = "$Date: 2017/01/22 $"
__copyright__ = "Copyright 2014 Altera Corporation."
__p4_file_header__ = "$Header: //acds/rel/17.0std/embedded/host_tools/altera/diskutils/alt_boot_disk_util.py#1 $"

import StringIO
import optparse
import os
import re
import struct
import sys
import unittest

if(os.name == 'nt'):
    #needed to access winapi
    import ctypes
    import ctypes.wintypes
    K32DLL = ctypes.windll.kernel32

class BootDiskUtilError(Exception):
    """Exception class for this script"""
    def __init__(self, value):
        super(BootDiskUtilError, self).__init__(self)
        self.value = value
    def __str__(self):
        return repr(self.value)

#constants from WINAPI
GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
OPEN_EXISTING = 3
FILE_BEGIN = 0
IOCTL_DISK_GET_DRIVE_GEOMETRY_EX = 0x700a0
IOCTL_STORAGE_GET_DEVICE_NUMBER = 0x2d1080
INVALID_HANDLE_VALUE = -1
DISK_GEOMETRY_EX_STRUCT_SIZE = 40
STORAGE_DEVICE_NUMBER_STRUCT_SIZE = 12

class WindowsDisk:
    """Utility class for representing a windows disk.  uses windows API to do
        IO operations."""
    
    def __init__(self, disk_path):
        """get bootsector and disk size from filehandle"""
        self.disk_path = disk_path
        
        #test if this is a phyiscal drive path
        if(re.match(r'\\\\\.\\[A-Z]:', disk_path.upper(), re.I) or 
            re.match(r'\\\\\.\\PHYSICALDRIVE', disk_path.upper(), re.I)):
            self.file_handle = self._open_disk()
            self.device_number = self._get_device_number()
            self.close_disk()
            
            #reopen disk as physical drive
            device_num = self.device_number["DeviceNumber"]
            self.disk_path = r'\\.\\PHYSICALDRIVE%d' % device_num
            self.file_handle = self._open_disk()
            self.disk_geometry_ex = self._get_drive_geometry_ex()
            self.sector_size = self.disk_geometry_ex["BytesPerSector"]
            self.size = self.disk_geometry_ex["DiskSize"]
        else:
            #regular file is simpler
            self.file_handle = self._open_disk()
            self.sector_size = 512
            self.size = self._get_file_size()
        self.bootsector = self.read_data(self.get_sector_size())
        if(self.get_sector_size() > 512):
            self.bootsector = self.bootsector[0:512]
        
    def _get_file_size(self):
        """use winapi to get file size"""
        filesize = ctypes.wintypes.LARGE_INTEGER(0) 
        if(not K32DLL.GetFileSizeEx(self.file_handle, ctypes.byref(filesize))):
            raise IOError("GetFileSizeEx failed!")
        return filesize.value
    
    def close_disk(self):
        """use winapi to close disk handle"""
        if(not K32DLL.CloseHandle(self.file_handle)):
            raise IOError("CloseHandle failed!")

    def _open_disk(self):
        """use winapi to open disk handle"""
        file_handle = K32DLL.CreateFileA(self.disk_path, GENERIC_READ | GENERIC_WRITE, 
            FILE_SHARE_READ | FILE_SHARE_WRITE, 
            0, OPEN_EXISTING, 0, 0)
        if(file_handle == INVALID_HANDLE_VALUE):
            raise IOError("device open failed!")
        return file_handle
        
    def _get_drive_geometry_ex(self):
        """use winapi to get drive geometry info"""
        bytesread = ctypes.wintypes.DWORD()
        data = ctypes.create_string_buffer('\000' * DISK_GEOMETRY_EX_STRUCT_SIZE)
        result = K32DLL.DeviceIoControl(self.file_handle, 
            IOCTL_DISK_GET_DRIVE_GEOMETRY_EX, 0, 0, 
            data, DISK_GEOMETRY_EX_STRUCT_SIZE, ctypes.byref(bytesread), 0)
        
        if(not result):
            raise IOError("DeviceIoControl failed!")
        
        #DISK_GEOMETRY_EX
        #8  LARGE_INTEGER Cylinders
        #4  MEDIA_TYPE    MediaType
        #4  ULONG         TracksPerCylinder
        #4  ULONG         SectorsPerTrack
        #4  ULONG         BytesPerSector
        #8  LARGE_INTEGER DiskSize

        disk_geometry_ex = {}
        disk_geometry_ex["Cylinders"] = struct.unpack_from('q', data, 0)[0]
        disk_geometry_ex["MediaType"] = struct.unpack_from('l', data, 8)[0]
        disk_geometry_ex["TracksPerCylinder"] = struct.unpack_from('l', data, 12)[0]
        disk_geometry_ex["SectorsPerTrack"] = struct.unpack_from('l', data, 16)[0]
        disk_geometry_ex["BytesPerSector"] = struct.unpack_from('l', data, 20)[0]
        disk_geometry_ex["DiskSize"] = struct.unpack_from('q', data, 24)[0]
        
        return disk_geometry_ex
        
    def _get_device_number(self):
        """use winapi to device number and partition number"""
        bytesread = ctypes.wintypes.DWORD()
        data = ctypes.create_string_buffer('\000' * STORAGE_DEVICE_NUMBER_STRUCT_SIZE)
        result = K32DLL.DeviceIoControl(self.file_handle, 
            IOCTL_STORAGE_GET_DEVICE_NUMBER, 0, 0, 
            data, STORAGE_DEVICE_NUMBER_STRUCT_SIZE, ctypes.byref(bytesread), 0)
        if(not result):
            raise IOError("DeviceIoControl failed!")
        
        #STORAGE_DEVICE_NUMBER
        #DEVICE_TYPE DeviceType
        #ULONG       DeviceNumber
        #ULONG       PartitionNumber
        device_number = {}
        device_number["DeviceType"] = struct.unpack_from('l', data, 0)[0]
        device_number["DeviceNumber"] = struct.unpack_from('l', data, 4)[0]
        device_number["PartitionNumber"] = struct.unpack_from('l', data, 8)[0]
        
        return device_number
        
    def _seek(self, offset):
        """use winapi to go to a specified position"""
        pos = ctypes.wintypes.LARGE_INTEGER(offset) 
        result = K32DLL.SetFilePointerEx(self.file_handle, pos, 0, FILE_BEGIN)
        if(not result):
            raise IOError("SetFilePointerEx failed!")
            
    def _read(self, size):
        """use winapi to read data from a file handle"""
        data = ctypes.create_string_buffer('\000' * size)
        bytesread = ctypes.wintypes.DWORD()
        result = K32DLL.ReadFile(self.file_handle, data, size, 
            ctypes.byref(bytesread), 0)
        if(not result):
            raise IOError("ReadFile failed!")
            
        read_data = data.raw[0:bytesread.value]
        return read_data
        
    def _write(self, write_data):
        """use winapi to write data to a file handle"""
        data = ctypes.create_string_buffer(write_data)
        byteswritten = ctypes.wintypes.DWORD()
        result = K32DLL.WriteFile(self.file_handle, data, len(write_data), 
            ctypes.byref(byteswritten), 0)
        if(not result):
            raise IOError("WriteFile failed!")
        
    def get_sector_size(self):
        """returns sector size"""
        return self.sector_size
        
    def get_num_sectors(self):
        """get disk size in sectors"""
        return self.size / self.sector_size

    def write_data(self, data, offset = 0):
        """write data to disk"""
        if(len(data) % self.sector_size != 0): 
            raise Exception("writes must be in %d byte chunks" % self.sector_size)
        self._seek(offset)
        self._write(data)
        
    def read_data(self, size, offset = 0):
        """read data from disk"""
        if(size % self.sector_size != 0): 
            raise Exception("reads must be in %d byte chunks" % self.sector_size)
        self._seek(offset)
        return self._read(size)
    
class Disk:
    """Utility class for representing a disk"""
    SECTOR_SIZE = 512
    
    def __init__(self, file_handle, size=None):
        """get bootsector and disk size from filehandle"""
        self.file_handle = file_handle
        self.bootsector = self.read_data(self.get_sector_size())
        if(size):
            self.size = size
        else:
            file_handle.seek(0, 2) # move the cursor to the end of the file
            self.size = file_handle.tell()
        
    def get_sector_size(self):
        """returns sector size which is always 512 for this script"""
        return self.SECTOR_SIZE

    def get_num_sectors(self):
        """get disk size in sectors"""
        return self.size / self.SECTOR_SIZE
        
    def write_data(self, data, offset = 0):
        """write data to disk"""
        if(len(data) % self.SECTOR_SIZE != 0): 
            raise Exception("writes must be in %d byte chunks" % self.SECTOR_SIZE)
        self.file_handle.seek(offset)
        self.file_handle.write(data)
        
    def read_data(self, size, offset = 0):
        """read data from disk"""
        if(size % self.SECTOR_SIZE != 0): 
            raise Exception("reads must be in %d byte chunks" % self.SECTOR_SIZE)
        self.file_handle.seek(offset)
        return self.file_handle.read(size)
        
    def verify_data(self, data, offset = 0):
        """read data from disk make check if it matches input data"""
        self.file_handle.seek(offset)
        new_data = self.file_handle.read(len(data))
        return new_data == data
    
#pylint does not need to be so strict for unit tests
#pylint: disable=C0111, W0232, R0904
class TestDisk(unittest.TestCase):
    """Unit tests for Disk class"""
    DISK_SIZE = 2048
    TEST_STRING = 'hello'
    
    @classmethod
    def create_dummy_disk(cls):
        """create a fake disk"""
        empty_disk = BootDiskTestImageFactory.create_disk_from_str(cls.TEST_STRING, cls.DISK_SIZE)
        file_handle = StringIO.StringIO(empty_disk)
        disk = Disk(file_handle)
        
        return disk
    
    def test_basic_disk(self):
        """test basic disk class methods"""
        disk = TestDisk.create_dummy_disk()
        self.assertEqual(disk.bootsector[0:5], self.TEST_STRING)
        self.assertEqual(self.DISK_SIZE, disk.size)
        
        self.assertEqual(disk.get_sector_size(), 512)
        self.assertEqual(disk.get_num_sectors(), 4)
        
class BootDiskTestImageFactory:
    """Factory class for creating disk images.  partition tables are in hex and
       converted to binary"""
    @staticmethod
    def hex_to_str(data):
        """convert a string of hex values to binary"""
        tmp_str = data
        tmp_str = re.sub(r'\s+', '', tmp_str)
        return tmp_str.decode("hex")
        
    @staticmethod
    def create_disk_from_str(input_str, size):
        """"creates a disk object from a string"""
        disk_str = input_str + (' ' * (size - len(input_str)))
        return disk_str
        
    @classmethod
    def create_basic_disk(cls):
        BASIC_DISK_SIZE = 32 * 1024 * 1024
        BASIC_BOOT_SECTOR_HEX = (' 00 ' * (27*16) ) + \
        """00 00 00 00 00 00 00 00 2B 88 F1 E4 00 00 00 61
        22 00 0B ED 2B 02 00 18 00 00 00 A0 00 00 00 ED
        2C 02 83 14 10 04 00 B8 00 00 00 48 00 00 00 20
        21 00 A2 61 21 00 00 08 00 00 00 10 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 AA"""
        
        bootsector = cls.hex_to_str(BASIC_BOOT_SECTOR_HEX)
        disk_str = cls.create_disk_from_str(bootsector, BASIC_DISK_SIZE)
        file_handle = StringIO.StringIO(disk_str)
        disk = Disk(file_handle)
        return disk
        
    @classmethod
    def create_basic_disk_with_no_a2(cls):
        BASIC_DISK_SIZE = 32 * 1024 * 1024
        BASIC_BOOT_SECTOR_HEX = (' 00 ' * (27*16) ) + \
        """00 00 00 00 00 00 00 00 2B 88 F1 E4 00 00 00 61
        22 00 0B ED 2B 02 00 18 00 00 00 A0 00 00 00 ED
        2C 02 83 14 10 04 00 B8 00 00 00 48 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 AA"""
        
        bootsector = cls.hex_to_str(BASIC_BOOT_SECTOR_HEX)
        disk_str = cls.create_disk_from_str(bootsector, BASIC_DISK_SIZE)
        file_handle = StringIO.StringIO(disk_str)
        disk = Disk(file_handle)
        return disk
        
    @classmethod
    def create_basic_disk_multi_a2(cls):
        BASIC_DISK_SIZE = 32 * 1024 * 1024
        BASIC_BOOT_SECTOR_HEX = (' 00 ' * (27*16) ) + \
        """00 00 00 00 00 00 00 00 2B 88 F1 E4 00 00 00 61
        22 00 0B ED 2B 02 00 18 00 00 00 A0 00 00 00 ED
        2C 02 A2 14 10 04 00 B8 00 00 00 48 00 00 00 20
        21 00 A2 61 21 00 00 08 00 00 00 10 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 AA"""
        
        bootsector = cls.hex_to_str(BASIC_BOOT_SECTOR_HEX)
        disk_str = cls.create_disk_from_str(bootsector, BASIC_DISK_SIZE)
        file_handle = StringIO.StringIO(disk_str)
        disk = Disk(file_handle)
        return disk
        
    @classmethod
    def create_large_disk(cls):
        #small hack to save memory
        #BASIC_DISK_SIZE = 2147483648
        BASIC_DISK_SIZE = 32 * 1024 * 1024
        BASIC_BOOT_SECTOR_HEX = (' 00 ' * (27*16) ) + \
        """00 00 00 00 00 00 00 00 3B 81 59 40 00 00 00 12
        0F 84 0B 80 2C EC 00 60 20 00 98 99 19 00 00 E3
        24 00 83 6E 2B 83 00 38 00 00 00 00 20 00 00 20
        21 00 A2 41 01 00 00 08 00 00 00 08 00 00 00 00
        00 00 00 00 00 00 00 00 00 00 00 00 00 00 55 AA"""
        
        bootsector = cls.hex_to_str(BASIC_BOOT_SECTOR_HEX)
        disk_str = cls.create_disk_from_str(bootsector, BASIC_DISK_SIZE)
        file_handle = StringIO.StringIO(disk_str)
        disk = Disk(file_handle, 2147483648)
        return disk
#pylint: enable=C0111, W0232, R0904
        
class PartitionTable:
    """This class parses a partition table from the disk object"""
    
    ###contants for PC partition table
    FIRST_PARTITION_OFFSET = 446
    PARTITION_SIZE = 16
    NUM_PARTITIONS = 4
    
    def __init__(self, disk):
        """read in partition table from disk and process it"""
        self.disk = disk
        
        if(len(disk.bootsector) != 512): 
            raise BootDiskUtilError("Invalid partition table")
        
        #check for magic number in boot sector
        if(disk.bootsector[510] != chr(0x55) or disk.bootsector[511] != chr(0xAA)):
            raise BootDiskUtilError("Invalid partition table")
            
        self.partition_data = []
        
        for i in range(self.NUM_PARTITIONS):
            partition_entry = dict()
            begin = self.FIRST_PARTITION_OFFSET + self.PARTITION_SIZE * i
            end = begin + self.PARTITION_SIZE
            raw_part = disk.bootsector[begin:end]
            partition_entry["raw_data"] = raw_part
            partition_entry["number"] = i + 1
            self.process_raw_partition(partition_entry)
            self.partition_data += [partition_entry]
            
        self.get_a2_partition()
            
    def process_raw_partition(self, part_entry):
        """process 16 byte partition table entry and get the data that is relavant
           which emptiness, type, and size"""
        raw_data = part_entry["raw_data"]
        if(raw_data == (chr(0) * 16)):
            part_entry["empty"] = True 
        else:
            part_entry["empty"] = False
            part_entry["type"] = ord(raw_data[4])
            
            part_entry["start_sector"] = struct.unpack('I', raw_data[8:12])[0]
            part_entry["num_sectors"] = struct.unpack('I', raw_data[12:16])[0]
            part_entry["end_sector"] = part_entry["start_sector"] + part_entry["num_sectors"] - 1
            
            if(part_entry["end_sector"] > self.disk.get_num_sectors()):
                raise BootDiskUtilError("Invalid partition table - disk size mismatch")
                
    def get_a2_partition(self):
        """find the a2 partition, also make sure there is only 1 and that it is 
           large enough to fit a preloader image"""
        a2_entry = None
        for part_entry in self.partition_data:
            if(not part_entry["empty"] and part_entry["type"] == 0xa2):
                if(a2_entry):
                    raise BootDiskUtilError("multiple 0xa2 partitions found!")
                a2_entry = part_entry
                
        if(not a2_entry):
            raise BootDiskUtilError("0xa2 partition not found!")
                
        #make sure a2 partition is big enough
        MINIMUM_A2_SECTORS = AlteraBootPartitionUtility.PRELOADER_SIZE/self.disk.get_sector_size()
        if(a2_entry["num_sectors"] < MINIMUM_A2_SECTORS):
            raise BootDiskUtilError("0xa2 partition is smaller than 256K!")
                
        return a2_entry
            
    def raw_partition_dump(self):
        """unitity for dumping raw partition data"""
        for part_entry in self.partition_data:
            raw_part = part_entry["raw_data"]
            print "Partition %i: %i %s\n" % (part_entry["number"], len(raw_part), map(hex, map(ord, raw_part)))
        
#pylint does not need to be so strict for unit tests
#pylint: disable=C0111, R0904
class TestPartitionTable(unittest.TestCase):
    """Unit tests for PartitionTable class"""
    
    def test_basic_disk(self):
        disk = BootDiskTestImageFactory.create_basic_disk()
        part_table = PartitionTable(disk)
        
        self.assertFalse(part_table.partition_data[0]["empty"])
        self.assertFalse(part_table.partition_data[1]["empty"])
        self.assertFalse(part_table.partition_data[2]["empty"])
        self.assertTrue(part_table.partition_data[3]["empty"])
        
        self.assertEqual(hex(part_table.partition_data[0]["type"]), '0xb')
        self.assertEqual(hex(part_table.partition_data[1]["type"]), '0x83')
        self.assertEqual(hex(part_table.partition_data[2]["type"]), '0xa2')
        
        self.assertEqual(part_table.partition_data[0]["start_sector"], 6144)
        self.assertEqual(part_table.partition_data[0]["end_sector"], 47103)
        
        self.assertEqual(part_table.partition_data[1]["start_sector"], 47104)
        self.assertEqual(part_table.partition_data[1]["end_sector"], 65535)
        
        self.assertEqual(part_table.partition_data[2]["start_sector"], 2048)
        self.assertEqual(part_table.partition_data[2]["end_sector"], 6143)

    def test_invalid_mbr(self):
        disk = TestDisk.create_dummy_disk()
        with self.assertRaisesRegexp(BootDiskUtilError, "Invalid partition table"):
            PartitionTable(disk)

    def tests_a2_partition_too_small(self):
        disk = BootDiskTestImageFactory.create_basic_disk()
        
        part_table = PartitionTable(disk)
        a2_part = part_table.get_a2_partition()
        
        a2_part["num_sectors"] = 511
        a2_part["end_sector"] = a2_part["start_sector"] + a2_part["num_sectors"] - 1
        
        with self.assertRaisesRegexp(BootDiskUtilError, "0xa2 partition is smaller than 256K!"):
            #should fail this time because it is too small
            a2_part = part_table.get_a2_partition()

    def test_missing_a2_partition(self):
        disk = BootDiskTestImageFactory.create_basic_disk_with_no_a2()
        with self.assertRaisesRegexp(BootDiskUtilError, "0xa2 partition not found!"):
            PartitionTable(disk)
            
    def test_multi_a2_partition(self):
        disk = BootDiskTestImageFactory.create_basic_disk_multi_a2()
        with self.assertRaisesRegexp(BootDiskUtilError, "multiple 0xa2 partitions found!"):
            PartitionTable(disk)
            
    def test_bad_partition_size(self):
        disk = BootDiskTestImageFactory.create_large_disk()
        disk.size = 32 * 1024 * 1024
        with self.assertRaisesRegexp(BootDiskUtilError, "Invalid partition table - disk size mismatch"):
            PartitionTable(disk)
            
    def test_large_disk(self):
        disk = BootDiskTestImageFactory.create_large_disk()
        part_table = PartitionTable(disk)
        
        self.assertFalse(part_table.partition_data[0]["empty"])
        self.assertFalse(part_table.partition_data[1]["empty"])
        self.assertFalse(part_table.partition_data[2]["empty"])
        self.assertTrue(part_table.partition_data[3]["empty"])
        
        self.assertEqual(hex(part_table.partition_data[0]["type"]), '0xb')
        self.assertEqual(hex(part_table.partition_data[1]["type"]), '0x83')
        self.assertEqual(hex(part_table.partition_data[2]["type"]), '0xa2')
        
        self.assertEqual(part_table.partition_data[0]["start_sector"], 2121728)
        self.assertEqual(part_table.partition_data[0]["end_sector"], 3799447)
        
        self.assertEqual(part_table.partition_data[1]["start_sector"], 14336)
        self.assertEqual(part_table.partition_data[1]["end_sector"], 2111487)
        
        self.assertEqual(part_table.partition_data[2]["start_sector"], 2048)
        self.assertEqual(part_table.partition_data[2]["end_sector"], 4095)
#pylint: enable=C0111, R0904

class AlteraBootPartitionUtility:
    """utility class for writing to altera boot partition"""
    
    #preloader is fixed at 256KB in cyclone V
    PRELOADER_SIZE = 64 * 1024 * 4
    A10BOOTLOADER_SIZE = 256 * 1024 * 4
    
    def __init__(self, part_table):
        self.part_table = part_table
        self.disk = part_table.disk
        self.a2_part = part_table.get_a2_partition()
        
        self.a2_byte_offset = self.a2_part["start_sector"] * self.disk.get_sector_size()
        self.a2_part_size = self.a2_part["num_sectors"] * self.disk.get_sector_size()
        
    def write_preloader(self, preloader_data):
        """write the preloader to the 0xa2 partition"""
        if(len(preloader_data) > self.PRELOADER_SIZE):
            raise BootDiskUtilError("Preloader is too big")
            
        self.disk.write_data(preloader_data, self.a2_byte_offset)
            
    def write_a10bootloader(self, preloader_data):
        """write the a10 bootloader to the 0xa2 partition"""
        if(len(preloader_data) > self.A10BOOTLOADER_SIZE):
            raise BootDiskUtilError("Arria10 bootloader is too big")
            
        self.disk.write_data(preloader_data, self.a2_byte_offset)

    def write_bootloader(self, bootloader_data):
        """write the bootload/uboot to the 0xa2 partition"""
        #need to add sector padding for windows
        sector_alignment = len(bootloader_data) % self.disk.get_sector_size()
        if(sector_alignment > 0):
            padding = self.disk.get_sector_size() - sector_alignment
            bootloader_data = bootloader_data +  chr(0) * padding

        if(len(bootloader_data) > self.a2_part_size - self.PRELOADER_SIZE):
            raise BootDiskUtilError("bootloader is too big for a2 partition")
            
        self.disk.write_data(bootloader_data, self.a2_byte_offset+self.PRELOADER_SIZE)
            
#pylint does not need to be so strict for unit tests
#pylint: disable=C0111, R0904
class TestAlteraBootPartitionUtility(unittest.TestCase):
    """Unit tests for AlteraBootPartitionUtility class"""
    def test_preloader_write(self):
        disk = BootDiskTestImageFactory.create_basic_disk()
        
        part_table = PartitionTable(disk)
        boot_util_obj = AlteraBootPartitionUtility(part_table)
        
        self.assertEqual(boot_util_obj.a2_byte_offset, 2048*512)
        self.assertEqual(boot_util_obj.a2_part_size, 4096*512)
        
        preloader_data = ('start' + chr(0) * (boot_util_obj.PRELOADER_SIZE - 8) + 'end')
        boot_util_obj.write_preloader(preloader_data)
        self.assertTrue(boot_util_obj.disk.verify_data(preloader_data, boot_util_obj.a2_byte_offset))
        
    def test_oversize_preloader_write(self):
        disk = BootDiskTestImageFactory.create_basic_disk()
        
        part_table = PartitionTable(disk)
        boot_util_obj = AlteraBootPartitionUtility(part_table)
        
        preloader_data = ('start' + chr(0) * (boot_util_obj.PRELOADER_SIZE - 8+1) + 'end')
        with self.assertRaisesRegexp(BootDiskUtilError, "Preloader is too big"):
            boot_util_obj.write_preloader(preloader_data)
            
    def test_bootloader_write(self):
        disk = BootDiskTestImageFactory.create_basic_disk()
        
        part_table = PartitionTable(disk)
        boot_util_obj = AlteraBootPartitionUtility(part_table)
        
        bootloader_size = boot_util_obj.a2_part_size - boot_util_obj.PRELOADER_SIZE
        bootloader_data = ('start' + chr(0) * (bootloader_size - 8) + 'end')
        boot_util_obj.write_bootloader(bootloader_data)
        self.assertTrue(boot_util_obj.disk.verify_data(bootloader_data, boot_util_obj.a2_byte_offset+boot_util_obj.PRELOADER_SIZE))
        
    def test_oversize_bootloader_write(self):
        disk = BootDiskTestImageFactory.create_basic_disk()
        
        part_table = PartitionTable(disk)
        boot_util_obj = AlteraBootPartitionUtility(part_table)
        
        bootloader_size = boot_util_obj.a2_part_size - boot_util_obj.PRELOADER_SIZE
        bootloader_data = ('start' + chr(0) * (bootloader_size - 8+1) + 'end')
        with self.assertRaisesRegexp(BootDiskUtilError, "bootloader is too big for a2 partition"):
            boot_util_obj.write_bootloader(bootloader_data)
            
    def test_odd_sized_bootloader_write(self):
        """tests writing a bootloader that is not 512 byte aligned.  
           writing disks in windows requires 512 byte alignment"""
        disk = BootDiskTestImageFactory.create_basic_disk()
        
        part_table = PartitionTable(disk)
        boot_util_obj = AlteraBootPartitionUtility(part_table)
        
        bootloader_size = (boot_util_obj.a2_part_size - boot_util_obj.PRELOADER_SIZE)-1
        bootloader_data = ('start' + chr(0) * (bootloader_size - 8) + 'end')
        boot_util_obj.write_bootloader(bootloader_data)
        self.assertTrue(boot_util_obj.disk.verify_data(bootloader_data, boot_util_obj.a2_byte_offset+boot_util_obj.PRELOADER_SIZE))
#pylint: enable=C0111, R0904
        
def parse_options():
    """parse command line options and valid them"""
    if(os.name == 'nt'):
        windows_help_info = '#write BOOTloader and PREloader to disk drive \'E\'\n' +\
            '    alt-boot-disk-util -p preloader -b bootloader -a write -d E \n\n'
    else:
        windows_help_info = ""
        
    parser = optparse.OptionParser(usage=
         '\n#write preloader to disk\n' +\
         '    alt-boot-disk-util -p preloader -a write disk_file\n\n' +\
         '#write bootloader to disk\n' +\
         '    alt-boot-disk-util -b bootloader -a write disk_file\n\n' +\
         '#write BOOTloader and PREloader to disk\n' +\
         '    alt-boot-disk-util -p preloader -b bootloader -a write disk_file\n\n' +\
         '#write Arria10 Bootloader to disk\n' +\
         '    alt-boot-disk-util -B a10bootloader -a write disk_file\n\n' +\
         windows_help_info,
                                          version=__version__)

    parser.add_option("-b", "--bootloader", dest="bootloader", default=None,
        help="bootloader image file' ", metavar="FILE")
    
    parser.add_option("-p", "--preloader", dest="preloader", default=None,
        help="preloader image file' ", metavar="FILE")
    
    parser.add_option("-a", "--action", dest="action", default=None,
        help="only supports 'write' action' ", metavar="ACTION")
    
    parser.add_option("-B", "--a10-bootloader", dest="a10bootloader", default=None,
        help="arria10 bootloader image file", metavar="FILE")
    
    #add drive letter option for windows only
    if(os.name == 'nt'):
        parser.add_option("-d", "--drive", dest="drive", default=None,
            help="specify disk drive letter to write to", metavar="DRIVE")
    
    (options, args) = parser.parse_args()
    
    #validate drive letter if that is specified
    if(os.name == 'nt' and options.drive):
        if(len(args) > 0):
            raise BootDiskUtilError(
                "options error: drive letter and disk image specified.  " +\
                "Please choose one or the other!")
        if(not re.match(r'^[A-Z]$', options.drive.upper(), re.I)):
            raise BootDiskUtilError("options error: invalid drive letter!")
        args = [r'\\.\%s:' % options.drive.upper()]
    
    if(len(args) != 1):
        parser.print_help()
        raise BootDiskUtilError("options error: disk not specified!")
    
    if(not options.action):
        parser.print_help()
        raise BootDiskUtilError("options error: ACTION not specified!")
        
    if(options.action.lower() != 'write'):
        parser.print_help()
        raise BootDiskUtilError("options error: ACTION not %s, not supported!" % options.action)
        
    if((not options.bootloader and not options.preloader and not options.a10bootloader)):
        parser.print_help()
        raise BootDiskUtilError("options error: need to specify a bootloader, a preloader, or a arria10 bootloader!")

    if(options.a10bootloader and (options.bootloader or options.preloader)):
        parser.print_help()
        raise BootDiskUtilError("cannot specifiy arria10 bootloader with bootloader or preloader!")

        
    return (options, args)
        
def script_main():
    """main entry point for the script"""
    
    print "Altera Boot Disk Utility"
    print "Copyright (C) 1991-2014 Altera Corporation\n"
    
    #get command line options and validate them
    (options, args) = parse_options()
    disk_path = args[0]
    
    #load preloader and/or bootloader file
    preloader_data = None
    if(options.preloader):
        with open(options.preloader, 'rb') as file_handle:
            preloader_data = file_handle.read()
            
    bootloader_data = None
    if(options.bootloader):
        with open(options.bootloader, 'rb') as file_handle:
            bootloader_data = file_handle.read()

    a10bootloader_data = None
    if(options.a10bootloader):
        with open(options.a10bootloader, 'rb') as file_handle:
            a10bootloader_data = file_handle.read()

    #open disk image and perform the operations that the user requested
    #check for windows and use special WindowsDisk class
    if(os.name == 'nt'):
        disk = WindowsDisk(disk_path)
    else:
        file_handle = open(disk_path, 'r+b')
        disk = Disk(file_handle)
            
    part_table = PartitionTable(disk)
    boot_util_obj = AlteraBootPartitionUtility(part_table)
    
    if(preloader_data):
        boot_util_obj.write_preloader(preloader_data)
        
    if(bootloader_data):
        boot_util_obj.write_bootloader(bootloader_data)
        
    if(a10bootloader_data):
        boot_util_obj.write_a10bootloader(a10bootloader_data)
        
    if(os.name == 'nt'):
        disk.close_disk()
    else:
        file_handle.close()

    print "Altera Boot Disk Utility was successful."
    return 0

def main():
    """execute main and clean up exception handling"""
    try:
        result = script_main()
    except Exception, err:
        print str(err)
        result = 1
    sys.exit(result)

if __name__ == '__main__':
    main()

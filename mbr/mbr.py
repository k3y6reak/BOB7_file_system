# -*- coding:utf-8 -*-
import struct
import sys

def parsing2(data, cur_lba, save_lba):
    record = data[cur_lba:cur_lba+512]
    record = record[446:]
    idx = 0
    while idx < 32:
        bootcode = record[idx].encode("hex")
        chs1 = record[idx+1:idx+1+3].encode("hex")
        partition_type = int(record[idx+1+3:idx+1+3+1].encode("hex"))
        chs2 = record[idx+1+3+1:idx+1+3+1+3].encode("hex")
        lba = struct.unpack_from("<I", record[idx+1+3+1+3:idx+1+3+1+3+4])[0]*512
        size = record[idx+1+3+1+3+4:idx+1+3+1+3+4+4].encode("hex")

        print "==================="
        print "bootcode: ", bootcode
        print "chs1: ", chs1
        print "partition type: ", partition_type
        print "chs2: ", chs2
        if (partition_type == 7):
            print "LBA: ", cur_lba + lba
        else:
            print "LBA: ", lba + save_lba
        print "size: ", size
        idx+=16

        if partition_type == 5:
            parsing2(data, lba+save_lba, save_lba)

def parsing(data):
    record = data[446:512]
    idx = 0
    while idx < 64:
        bootcode = record[idx].encode("hex")
        chs1 = record[idx+1:idx+1+3].encode("hex")
        partition_type = int(record[idx+1+3:idx+1+3+1].encode("hex"))
        chs2 = record[idx+1+3+1:idx+1+3+1+3].encode("hex")
        lba = struct.unpack_from("<I", record[idx+1+3+1+3:idx+1+3+1+3+4])[0]*512
        size = record[idx+1+3+1+3+4:idx+1+3+1+3+4+4].encode("hex")

        print "==================="
        print "bootcode: ", bootcode
        print "chs1: ", chs1
        print "partition type: ", partition_type
        print "chs2: ", chs2
        print "LBA: ", lba
        print "size: ", size
        idx+=16
        if partition_type == 5:
            parsing2(data, lba, lba)

def load(image):
    f = open(image, 'rb')
    data = f.read()
    parsing(data)
    f.close()

def main(image):
    load(image)

if __name__ == '__main__':
    main(sys.argv[1])

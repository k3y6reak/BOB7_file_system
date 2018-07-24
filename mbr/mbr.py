import struct
import sys

PART_TYPE_EBR = 5
PART_TYPE_NTFS = 7
BOOT_INST_OFFSET = 446
MBR_SIZE = 512
CHS1_OFFSET = 1
PART_TYPE_OFFSET = CHS1_OFFSET + 3
CHS2_OFFSET = PART_TYPE_OFFSET + 1
LBA_OFFSET = CHS2_OFFSET + 3
SIZE_OFFSET = LBA_OFFSET + 4
EBR_SIZE = 512
UNUSED_DATA_SIZE = 446
NUM_OF_PART_ENTRY_SIZE_MBR = 64
NUM_OF_PART_ENTRY_SIZE_EBR = 32

def get_data(record, idx, cur_lba=0, save_lba_for_ebr=0):
    bootcode = record[idx].encode("hex")
    chs1 = record[idx+CHS1_OFFSET:idx+PART_TYPE_OFFSET].encode("hex")
    partition_type = int(record[idx+PART_TYPE_OFFSET:idx+CHS2_OFFSET].encode("hex"))
    chs2 = record[idx+CHS2_OFFSET:idx+LBA_OFFSET].encode("hex")
    lba = struct.unpack_from("<I", record[idx+LBA_OFFSET:idx+SIZE_OFFSET])[0]*512
    size = record[idx+SIZE_OFFSET:idx+SIZE_OFFSET+4].encode("hex")

    print "==================="
    print "bootcode: ", bootcode
    print "chs1: ", chs1
    print "partition type: ", partition_type
    print "chs2: ", chs2
    if (partition_type == PART_TYPE_NTFS):
        print "LBA: ", cur_lba + lba
    else:
        print "LBA: ", lba + save_lba_for_ebr
    print "size: ", size
    return lba, partition_type

def parsing2(data, cur_lba, save_lba_for_ebr):
    record = data[cur_lba:cur_lba+EBR_SIZE]
    record = record[UNUSED_DATA_SIZE:]
    idx = 0
    while idx < NUM_OF_PART_ENTRY_SIZE_EBR:
        lba, partition_type = get_data(record, idx, cur_lba, save_lba_for_ebr)
        idx+=16

        if partition_type == PART_TYPE_EBR:
            parsing2(data, lba+save_lba_for_ebr, save_lba_for_ebr)

def parsing(data):
    record = data[BOOT_INST_OFFSET:MBR_SIZE]
    idx = 0
    while idx < NUM_OF_PART_ENTRY_SIZE_MBR:
        lba, partition_type = get_data(record, idx)
        idx+=16

        if partition_type == PART_TYPE_EBR:
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

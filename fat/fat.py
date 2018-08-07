from sys import argv
from binascii import hexlify, unhexlify
from struct import pack, unpack

BOOT_SECTOR_SIZE = 512
JUMP_BOOT_CODE_OFFSET = 0
OEM_NAME_OFFSET = JUMP_BOOT_CODE_OFFSET + 3
BYTE_PER_SECTOR_OFFSET = OEM_NAME_OFFSET + 8
SECTOR_PER_CLUSTER_OFFSET = BYTE_PER_SECTOR_OFFSET + 2
RESV_SECTOR_OFFSET = SECTOR_PER_CLUSTER_OFFSET + 1
NUM_OF_FAT_OFFSET = RESV_SECTOR_OFFSET + 2
ROOT_ENTRY_OFFSET = NUM_OF_FAT_OFFSET + 1
TOTAL_SECTOR16_OFFSET = ROOT_ENTRY_OFFSET + 2
MEDIA_OFFSET = TOTAL_SECTOR16_OFFSET + 2
FAT_SIZE16_OFFSET = MEDIA_OFFSET + 1
SECTOR_PER_TRACK_OFFSET = FAT_SIZE16_OFFSET + 2
NUM_OF_HEAD_OFFSET = SECTOR_PER_TRACK_OFFSET + 2
HIDDEN_SECTOR_OFFSET = NUM_OF_HEAD_OFFSET + 2
TOTAL_SECTOR32_OFFSET = HIDDEN_SECTOR_OFFSET + 4
FAT_SIZE32_OFFSET = TOTAL_SECTOR32_OFFSET + 4
EXT_FLAG_OFFSET = FAT_SIZE32_OFFSET + 4

SFN_NAME_OFFSET = 0
SFN_EXT_OFFSET = SFN_NAME_OFFSET + 8
ATTR_TYPE_OFFSET = SFN_EXT_OFFSET + 3
RESERVED_OFFSET = ATTR_TYPE_OFFSET + 1
CREATE_TIME_10MS_OFFSET = RESERVED_OFFSET + 1
CREATE_TIME_OFFSET = CREATE_TIME_10MS_OFFSET + 1
CREATE_DATE_OFFSET = CREATE_TIME_OFFSET + 2
ACCESS_DATE_OFFSET = CREATE_DATE_OFFSET + 2
HIGH_CLUSTER_OFFSET = ACCESS_DATE_OFFSET + 2
UPDATE_TIME_OFFSET = HIGH_CLUSTER_OFFSET + 2
UPDATE_DATE_OFFSET = UPDATE_TIME_OFFSET + 2
LOW_CLUSTER_OFFSET = UPDATE_DATE_OFFSET + 2
FILE_SIZE_OFFSET = LOW_CLUSTER_OFFSET + 2

LFN_NAME_OFFSET = 1
LFN_FIRST_NAME_OFFSET = LFN_NAME_OFFSET
LFN_ATTR_TYPE_OFFSET = LFN_FIRST_NAME_OFFSET + 10
LFN_RESERVED_OFFSET = LFN_ATTR_TYPE_OFFSET + 1
CHK_SFN_OFFSET = LFN_RESERVED_OFFSET + 1
LFN_SECOND_NAME_OFFSET = CHK_SFN_OFFSET + 1
LFN_CLUSTER_OFFSET = LFN_SECOND_NAME_OFFSET + 12
LFN_THIRD_NAME_OFFSET = LFN_CLUSTER_OFFSET + 2

LFN_FLAG= 0x0F
READ_ONLY_FLAG = 0x01
HIDDEN_FLAG = 0x02
SYSTEM_FLAG = 0x04
VOLUME_LABEL_FLAG = 0x08
DIR_FLAG = 0x10
ARCHIVE_FLAG = 0x20
ERASED = 0xE5

def attribute_check(attribute):
    print "\t",
    if attribute == READ_ONLY_FLAG:
        print "READ ONLY",
    elif attribute == HIDDEN_FLAG:
        print "HIDDEN",
    elif attribute == SYSTEM_FLAG:
        print "SYSTEM",
    elif attribute == VOLUME_LABEL_FLAG:
        print "VOLUM LABEL",
    elif attribute == DIR_FLAG:
        print "DIRECTORY",
    elif attribute == ARCHIVE_FLAG:
        print "FILE",
    else:
        print "NONE",

def file_dir_parsing(data):
    idx = 0
    file_name = []
    while True:
        dir_entry = data[idx:idx+32]
        flag = unpack("<B", dir_entry[0])[0]

        if flag == 0x00:
            exit(0)

        attribute = unpack("<B", dir_entry[ATTR_TYPE_OFFSET:RESERVED_OFFSET])[0]

        CHK_LFN = False
        if attribute == LFN_FLAG:
            if (flag & 0xF0) == 0x40:
                lfn_idx = (flag & 0x0F)
                while lfn_idx >= 1:
                    dir_entry = data[idx:idx+32]

                    file3 = hexlify(dir_entry[LFN_FIRST_NAME_OFFSET:LFN_ATTR_TYPE_OFFSET]).decode("hex").decode("utf-16-le", errors='replace')
                    file2 = hexlify(dir_entry[LFN_SECOND_NAME_OFFSET:LFN_CLUSTER_OFFSET]).decode("hex").decode("utf-16-le", errors='replace')
                    file1 = hexlify(dir_entry[LFN_THIRD_NAME_OFFSET:LFN_THIRD_NAME_OFFSET+4]).decode("hex").decode("utf-16-le", errors='replace')
                    file_name.append(file1)
                    file_name.append(file2)
                    file_name.append(file3)

                    if lfn_idx == 1:
                        print_file_name = ""
                        for n in reversed(file_name):
                            print_file_name += n
                        print print_file_name,
                        file_name = []

                    lfn_idx-=1
                    idx+=32
                    CHK_LFN = True

        else:
            if flag == ERASED:
                print "[X]",

            print hexlify(dir_entry[SFN_NAME_OFFSET:SFN_EXT_OFFSET]).decode("hex").decode("euc-kr", errors='replace'),
            print "."+hexlify(dir_entry[SFN_EXT_OFFSET:ATTR_TYPE_OFFSET]).decode("hex").decode("euc-kr", errors='replace'),
            attribute_check(attribute)
            print "\t", unpack("<I", dir_entry[FILE_SIZE_OFFSET:FILE_SIZE_OFFSET+4])[0], "bytes"

            CHK_LFN = False
        print "\n"

        if CHK_LFN == True:
            continue
        else:
            idx+=32

def parsing(data):
    boot_sector = data[:BOOT_SECTOR_SIZE]
    byte_per_sector = unpack("<H", data[BYTE_PER_SECTOR_OFFSET:SECTOR_PER_CLUSTER_OFFSET])[0]
    root_entry_num = unpack("<H", data[ROOT_ENTRY_OFFSET:TOTAL_SECTOR16_OFFSET])[0]
    fat_size32 = unpack("<I", data[FAT_SIZE32_OFFSET:EXT_FLAG_OFFSET])[0]
    reserved_sector_count = unpack("<H", data[RESV_SECTOR_OFFSET:NUM_OF_FAT_OFFSET])[0]
    num_of_fat = unpack("<B", data[NUM_OF_FAT_OFFSET:ROOT_ENTRY_OFFSET])[0]
    sector_per_cluster = unpack("<B", data[SECTOR_PER_CLUSTER_OFFSET:RESV_SECTOR_OFFSET])[0]

    root_dir_sector = (root_entry_num * 32 + (byte_per_sector - 1)) / byte_per_sector
    first_data_sector = reserved_sector_count + fat_size32 * num_of_fat + root_dir_sector
    cluster = 2
    cluster_to_sector = ((cluster-2)*sector_per_cluster + first_data_sector) * 512
    file_dir_parsing(data[cluster_to_sector:])

def load(image):
    f = open(image, 'rb')
    data = f.read()
    parsing(data)
    f.close()

def main(image):
    load(image)

if __name__ == '__main__':
    main(argv[1])

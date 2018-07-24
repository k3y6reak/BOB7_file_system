import struct
import sys

MBR_HDR_SIZE = 512
GPT_HDR_SIZE = 512
NUM_OF_PART_OFFSET = 80
PART_SIZE = 128
START_LBA_OFFSET = 32

def parsing(gpt):
    gpt_header = gpt[:GPT_HDR_SIZE]
    num_of_partitions = struct.unpack_from("<I", gpt_header[NUM_OF_PART_OFFSET:NUM_OF_PART_OFFSET+4])[0]
    partition_info = gpt[GPT_HDR_SIZE:num_of_partitions*PART_SIZE]

    idx = 0
    part_idx = 0
    while(idx < num_of_partitions):
        guid_for_partition = partition_info[part_idx:part_idx+16]
        guid_sum = 0
        for i in guid_for_partition:
            guid_sum += struct.unpack_from("<b", i)[0]

        if guid_sum == 0:
            exit(0)
        else:
            print "Real Offset","[",idx,"]:", struct.unpack_from("<q", partition_info[part_idx+START_LBA_OFFSET:part_idx+START_LBA_OFFSET+8])[0]*512
        part_idx+=128
        idx += 1

def load(image):
    f = open(image, 'rb')
    data = f.read()
    gpt = data[MBR_HDR_SIZE:]
    parsing(gpt)
    f.close()

def main(image):
    init()
    load(image)

if __name__ == '__main__':
    main(sys.argv[1])

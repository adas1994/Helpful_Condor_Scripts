import os, sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('src_dir', help='source directory where root files are situated')
parser.add_argument('file_list', help='name of the file where to put the list')
parser.add_argument('put_dir', default=None, help='directory')

args = parser.parse_args()
src_dir = args.src_dir
file_list = args.file_list
put_dir = args.put_dir


def make_and_put_list(src_dir, file_list, put_dir=None):
    if put_dir is not None:
        assert os.path.exists(put_dir)
    else:
        put_dir = os.getcwd()
    print("putting the file list text in this directory : ",put_dir)
    file_path = os.path.join(put_dir, file_list)
    assert os.path.exists(src_dir)
    raw_file_list = os.listdir(src_dir)
    rootfile_fullpathlist = []
    n = len(raw_file_list)
    for i in range(n):
        raw_path = raw_file_list[i]
        if raw_path.endswith('.root'):
            full_path = os.path.join(src_dir, raw_path)
            rootfile_fullpathlist.append(full_path)
    fin_name = os.path.join(put_dir, file_list)
    fin = open(fin_name, "w")
    for ifile in rootfile_fullpathlist:
        fin.write(ifile+'\n')

    fin.close()


make_and_put_list(src_dir, file_list, put_dir)

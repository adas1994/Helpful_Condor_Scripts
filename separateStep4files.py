import os, sys
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('src_dir', help='source directory where root files are situated')
parser.add_argument('DQMfile_list', help='name of the file where to put the list of DQM Files')
parser.add_argument('DQM_inDQMfile_list', help='name of the file where to put the list of DQM_inDQM Files')
parser.add_argument('put_dir', default=None, help='directory')

args = parser.parse_args()
src_dir = args.src_dir
DQM_file_list = args.DQMfile_list
DQM_inDQM_file_list = args.DQM_inDQMfile_list
put_dir = args.put_dir


def make_and_put_list(src_dir, DQM_inDQM_file_list, DQM_file_list, put_dir=None):
    if put_dir is not None:
        assert os.path.exists(put_dir)
    else:
        put_dir = os.getcwd()
    print("putting the file list text in this directory : ",put_dir)
    DQM_file_path = os.path.join(put_dir, DQM_file_list)
    DQM_inDQM_file_path = os.path.join(put_dir, DQM_inDQM_file_list)
    assert os.path.exists(src_dir)
    raw_file_list = os.listdir(src_dir)
    DQM_inDQM_rootfile_fullpathlist = []
    DQM_rootfile_fullpathlist = []
    n = len(raw_file_list)
    for i in range(n):
        raw_path = raw_file_list[i]
        if raw_path.endswith('.root'):
            full_path = os.path.join(src_dir, raw_path)
            if 'inDQM' in raw_path:
                DQM_inDQM_rootfile_fullpathlist.append(full_path)
            else:
                DQM_rootfile_fullpathlist.append(full_path)
    

    fin_DQM_inDQM = open(DQM_inDQM_file_path, "w")
    for ifile in DQM_inDQM_rootfile_fullpathlist:
        fin_DQM_inDQM.write(ifile+'\n')
    fin_DQM_inDQM.close()

    fin_DQM = open(DQM_file_path, "w")
    for ifile in DQM_rootfile_fullpathlist:
        fin_DQM.write(ifile+'\n')
    fin_DQM.close()

make_and_put_list(src_dir, DQM_inDQM_file_list, DQM_file_list, put_dir)

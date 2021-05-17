#!/usr/bin/env python

import os, sys
import shutil
import subprocess, shlex
import re
import argparse

"""
finding executable example
import distutils.spawn
distutils.spawn.find_executable(cmsRun)
'/cvmfs/cms-ib.cern.ch/week0/slc7_amd64_gcc820/cms/cmssw/CMSSW_11_1_X_2020-03-06-1100/bin/slc7_amd64_gcc820/cmsRun'
"""
parser = argparse.ArgumentParser()


parser.add_argument("proxypath", help="path of the proxyfile")
parser.add_argument("cmssw_base", help="cmssw base")
parser.add_argument("cmssw_holder_dir", help="cmssw holder dir")
parser.add_argument("configfile", help="config file to run")
parser.add_argument("files_list", help="text file containing list of gensim files")
parser.add_argument("idx_primary", type=int, help="numeric index of the gensim file to be used")
parser.add_argument("storage_dir", help="diresctory for storing output root file")
parser.add_argument("geometry", type=int, help="detector version, 35 or 41")
parser.add_argument("premix_method", help="old or new premix_method")


args = parser.parse_args()

proxypath        = args.proxypath
cmssw_base       = args.cmssw_base
cmssw_holder_dir = args.cmssw_holder_dir
configfile       = args.configfile
files_list       = args.files_list
idx_primary      = args.idx_primary
storage_dir      = args.storage_dir
geometry         = args.geometry
premix_method    = args.premix_method

def modify_and_cmsRun_config_file(configfile, files_list, idx_primary):
    fin = open(files_list, "r")
    gensim_file = fin.readlines()[idx_primary]
    gensim_file =  gensim_file.rstrip('\n')[7:]
    gensim_file = 'root://deepthought.crc.nd.edu/'+gensim_file
    gensim_file =  gensim_file
    if geometry==41:
        gensim_file = gensim_file
    if geometry==35:
        gensim_file = 'root://cms-xrd-global.cern.ch//store/user/abhd1994/SerViceWork/SmallBx/StandardMix/TTbar_14TeV_TuneCUETP8M1_cfi_GEN_SIM.root'
    print("Got Primary Dataset File as : ",gensim_file)
    
    rep = {'step2_SIM.root' : gensim_file}
    rep = dict((re.escape(k), v) for k, v in rep.iteritems())
    pattern = re.compile("|".join(rep.keys()))
    CMSSW_holder_dir = cmssw_holder_dir
    CMSSW_BASE = cmssw_base
    tarfile = CMSSW_BASE +'.tar.gz'
    src_cmd = "source /cvmfs/cms.cern.ch/cmsset_default.csh"
    src_cmd_args = shlex.split(src_cmd)
    ps1 = subprocess.Popen(src_cmd_args, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    ps1_out, ps1_err = ps1.communicate()
    print(ps1_out, ps1_err)
    cmssw_full_path = os.path.join(CMSSW_holder_dir, CMSSW_BASE)
    zipping_cmd = 'tar --exclude-caches-all --exclude-vcs -zcf ' +tarfile +' -C '+ cmssw_full_path +'/.. '+ CMSSW_BASE +' --exclude=tmp --exclude="*.root"  --exclude="*.jdl"'
    
    os.system(zipping_cmd)
    unzipping_cmd = "tar -xf "+tarfile
    os.system(unzipping_cmd)
    os.environ["X509_USER_PROXY"] = proxypath
    os.system("voms-proxy-info -all")
    os.system("voms-proxy-info -all -file "+proxypath)
    configfile_path = CMSSW_BASE+"/src/StandardMix/"+configfile
    configfile_torun =  open(configfile_path, "r")
    substitute_file_path  = CMSSW_BASE+"/src/StandardMix/substitute.py"
    substitute_file = open(substitute_file_path, "w")
    
    for line in configfile_torun:
        modified_text = pattern.sub(lambda m: rep[re.escape(m.group(0))], line)
        substitute_file.write(modified_text)
            
    configfile_torun.close()
    substitute_file.close()
    repl_cmd = "mv "+substitute_file_path+" "+configfile_path
    os.system(repl_cmd)
    os.chdir(os.path.join(CMSSW_BASE, "src"))
    print("Current dirctory is ----  ",os.getcwd())
    project_rename_cmd = "scramv1 b ProjectRename"
    os.system(project_rename_cmd)
    os.system("./Standard_step2_helper.csh "+storage_dir+" "+str(idx_primary))
    print("cmsRun job done, data stored")
    print("current directory is ",os.getcwd())
#modify_and_cmsRun_config_file("step3_DIGI_DATAMIX_L1_L1TrackTrigger_DIGI2RAW_HLT.py", "/afs/crc.nd.edu/user/a/adas/Orchid/gensimfiles_fullpath.txt", 33, 237)
modify_and_cmsRun_config_file(configfile, files_list, idx_primary)



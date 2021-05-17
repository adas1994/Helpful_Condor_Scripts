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
parser.add_argument("idx_primary", type=int, help="numeric index of the gensim file to be used")
parser.add_argument("storage_dir", help="diresctory for storing output root file")
parser.add_argument("geometry", type=int, help="detector version, 35 or 41")
parser.add_argument("gensimsample", help="photon or ttbar or singlePi")


args = parser.parse_args()

proxypath        = args.proxypath
cmssw_base       = args.cmssw_base
cmssw_holder_dir = args.cmssw_holder_dir
configfile       = args.configfile
idx_primary      = args.idx_primary
storage_dir      = args.storage_dir
geometry         = args.geometry
gensimsample     = args.gensimsample

def modify_and_cmsRun_config_file(configfile, idx_primary):
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
    print("--- printing zipping command : ",zipping_cmd)
    print(".....")
    os.system(zipping_cmd)
    unzipping_cmd = "tar -xf "+tarfile
    os.system(unzipping_cmd)
    os.environ["X509_USER_PROXY"] = proxypath
    os.system("voms-proxy-info -all")
    os.system("voms-proxy-info -all -file "+proxypath)
    configfile_path = CMSSW_BASE+"/src/PreMix/"+configfile
    
    os.chdir(os.path.join(CMSSW_BASE, "src"))
    print("Current dirctory is ----  ",os.getcwd())
    project_rename_cmd = "scramv1 b ProjectRename"
    os.system(project_rename_cmd)
    os.system("./gensim_helper.csh "+storage_dir+" "+str(idx_primary) +" "+gensimsample)
    print("cmsRun job done, data stored")
    print("current directory is ",os.getcwd())
#modify_and_cmsRun_config_file("step3_DIGI_DATAMIX_L1_L1TrackTrigger_DIGI2RAW_HLT.py", "/afs/crc.nd.edu/user/a/adas/Orchid/gensimfiles_fullpath.txt", 33, 237)
modify_and_cmsRun_config_file(configfile, idx_primary)

# tar --exclude-caches-all --exclude-vcs -zcf CMSSW_11_0_X_2020-03-18-2300.tar.gz /afs/crc.nd.edu/user/a/adas/ServiceWork/CMSSW_11_0_X_2020-03-18-2300/.. CMSSW_11_0_X_2020-03-18-2300 --exclude=tmp --exclude="*.root" --exclude="*.jdl"

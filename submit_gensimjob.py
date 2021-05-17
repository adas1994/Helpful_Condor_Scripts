#!/usr/bin/env python
import os, sys
import shutil
import argparse
import datetime
import fnmatch
from socket import gethostname
import re

parser = argparse.ArgumentParser()
parser.add_argument("numjobs", metavar='n', type=int, help="number of jobs to be submitted")
parser.add_argument("qsubscript", metavar='q', help="condor script name")
parser.add_argument("geom", metavar='g', type=int, help="geometry;35/41")
parser.add_argument("gensimsample", metavar='s', help="photon, ttbar, singlePi, singleK0_L")
args = parser.parse_args()

geom      = args.geom
njobs     = args.numjobs
qsubname  = args.qsubscript
gensimsample = args.gensimsample

if geom==35:
    storage_base_dir = "/hadoop/store/user/adas/New_storeD35"
elif geom==41:
    storage_base_dir = "/hadoop/store/user/adas/New_storeD41"


if not os.path.exists(storage_base_dir):
    print("Storage base directory ",storage_base_dir ," doesn't exist !!!")
    print("Creating new directory... ",storage_base_dir)
    os.mkdir(storage_base_dir)

base_dir        = os.path.dirname(os.path.abspath(__file__))
CMSSW_BASE      = "CMSSW_11_1_0_pre8"
executable_name = "gensim_driver.py"
tar_command     = 'tar --exclude-caches-all --exclude-vcs -zcf '+CMSSW_BASE+'.tar.gz -C '+ CMSSW_BASE+'/.. '+CMSSW_BASE+'  --exclude=tmp --exclude="*.jdl" --exclude="*.root"'
p_path          = os.path.join(base_dir, "x509up_u230413")



def submit_jobs(njobs, qsub_scriptname, dirname = None):
    if dirname == None:
        dirname = base_dir
    full_qsubscript_path = os.path.join(dirname, qsub_scriptname)
    assert os.path.exists(full_qsubscript_path)
    x = datetime.datetime.now()
    print(x)
    timestamp = x.strftime("%Y")+"_"+x.strftime("%m")+"_"+x.strftime("%d")+"_"+x.strftime("%H")+"_"+x.strftime("%M")+"_"+x.strftime("%S")
    temporary_workdir = os.path.join(dirname, timestamp)
    os.mkdir(temporary_workdir)
    storage_dir = os.path.join(storage_base_dir, timestamp+"_"+gensimsample)
    os.mkdir(storage_dir)
    
    fout_path_list = []
    for i in range(njobs):
        executable_filepath = os.path.join(dirname, executable_name)
        rep = {}
        rep["executable_name"] = executable_name 
        rep["job_number"]      =  str(i)
        rep["executable_path"] = executable_filepath
        if gensimsample == "photon":
            rep["configfile"]      = "SinglePhotonPt5_Vtx0_LEta_26D41.py"
        elif gensimsample == "ttbar":
            rep["configfile"]      = "TTbar_14TeV_TuneCP5_cfi_GEN_SIM.py"
        elif gensimsample == "singlePi":
            rep["configfile"]      = "SinglePiPt25Eta1p7_2p7_cfi_GEN_SIM.py"
        elif gensimsample == "singleK0_L":
            rep["configfile"]      = "SingleK0_L_Pt5_Vtx0_LEta_26D41.py"
        else:
            raise NotImplementedError("wrong gensimsample; type photon or ttbar or singlePi")
        rep["storage_dir"]     = storage_dir
        rep["CMSSW_BASE"]      = CMSSW_BASE
        rep["base_dir"]        = base_dir
        rep["generic_ppath"]   = p_path
        rep["geom"]            = str(geom)
        rep["timestamp"]       = temporary_workdir
        rep["gensimsample"]    = gensimsample
        rep = dict((re.escape(k), v) for k, v in rep.iteritems())
        pattern = re.compile("|".join(rep.keys()))
        fin = open(full_qsubscript_path, "r")
        fin_initial = qsub_scriptname[:-4]
        fout_name =fin_initial+str(i)+".jdl"
        fout_path = os.path.join(temporary_workdir, fout_name)
        fout = open(fout_path, "w")
        for line in fin:
            #print(fout_path)
            modified_text = pattern.sub(lambda m: rep[re.escape(m.group(0))], line)
            fout.write(modified_text)
        fout.close()
        fout_path_list.append(fout_path)
        
        fin.close()
        qsub_cmd = "condor_submit "+fout_path
        os.system(qsub_cmd)


submit_jobs(njobs, qsubname)

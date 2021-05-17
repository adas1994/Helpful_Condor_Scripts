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
parser.add_argument("pm", help="old or new premix method")
parser.add_argument("data_tag", help = "any special tag you wanna add to the output rootfiles")
parser.add_argument("directory_tag", help = "any tag for the directory where the output rootfiles will be saved")
args = parser.parse_args()

geom      = args.geom
pm        = args.pm
njobs     = args.numjobs
qsubname  = args.qsubscript
data_tag  = args.data_tag
directory_tag = args.directory_tag
outdir_name = "HGCTimingValidation_"+directory_tag
storage_base_dir = ""
if geom==35 and pm=='old':
    storage_base_dir = "/hadoop/store/user/adas/New_storeD35/PreMixOld/"+outdir_name
elif geom==35 and pm=='new':
    storage_base_dir = "/hadoop/store/user/adas/New_storeD35/PreMixNew/"+outdir_name
elif geom==41 and pm=='old':
    storage_base_dir = "/hadoop/store/user/adas/New_storeD41/PreMixOld/"+outdir_name
elif geom==41 and pm=='new':
    storage_base_dir = "/hadoop/store/user/adas/New_storeD41/PreMixNew/"+outdir_name

print("-------- ",storage_base_dir)
if (storage_base_dir is not "") and (not os.path.exists(storage_base_dir)):
    print("Storage base directory ",storage_base_dir ," doesn't exist !!!")
    print("Creating new directory... ",storage_base_dir)
    os.mkdir(storage_base_dir)

base_dir        = os.path.dirname(os.path.abspath(__file__))
CMSSW_BASE      = "CMSSW_11_1_0_pre8"
executable_name = "HGCTValidation_driver.py"
tar_command     = 'tar --exclude-caches-all --exclude-vcs -zcf '+CMSSW_BASE+' -C '+ CMSSW_BASE+'/.. '+CMSSW_BASE+'  --exclude=tmp --exclude="*.jdl" --exclude="*.root"'
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
    storage_dir = os.path.join(storage_base_dir, timestamp)
    os.mkdir(storage_dir)
    
    fout_path_list = []
    for i in range(njobs):
        executable_filepath = os.path.join(dirname, executable_name)
        rep = {}
        rep["executable_name"] = executable_name 
        rep["job_number"]      =  str(i)
        rep["executable_path"] = executable_filepath
        rep["file_listpath"]   = os.path.join(base_dir, "filesfor_PreMixHGCTimingValidation.txt")
        rep["configfile"]      = "part_Time_template.py"
        rep["storage_dir"]     = storage_dir
        rep["CMSSW_BASE"]      = CMSSW_BASE
        rep["base_dir"]        = base_dir
        rep["generic_ppath"]   = p_path
        rep["geom"]            = str(geom)
        rep["pm"]              = pm
        rep["timestamp"]       = temporary_workdir
        rep["data_tag"]        = data_tag
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

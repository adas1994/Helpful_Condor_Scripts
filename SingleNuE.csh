#!/bin/csh


setenv SUBMISSION_TIME date
echo "Starting Job on " $SUBMISSION_TIME #`date`
echo "Running on : `uname -a`"
echo "System Software: `cat /etc/redhat-release`"
#echo $(Cluster)_$(Process)
setenv X509_USER_PROXY $1
voms-proxy-info -all
voms-proxy-info -all -file $1
source /cvmfs/cms.cern.ch/cmsset_default.csh
xrdcp -s $3 .
setenv cms_release_tar "$2.tar.gz"
echo ${cms_release_tar}
tar -xf ${cms_release_tar}
rm ${cms_release_tar}
setenv SCRAM_ARCH slc7_amd64_gcc700
cd $2/src/
scramv1 b ProjectRename
eval `scramv1 runtime -csh`
scram b USER_CXXFLAGS="-g" -j 15
cd PreMix/
echo "Entered the PreMix directory"
echo `ls -ltr`
cmsRun SingleNuE10_cfi_GEN_SIM_DIGI_PU.py
#mkdir /hadoop/store/user/adas/store_code/PreMixNew/$(Cluster)_$(Process)_SUBMISSION_TIME
#SingleNuE10_cfi_GEN_SIM_DIGI_PU.root
xrdcp SingleNuE10_cfi_GEN_SIM_DIGI_PU.root $5/SingleNuE10_cfi_GEN_SIM_DIGI_PU$4.root
#mkdir /hadoop/store/user/adas/store_code/PreMixNew/$SUBMISSION_TIME
rm *.root
cd ${_CONDOR_SCRATCH_DIR}
rm -rf $2

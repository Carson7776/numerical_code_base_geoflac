# -S /bin/sh
#PBS -q batch
#PBS -o stdout.$PBS_JOBID
#PBS -e stderr.$PBS_JOBID
#PBS -V
#PBS -q q25g2
#PBS -N GRm
#PBS -l nodes=1:ppn=2

export OMP_NUM_THREADS=2  # same as ppn

cd $PBS_O_WORKDIR
cp $PBS_NODEFILE nodelist.$PBS_JOBID

###coping input &submit file to geoflac_modified_input_and_submit_file
cp submit.sh /home/humaorong/geoflac_modified_input_and_submit/geoflac_modified_v00/GRm**_r**
cp subduction.inp /home/humaorong/geoflac_modified_input_and_submit/geoflac_modified_v00/GRm**_r**

D=/home/humaorong/geoflac_modified

### Recording state of the code
cp $D/src/snapshot.diff .

### Recording starting time
echo $(date)>logtime.txt

### Execute the model
$D/src/flac subduction.inp
#cp _contents.save _contents.rs
#$D/src/flac subduction2.inp

### Recording ending time
echo $(date)>>logtime.txt

### Convert model results
python3 $D/util/flac2vtk.py ./
python3 $D/util/flacmarker2vtk.py ./
#draw force time relation graph
python3 $D/util/draw_froc_time.py ./
#draw diagram
python3 $D/util/draw_diagram.py ./
#draw topo time graph

# ~~~~ submit command ~~~~
# qsub < [script]




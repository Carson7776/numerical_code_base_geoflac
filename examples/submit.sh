# -S /bin/sh
#PBS -q batch
#PBS -o stdout.$PBS_JOBID
#PBS -e stderr.$PBS_JOBID
#PBS -V
#PBS -q q25g2
#PBS -N model_name
#PBS -l nodes=1:ppn=4

export OMP_NUM_THREADS=4  # same as ppn

cd $PBS_O_WORKDIR
#cp $PBS_NODEFILE nodelist.$PBS_JOBID

# compute node to use fixed local libraries
export PYTHONPATH=$HOME/.local/lib/python3.6/site-packages:$PYTHONPATH

### coping input & submit file to geoflac_modified_input_and_submit_file
base_path="/home/humaorong/geoflac_modified_input_and_submit/geoflac_modified_v00"
save_path="${base_path}/${PBS_JOBNAME}"

mkdir -p "$save_path"
cp submit.sh subduction.inp "$save_path"

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
python3 $D/util/draw_diagram_linux.py ./ 
python3 $D/util/draw_video.py ./ 2>&1 #merge errors to stdout
#python3 $D/util/draw_froc_time.py ./ #fix and add python path error
# ~~~~ submit command ~~~~
# qsub < [script]

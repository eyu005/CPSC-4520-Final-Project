#!/usr/bin/env bash
#
#SBATCH --job-name=sugarscape
#SBATCH --array=0-899              # 900 seeds: 0 through 899
#SBATCH --output=slurm_logs/sugarscape_%A_%a.out
#SBATCH --error=slurm_logs/sugarscape_%A_%a.err
#SBATCH --time=05:00:00            # 5 hour per seed
#SBATCH --mem=2G                   # 2 GB RAM per job
#SBATCH --cpus-per-task=1
#SBATCH --partition=cpu       # or whichever Delta partition you use
#SBATCH --account=besx-delta-cpu


# Create output directories
mkdir -p ~/sugarscape/slurm_jsons ~/sugarscape/sugarscape_out ~/sugarscape/slurm_logs 

#define decision models array 
DECISION_MODELS=("altruistBinary" "altruistTop" "benthamBinary" "benthamTop" "egoistBinary" 
                "egoistTop" "negativeBentham" "none" "rawSugarscape")

#Calculate seed and model from job array index 
SEED=$((SLURM_ARRAY_TASK_ID % 100))
MODEL_IDX=$((SLURM_ARRAY_TASK_ID / 100))
MODEL_NAME=${DECISION_MODELS[$MODEL_IDX]}

mkdir -p ~/sugarscape/slurm_jsons/${MODEL_NAME}

TEMPLATE_JSON=~/sugarscape/baseline_10000.json
JOB_JSON=~/sugarscape/slurm_jsons/${MODEL_NAME}/config_${MODEL_NAME}_seed${SEED}.json

mkdir -p ~/sugarscape/sugarscape_out/${MODEL_NAME}

OUTPUT_PATH=~/sugarscape/sugarscape_out/${MODEL_NAME}/seed${SEED}.json

# Create job-specific configuration
python3 -c "
import json
with open('$TEMPLATE_JSON') as f: config = json.load(f)
config['sugarscapeOptions']['seed'] = $SEED
config['sugarscapeOptions']['agentDecision4Models'] = ['$MODEL_NAME']
config['sugarscapeOptions']['logfile'] = '$OUTPUT_PATH'
config['sugarscapeOptions']['logfileFormat'] = 'json'
with open('$JOB_JSON', 'w') as f: json.dump(config, f, indent=2)
print('Created config for model: $MODEL_NAME, seed: $SEED')
"

# Check if config was created successfully
if [[ ! -f "$JOB_JSON" ]]; then
    echo "ERROR: Failed to create config file"
    exit 1
fi

# Run the simulation
python3 ~/sugarscape/sugarscape.py --conf "$JOB_JSON"

# Check if simulation completed successfully
if [[ $? -ne 0 ]]; then
    echo "ERROR: Simulation failed"
    exit 1
fi

# Verify output file was created
if [[ ! -f "$OUTPUT_PATH" ]]; then
    echo "ERROR: Output file not found at $OUTPUT_PATH"
    exit 1
else
    echo "Output saved to $OUTPUT_PATH"
fi

# Clean up temporary config
rm "$JOB_JSON"

echo "Completed: Model=${MODEL_NAME}, Seed=${SEED}"
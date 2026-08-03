import argparse
import logging
import sys
import numpy as np
from pathlib import Path

# ==========================================
# CLUSTER SAFE MATPLOTLIB SETUP
# ==========================================
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==========================================
# CONFIGURATION
# ==========================================
DEFAULT_DATA_DIR = "/scratch2/humaorong"
DEFAULT_OUT_DIR = "/scratch2/humaorong/data_analysis/all_model_forc/result"

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def load_all_forc_data(master_directory: str, file_pattern: str = "forc.0", allowed_prefixes: tuple = None, target_numbers: list = None) -> dict:
    """
    Scan a directory for specific files and load them as NumPy arrays.
    Skip files that do not match the specified prefixes or target numbers.
    """
    master_path = Path(master_directory).resolve()
    data_collection = {}

    if not master_path.exists() or not master_path.is_dir():
        logging.error(f"Invalid or missing directory: {master_directory}")
        return data_collection

    logging.info(f"Scanning {master_directory} for '{file_pattern}'...\n")
    
    for file_path in master_path.rglob(file_pattern):
        model_name = file_path.parent.name
        
        # Filter by prefix (e.g., GRm)
        if allowed_prefixes and not model_name.startswith(allowed_prefixes):
            continue
            
        # Filter by target model numbers
        if target_numbers and not any(str(num) in model_name for num in target_numbers):
            continue
        
        try:
            data_collection[model_name] = np.loadtxt(file_path)
            logging.info(f"Loaded: {model_name: <25} | Shape: {data_collection[model_name].shape}")
        except Exception as e:
            logging.warning(f"Failed to load {file_path}. Error: {e}")

    logging.info(f"Finished! Successfully loaded {len(data_collection)} targeted files.")
    
    return data_collection


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Load and plot FORC simulation data.")
    
    parser.add_argument("--data_dir", type=str, default=DEFAULT_DATA_DIR)
    parser.add_argument("--pattern", type=str, default="forc.0")
    parser.add_argument("--prefixes", nargs='+', default=[], help="Filter folders by prefixes")
    parser.add_argument("--out_dir", type=str, default=DEFAULT_OUT_DIR)
    parser.add_argument("--models", nargs='+', default=[], help="Specific model numbers to plot")
    
    return parser.parse_args()


def plot_and_save_data(data_collection: dict, output_dir: str):
    """Generate and save a PNG figure for each loaded model."""
    out_path = Path(output_dir).resolve()
    out_path.mkdir(parents=True, exist_ok=True)
    logging.info(f"Saving figures to: {out_path}\n")

    for model_name, data_array in data_collection.items():
        fig, ax = plt.subplots(figsize=(8, 6))
        
        # Extract X and Y data columns
        x_data = data_array[:, 0]
        y_data = data_array[:, 1]
        
        ax.plot(x_data, y_data, color='blue', linewidth=1.5, label=model_name)
        ax.set_title(f"Force Analysis: {model_name}")
        ax.set_xlabel("Time / Step")
        ax.set_ylabel("Force Value")
        ax.grid(True, linestyle='--')
        ax.legend()
        
        save_name = out_path / f"{model_name}_forc_plot.png"
        fig.savefig(save_name, dpi=300, bbox_inches='tight')
        plt.close(fig)
        
        logging.info(f"Saved: {save_name.name}")


def main():
    args = parse_arguments()
    
    print("-" * 50)
    print("Step 1: Configuration")
    print(f"Target Directory: {args.data_dir}")
    print(f"Output Directory: {args.out_dir}")
    if args.prefixes:
        print(f"Folder Filter   : Must start with {args.prefixes}")
    if args.models:
        print(f"Target Models   : {args.models}")
    print("-" * 50)
    
    print("\nStep 2: Targeted Data Loading...")
    prefixes_tuple = tuple(args.prefixes) if args.prefixes else None
    
    forc_data = load_all_forc_data(
        master_directory=args.data_dir, 
        file_pattern=args.pattern,
        allowed_prefixes=prefixes_tuple,
        target_numbers=args.models  
    )
    
    if not forc_data:
        logging.error("No targeted data found or loaded. Exiting.")
        sys.exit(1)
        
    print("\nStep 3: Plotting and Saving Figures...")
    plot_and_save_data(forc_data, args.out_dir)
    
    print("\nPipeline Completed Successfully!")


if __name__ == "__main__":
    main()
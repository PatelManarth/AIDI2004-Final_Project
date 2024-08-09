import os
import json

def load_paths_config(file_name='paths.json'):
    # Get the absolute path of the project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Construct the path to the JSON configuration file
    config_path = os.path.join(project_dir, file_name)
    
    # Load the configuration file
    with open(config_path, 'r') as f:
        return json.load(f)

def get_full_paths(paths):
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    full_paths = {}
    for key, value in paths.items():
        if isinstance(value, dict):
            full_paths[key] = get_full_paths(value)  # Recursively handle nested dictionaries
        else:
            full_paths[key] = os.path.join(project_dir, value)
    
    return full_paths

# Load paths configuration
paths = load_paths_config()
full_paths = get_full_paths(paths)

# Example usage
if __name__ == "__main__":
    for key, path in full_paths.items():
        print(f"{key}: {path}")

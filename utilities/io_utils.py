import os
import yaml

def create_collection_folder(directory):
    # Check if the folder collection_0000 exists
    base_name = 'collection_0000'
    folder_name = base_name
    folder_path = os.path.join(directory, folder_name)
    
    # If the folder exists, increment the index until an available folder name is found
    index = 1
    while os.path.exists(folder_path):
        folder_name = f'collection_{index:04d}'
        folder_path = os.path.join(directory, folder_name)
        index += 1
    
    # Create the folder
    os.makedirs(folder_path)
    
    # Return the absolute path of the folder
    return os.path.abspath(folder_path)

def read_config(config_path="./inputs/config.yaml"):
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    return config

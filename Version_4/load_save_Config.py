import configparser
import os

CONFIG_FILE = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE):
        try:
            config.read(CONFIG_FILE)
            print("Configuration loaded from config.ini")
        except Exception as e:
            print(f"Error loading config.ini: {e}. Using default settings.")
    else:
        print("config.ini not found. Using default settings.")
    return config

def save_config(config_data):
    config = configparser.ConfigParser()
    config['Settings'] = config_data # Use a section named 'Settings'
    try:
        with open(CONFIG_FILE, 'w') as f:
            config.write(f)
        print("Configuration saved to config.ini")
    except Exception as e:
        print(f"Error saving config.ini: {e}")

#--------------- Test the functions ---------------

if __name__ == '__main__':
    config = load_config()
    print("Loaded config:", config)

    # Modify or add settings
    config_data_to_save = {
        'database_persistent': 'True',
        'quantized_model': 'False',
        'output_length_index': '1',
        'document_number': '3'
    }
    save_config(config_data_to_save)

    loaded_config = load_config()
    print("Reloaded config:", loaded_config['Settings'])
import os
from dotenv import load_dotenv

def get_env(env_var):
    load_dotenv()
    return os.getenv(env_var)

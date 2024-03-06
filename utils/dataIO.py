import json
import os
from typing import Any, Dict, Union
from typing import Optional

class InvalidFileIO(Exception):
    pass

class DataIO:
    def __init__(self):
        pass

    def save_json(self, filename: str, data: Union[Dict[str, Any], list]) -> bool:
        """Save json file and avoid JSON issues.

        Args:
            filename (str): The name of the file to save.
            data (Dict[str, Any] or list): The data to save in json format.

        Returns:
            bool: True if the file was saved successfully, False otherwise.
        """
        rand = randrange(1000, 10000)
        path, ext = os.path.splitext(filename)
        tmp_file = f"{path}-{rand}.tmp"

        if os.path.exists(filename):
            os.remove(filename)

        try:
            self.really_save_json(tmp_file, data)
            self.validate_json(tmp_file)
            os.replace(tmp_file, filename)
            return True
        except (json.decoder.JSONDecodeError, IOError) as e:
            print(f"Error saving json file: {e}")
            self.delete_tmp_file(tmp_file)
            return False

    def load_json(self, filename: str) -> Optional[Union[Dict[str, Any], list]]:
        """Load json file and return the data.

        Args:
            filename (str): The name of the file to load.

        Returns:
            Dict[str, Any] or list

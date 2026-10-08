from pathlib import Path

class DirectoryManager:

    @staticmethod
    def get_csv_files(input_folder):
        """
        Get all CSV files in the input folder.
        """
        return list(input_folder.glob("*.csv"))

    def list_files(self, folder_path, extension=None):
        """
        List all files in the given folder.
        """
        folder = Path(folder_path)
        if extension:
            return [file.name for file in folder.iterdir() if file.is_file() and file.suffix == extension]
        return [file.name for file in folder.iterdir() if file.is_file()]


from pathlib import Path
import csv

class FileManager:

    @staticmethod
    def read_file(file_path):
        """
        Read the content of a file.
        """
        with open(file_path, 'r') as file:
            return file.read()

    def write_file(file_path, content):
        """
        Write content to a file.
        """
        with open(file_path, 'w') as file:
            file.write(content)

    def append_to_file(file_path, content):
        """
        Append content to a file.
        """
        with open(file_path, 'a') as file:
            file.write(content)

    def delete_file(file_path):
        """
        Delete a file.
        """
        Path(file_path).unlink(missing_ok=True)

    def file_exists(file_path):
        """
        Check if a file exists.
        """
        return Path(file_path).exists()

    @staticmethod
    def read_csv(file_path: str | Path, has_header=True):
        with open(file_path, "r", newline="", encoding="utf-8") as file:
            reader = csv.reader(file)

            if has_header:
                header = next(reader, None)
                rows = list(reader)
                return header, rows

            return None, list(reader)


    def save_csv(self, file_path: str, headers: list, data: list[list[str]]):
        """
        Save data to a CSV file.
        """
        with open(file_path, 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file, delimiter=';', quoting=csv.QUOTE_ALL)
            writer.writerow(headers)
            writer.writerows(data)


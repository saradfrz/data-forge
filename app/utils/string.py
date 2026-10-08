import re

class StringUtils:

    @staticmethod
    def replace_multiple_spaces(text):
        return re.sub(r'\s+', ' ', text).strip()

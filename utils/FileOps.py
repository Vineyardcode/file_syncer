import os
import shutil
from utils.FlashMessage import FlashMessage

class FileOps:
    def __init__(self, log_file_path):
        self.flash_message = FlashMessage(log_file_path)

    def copy_file(self, src_file, dst_file):
        shutil.copy2(src_file, dst_file)
        self.flash_message.log("copied", src_file, dst_file)

    def delete_file(self, file_path):
        os.remove(file_path)
        self.flash_message.log("deleted", file_path)

    def create_file(self, src_file, dst_file):
        shutil.copy2(src_file, dst_file)
        self.flash_message.log("created", src_file, dst_file)

import os
import argparse
import time
import hashlib
from utils.FlashMessage import FlashMessage
from utils.FileOps import FileOps

class FolderSync:
    def __init__(self, **kwargs):
        self.flash_message = FlashMessage(kwargs.get("log_file"))
        self.file_ops = FileOps(self.flash_message)
        self.__dict__.update(kwargs)

    def run(self):
        self.flash_message.log("Synchronization started...")
        while True:
            self.synchronize_folders()
            time.sleep(self.sync_interval)

    def calculate_md5(self, file_path):
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()

    def synchronize_folders(self):
        source_files = set(os.listdir(self.source_folder))
        replica_files = set(os.listdir(self.replica_folder))

        for file in source_files - replica_files:
            src_file = os.path.join(self.source_folder, file)
            dst_file = os.path.join(self.replica_folder, file)
            self.file_ops.copy_file(src_file, dst_file)

        for file in replica_files - source_files:
            file_path = os.path.join(self.replica_folder, file)
            self.file_ops.delete_file(file_path)

        for file in source_files.intersection(replica_files):
            src_file = os.path.join(self.source_folder, file)
            dst_file = os.path.join(self.replica_folder, file)

            src_md5 = self.calculate_md5(src_file)
            dst_md5 = self.calculate_md5(dst_file)

            if src_md5 != dst_md5:
                self.file_ops.copy_file(src_file, dst_file)

def main():
    parser = argparse.ArgumentParser(description="One-way folder synchronization")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")

    folder_sync = FolderSync(**vars(parser.parse_args()))
    folder_sync.run()

if __name__ == "__main__":
    main()

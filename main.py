import os
import shutil
import hashlib
import time
import argparse

class FolderSync:
    def __init__(self, source_folder, replica_folder, sync_interval, log_file):
        self.source_folder = source_folder
        self.replica_folder = replica_folder
        self.sync_interval = sync_interval
        self.log_file = log_file

    @staticmethod
    def log(message, log_file):
        with open(log_file, 'a') as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] {message}\n")
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}] {message}")

    @staticmethod
    def compare_and_sync(source_folder, replica_folder, log_file):
        for root, _, files in os.walk(source_folder):
            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(replica_folder, os.path.relpath(src_file, source_folder))

                if not os.path.exists(dst_file) or not FolderSync.compare_files(src_file, dst_file):
                    FolderSync.log(f"Copying {src_file} to {dst_file}", log_file)
                    shutil.copy2(src_file, dst_file)

        for root, _, files in os.walk(replica_folder):
            for file in files:
                dst_file = os.path.join(root, file)
                src_file = os.path.join(source_folder, os.path.relpath(dst_file, replica_folder))

                if not os.path.exists(src_file):
                    FolderSync.log(f"Deleting {dst_file}", log_file)
                    os.remove(dst_file)

    @staticmethod
    def compare_files(file1, file2):
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            return hashlib.md5(f1.read()).hexdigest() == hashlib.md5(f2.read()).hexdigest()

    def sync_folders(self):
        FolderSync.log("Starting synchronization...", self.log_file)
        while True:
            FolderSync.compare_and_sync(self.source_folder, self.replica_folder, self.log_file)
            FolderSync.log("Synchronization complete.", self.log_file)
            time.sleep(self.sync_interval)

def main():
    parser = argparse.ArgumentParser(description="One-way folder synchronization")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")

    args = parser.parse_args()

    folder_sync = FolderSync(args.source_folder, args.replica_folder, args.sync_interval, args.log_file)
    folder_sync.sync_folders()

if __name__ == "__main__":
    main()

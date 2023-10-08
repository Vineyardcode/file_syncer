import os
import argparse
import filecmp
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FlashMessage:
    def __init__(self, log_file_path):
        self.log_file_path = log_file_path
        
    def log(self, message):
        log_message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}"
        print(log_message)
        with open(self.log_file_path, 'a') as log_file:
            log_file.write(log_message + '\n')

class FolderSyncManager:
    def __init__(self, source_folder, replica_folder, flash_message):
        self.source_folder = source_folder
        self.replica_folder = replica_folder
        self.flash_message = flash_message

    def synchronize_folders(self):
        comparison = filecmp.dircmp(self.source_folder, self.replica_folder)
        self.compare_and_sync(comparison)

    def compare_and_sync(self, comparison):
        for file in comparison.left_only:
            src_path = os.path.join(comparison.left, file)
            dst_path = os.path.join(comparison.right, file)
            if os.path.isfile(src_path):
                self.copy_file(src_path, dst_path)
                self.flash_message.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Copied: {src_path} -> {dst_path}")
            elif os.path.isdir(src_path):
                self.copy_directory(src_path, dst_path)
                self.flash_message.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Copied directory: {src_path} -> {dst_path}")

        for file in comparison.right_only:
            file_path = os.path.join(comparison.right, file)
            if os.path.exists(file_path):
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    self.flash_message.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Deleted: {file_path}")
                elif os.path.isdir(file_path):
                    self.remove_directory(file_path)
                    self.flash_message.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Deleted directory: {file_path}")

        for subdir in comparison.common_dirs:
            self.compare_and_sync(comparison.subdirs[subdir])

        for file in comparison.diff_files:
            src_path = os.path.join(comparison.left, file)
            dst_path = os.path.join(comparison.right, file)
            if not self.compare_files(src_path, dst_path):
                self.copy_file(src_path, dst_path)
                self.flash_message.log(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Copied: {src_path} -> {dst_path}")

    def compare_files(self, file1, file2):
        with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
            while True:
                chunk1 = f1.read(4096)
                chunk2 = f2.read(4096)
                if chunk1 != chunk2:
                    return False
                if not chunk1:
                    break
        return True

    def copy_file(self, src, dst):
        with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file:
            while True:
                chunk = src_file.read(4096)
                if not chunk:
                    break
                dst_file.write(chunk)

    def copy_directory(self, src, dst):
        os.makedirs(dst, exist_ok=True)
        for item in os.listdir(src):
            src_item = os.path.join(src, item)
            dst_item = os.path.join(dst, item)
            if os.path.isdir(src_item):
                self.copy_directory(src_item, dst_item)
            else:
                self.copy_file(src_item, dst_item)

    def remove_directory(self, path):
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path):
                self.remove_directory(item_path)
            else:
                os.remove(item_path)
        os.rmdir(path)

class EventHandler(FileSystemEventHandler):
    def __init__(self, sync_manager, sync_interval, flash_message):
        self.sync_manager = sync_manager
        self.sync_interval = sync_interval
        self.last_sync_time = time.time()
        self.flash_message = flash_message
        self.message_list = []

    def on_created(self, event):
        if event.event_type == 'created':
            src_path = event.src_path
            message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Created: {src_path}"
            if message not in self.message_list: 
                self.message_list.append(message)

    def on_deleted(self, event):
        if event.event_type == 'deleted':
            src_path = event.src_path
            message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Deleted: {src_path}"
            if message not in self.message_list: 
                self.message_list.append(message)

    def on_modified(self, event):
        if event.event_type == 'modified':
            src_path = event.src_path
            message = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - Modified: {src_path}"
            if message not in self.message_list: 
                self.message_list.append(message)

    def get_and_clear_messages(self):
        sorted_messages = sorted(self.message_list)
        self.message_list.clear()
        return "\n".join(sorted_messages)

def main():
    parser = argparse.ArgumentParser(description="One-way folder synchronization")
    parser.add_argument("source_folder", help="Path to the source folder")
    parser.add_argument("replica_folder", help="Path to the replica folder")
    parser.add_argument("sync_interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")

    args = parser.parse_args()
     
    flash_message = FlashMessage(log_file_path=args.log_file)
    sync_manager = FolderSyncManager(source_folder=args.source_folder, replica_folder=args.replica_folder, flash_message=flash_message)
    event_handler_source = EventHandler(sync_manager=sync_manager, sync_interval=args.sync_interval, flash_message=flash_message)
    event_handler_replica = EventHandler(sync_manager=sync_manager, sync_interval=args.sync_interval, flash_message=flash_message)

    observer = Observer()
    observer.schedule(event_handler_source, path=args.source_folder, recursive=True)
    observer.schedule(event_handler_replica, path=args.replica_folder, recursive=True)
    
    observer.start()

    flash_message.log("File sync started")
    try:
        while True:
            current_time = time.time()
            if current_time - event_handler_source.last_sync_time >= args.sync_interval:
                
                flash_message.log("-----> LOG NOTES: ")
                flash_message.log(event_handler_source.get_and_clear_messages())
                flash_message.log(event_handler_replica.get_and_clear_messages())
                sync_manager.synchronize_folders()
                event_handler_source.last_sync_time = current_time

            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
    




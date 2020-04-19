#!/usr/bin/env python3

import argparse
import os
import subprocess
import sys
import re
import shutil 

ext_list = ['.azw', '.azw1', '.azw3', '.azw4', '.cbr', '.cbz', '.chm', '.docx', '.epub', '.fb2', '.mobi', '.pdf']


def get_directory_name(filename):
    major, minor = filename.split(' - ', 1)
    major = major.strip()
    return major

class Organizer:

    def __init__(self):
        self.description = "Organize ebook, moving all format of a book to its own folder"
        self.parser = argparse.ArgumentParser(description=self.description)
        self.parser.add_argument("-o", "--output", type=str,
                                 help="Main directory to put organized folders")
        self.parser.add_argument("-n", "--dry_run", action='store_true',
                                 help="Dry run without actually make changes")
        self.parser.add_argument("-d", "--directory", type=str,
                                 help="The directory whose files to classify")
        self.args = self.parser.parse_args()
        
        self.file_list = []
        self.ignored_list = []

        self.total = 0
        self.ignored = 0
        self.organized = 0

        self.run()

    def _handle_file(self, path):
        ext = os.path.splitext(path)[-1].lower()
        print(ext)
        print(ext_list)
        if ext in ext_list:
            self.file_list.append(path)

    def _parse_directory(self):
        for item in os.listdir(self.args.directory):
            item = os.path.join(self.args.directory, item)
            if os.path.isfile(item):
                self._handle_file(item)
                continue
            if os.path.isdir(item):
                continue

    def copyto(self, file, folder):
        print(" -- Copying file to %s" % folder)
        shutil.copy2(file, folder)


    def run(self):
        if not os.path.isdir(self.args.directory):
            print("Error: The input is not a directory")
            return False
        if os.path.exists(self.args.output):
            print("Error: the destination already exists")
            return False

        os.makedirs(self.args.output)

        self._parse_directory()

        if len(self.file_list) == 0:
            print("No file need to be processed")
            return True

        self.total = len(self.file_list)

        for file in self.file_list:
            print('Processing "%s":' % file)
            root, ext = os.path.splitext(file)
            path, base = os.path.split(root)

            folder_name = get_directory_name(base)
            folder_path = os.path.join(self.args.output, folder_name)

            if os.path.exists(folder_path):
                if os.path.isfile(folder_path):
                    print("  -- Error: this name has taken")
                    self.ignored += 1
                    self.ignored_list.append(file)
                    continue
            else:
                os.makedirs(folder_path)
            try: 
                self.copyto(file, folder_path)
            except Exception as e:
                print("  -- Error: Cannot copy file - {} - {}".format(file, str(e)))
                self.ignored += 1
                self.ignored_list.append(file)
            else:
                self.organized += 1
            print("============================\n")

        # statistics
        print("\nProcessed %d files:" % self.total)
        print("  - Organized %d" % self.organized)
        print("  - Ignored %d" % self.ignored)
        print("  - Ignored List: %s" % self.ignored_list)
        return True



def main():
    Organizer()

if __name__ == '__main__':
    sys.exit(main())
import subprocess, sys, os, argparse, re

ext_list = ['.azw', '.azw1', '.azw3', '.azw4', '.cbr', '.cbz', '.chm', '.docx', '.epub', '.fb2', '.mobi', '.txt']

def metadata(file):
    process = subprocess.run(['ebook-meta', file], check=True, stdout=subprocess.PIPE, universal_newlines=True)
    lines = process.stdout.splitlines()
    result = {}
    for line in lines:
        if 'Title' in line:
            key, value = line.split(':', 1)
            result[key.strip(' .')] = value.strip()
        if 'Author(s)' in line:
            key, value = line.split(':', 1)
            value, *junk = value.split('[', 1)
            result[key.strip(' .')] = value.strip()
            break

    print(result)
    return result

def format_filename(s):
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    filename = ''.join(c for c in s if c in valid_chars)
    # filename = filename.replace(' ','_')
    return filename

def remove_ilegal_filename_chars(filename):
    import unicodedata
    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    cleanedFilename = cleanedFilename.decode("utf-8")
    return ''.join(c for c in cleanedFilename if c in validFilenameChars)

def normalize(dic):
    title = dic['Title']
    title = title.replace(':', ' -')
    author = dic['Author(s)']
    author = author.replace(',', '')
    author = author.strip()
    result = title + ' - ' + author
    print(result)
    return result


class Batch(object):

    def __init__(self, args):
        self.file_list = []
        self.skip_subdir = args.skip_subdir
        self.dry_run = args.dry_run
        self.allow_pdf = args.allow_pdf
        self.destination = None

        self.total = 0
        self.renamed = 0
        self.missing = 0
        self.errors = 0

        for f in args.files:
            if os.path.isdir(f):
                self._handle_directory(f)
            if os.path.isfile(f):
                self._handle_file(f)

        if args.destination:
            if os.path.isdir(args.destination):
                print("Error: destination file already exists")
                raise ValueError
            else:
                os.mkdir(args.destination)
                self.destination = args.destination

        if len(self.file_list) == 0:
            print("Error: no file need to be processed")
        return None

    def main(self):
        self.total = len(self.file_list)
        for file in self.file_list:
            root, ext = os.path.splitext(file)
            path, base = os.path.split(root)
            origional_name = base + ext
            print('Processing "%s":' % file)
            result = metadata(file)
            if not result:
                print("  -- Could not find the title of current file: %s skip it..." % file)
                self.missing += 1
                continue
            else:
                new_name = normalize(result) + ext
                if self.destination:
                    ret = subprocess.run(['cp', file, self.destination])
                    if ret.returncode == 0:
                        print("  -- Copying file to destination")
                        path = self.destination
                    else:
                        print("  -- Error copying the file")
                        self.errors += 1
                        continue
                new_name_path = os.path.join(path, new_name)

                print('  -- Renaming to "%s"' % new_name_path)
                if self.dry_run:
                    continue

                try:
                    if self.destination:
                        file = self.destination + '/' + origional_name
                        print(file)
                        print(new_name_path)
                    if os.path.exists(new_name_path):
                        print("  -- same name exists for this file")
                        new_name_path = new_name_path + ".dup"
                    os.rename(file, new_name_path)
                except OSError:
                    print("  -- Error renaming file...")
                    self.errors += 1
                self.renamed += 1
            print("============================\n")

        # statistics
        print("\nProcessed %d files:" % self.total)
        print("  - Renamed %d" % self.renamed)
        print("  - Missing meta %d" % self.missing)
        print("  - Errors %d" % self.errors)
        return True

    def _handle_directory(self, path):
        root = path
        for item in os.listdir(path):
            item = os.path.join(root, item)
            if os.path.isfile(item):
                self._handle_file(item)
                continue
            if os.path.isdir(item):
                if self.skip_subdir == False:
                    self._handle_directory(item)

    def _handle_file(self, path):
        ext = os.path.splitext(path)[-1].lower()
        if ext in ext_list:
            self.file_list.append(path)
        if self.allow_pdf and ext == '.pdf':
            self.file_list.append(path)

# start here
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="ebook batch rename")
    parser.add_argument('files', nargs='+',
                        help='list of ebook files to rename')
    parser.add_argument('-n', '--dry', dest='dry_run', action='store_true',
                        help='dry run of file name changes')
    parser.add_argument('-s', '--skip', dest='skip_subdir', action='store_true',
                        help='skip sub-directories')
    parser.add_argument('--pdf', dest='allow_pdf', action='store_true',
                        help='specifically allow to process PDF')
    parser.add_argument('-d', '--dest', dest='destination', type=str,
                        help='destination for renamed files')
    args = parser.parse_args()
    sys.exit(Batch(args).main())
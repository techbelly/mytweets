#!/usr/bin/env python2.6

from csv_ext import UnicodeReader, UnicodeWriter
from datetime import datetime
import sys
import re
import os

def fixing_nones(items):
    for i in items:
        def fix_none(i):
            if i == "None":
                return ""
            else:
                return i
        fields = [ fix_none(x) for x in i ]
        yield fields

def matching(items,name):
    for i in items:
        if re.search(name,i):
            yield i

def refile(name):
    in_file_name = '%s/%s.csv' % (FILE_PATH,name)
    in_file =  open(in_file_name)
    reader = fixing_nones(UnicodeReader(in_file))

    open_files = {}
    for line in reader:
        date_field = line[4]
        date = datetime.strptime(date_field,'%a %b %d %H:%M:%S +0000 %Y')
        file_name = "%s/%s-%d-%02d.csv" % (FILE_PATH,name,date.year, date.month)
        if file_name in open_files:
            _,writer = open_files[file_name]
        else:
            file = open(file_name,'ab')
            writer = UnicodeWriter(file)
            open_files[file_name] = (file,writer)
        writer.writerow(line)

    for file_name in open_files:
        file,_ = open_files[file_name]
        file.close()

    in_file.close()

    files = sorted(matching(os.listdir(FILE_PATH),name+'-'),reverse=True)
    if files[0]:
        os.rename("%s/%s" % (FILE_PATH,files[0]), in_file_name)


if __name__ == '__main__':

    if '-f' in sys.argv:
        FILE_PATH = sys.argv[sys.argv.index('-f')+1]
    else:
        try:
            from config import FILE_PATH
        except ImportError:
            print "File_path not specified. Create a config.py file. Or use -f on the command line. Cheerio"
            sys.exit(1)

    refile("mytweets")
    refile("myfriends")


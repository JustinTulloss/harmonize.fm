"""
Justin Tulloss

This compresses a bunch of javascripts file into one very small js file, and
css.
"""

from cStringIO import StringIO
import subprocess
import shutil
import os

COMPRESSOR_PATH = './yuicompressor-2.3.5.jar'
PREFIXES = {
    'css': '../masterapp/public/stylesheets',
    'js': '../masterapp/public/javascripts'
}

def concatenate(files):
    outfile = StringIO()
    for file in files:
        try:
            fd = open(file)
            outfile.write(fd.read())
        except IOError:
            pass
    outfile.seek(0)
    return outfile

def compress(file, outfile, type):
    compressor = subprocess.Popen([
        'java',
        '-jar',
        COMPRESSOR_PATH,
        '--type',
        type
    ], stdin = subprocess.PIPE, stdout = outfile)

    compressor.stdin.write(file.read())
    outfile.close()

def main():
    from masterapp.config.include_files import player_files,\
    compressed_player_files

    # Fix up path names
    jsfiles = []
    for file in player_files.javascripts:
        jsfiles.append(os.path.join(PREFIXES['js'], file))

    cssfiles = []
    for file in player_files.stylesheets:
        cssfiles.append(os.path.join(PREFIXES['css'], file)+'.css')

    # Write out compressed JS
    outp = os.path.join(PREFIXES['js'], compressed_player_files.javascripts[0])

	dir_name = os.path.dirname(outp)
	if not os.path.exists(dir_name):
		os.makedirs(dir_name)

    js = compress(concatenate(jsfiles), open(outp, 'wb'), 'js')

    # Write out compressed CSS
    outp = os.path.join(
        PREFIXES['css'], 
        compressed_player_files.stylesheets[0]
    )
    outp = outp+'.css'
    try:
        os.makedirs(os.path.dirname(outp))
    except Exception, e:
        print e
    css = compress(concatenate(cssfiles), open(outp, 'wb'), 'css')

if __name__ == '__main__':
    main()

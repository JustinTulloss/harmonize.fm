def populate_test_data():
    scandirs = [
        '/mnt/data/Users/justin/Music/Radiohead',
        '/mnt/data/Users/justin/Music/Wilco',
        '/mnt/data/Users/justin/Music/The Beatles'
    ]

    tagdata = []
    import os,re,sys
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(root,'..','..','..','libs.py'))

    from mutagen.easyid3 import EasyID3
    mp3exp = re.compile('.mp3$')
    for dir in scandirs:
        for root, dirs, files in os.walk(dir):
            for file in files:
                if mp3exp.search(file) != None:
                    tags = EasyID3(os.path.join(root,file))
                    tagdata.insert(0,{})#EasyID3 objects are immutable
                    tagdata[0].update(tags)
                    for k in tags.keys():
                        tagdata[0][k] = ','.join(tags[k])

    outfile=open('tagdata.py', 'w')
    outfile.write(u'tagdata=')
    outfile.write(str(tagdata))

if __name__ == "__main__":
    populate_test_data()
    

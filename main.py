import argparse
import re
import urllib.request
from urllib.parse import unquote
import os
import threading
import queue
import time
#from xml.dom.minidom import parse, parseString

args = None
file_dir = None

'''
TODO
thread the get_file function for faster urls parsing
'''

# https://downloads\.khinsider\.com\/game-soundtracks\/album\/(?P<album>[a-z0-9-]+)\/(?P<track>.*)

def init_arguments():
    global args
    parser = argparse.ArgumentParser(description='Video Game Music Downloader')
    parser.add_argument('url', default=None, help='Music page URL')
    parser.add_argument('-d', '--dir', default='.', help='Output directory')
    args = parser.parse_args()

def init_save_file_dir():
    global file_dir
    title = get_title(args.url)
    if title:
        print(f'album title: {title}')
    if args.dir == '.' and title != None:
        file_dir = os.path.join('.', get_folder_from_title(title))
    else:
        file_dir = args.dir
    print(f'save folder: {file_dir}')    
    
def __get_page(url):
    phandle = urllib.request.urlopen(url)
    raw_page = phandle.read()
    page = raw_page.decode("utf8")
    phandle.close()
    return page    

def get_title(url):
    pattern = '<title>(?P<title>.*) - Download'
    title = None
    page = __get_page(url)   
    for m in re.finditer(pattern, page):
        title = m['title']

    if title and '(' in title:
        title = title.split('(')[0].strip()

        #sanitize path
        invalid_chars = ['\\',  '/',  ':', '*',  '?',  '"',  '<',  '>',  '|']
        for ic in invalid_chars:
            while ic in title:
                title = title.replace(ic, ' ')
        
        #compress multipe spaces into one
        title = re.sub('\s+',' ', title)
        #title = ' '.join(title.split())

    return title

def get_folder_from_title(title):
    folder = title
    invalid_chars = ['\\',  '/',  ':', '*',  '?',  '"',  '<',  '>',  '|']
    for ic in invalid_chars:
        while ic in folder:
            folder = folder.replace(ic, ' ')
    
    #compress multipe spaces into one
    folder = re.sub('\s+',' ', folder)
    #folder = ' '.join(folder.split())    
    return folder

def get_tracks(url):
    tracks = []
    pattern = '<td class=\"playlistDownloadSong\"><a href=\"(?P<track>\/game-soundtracks\/album\/[0-9a-zA-Z\.%-]+\/[0-9a-zA-Z\.%-]+)\">'
    page = __get_page(url)   
    for m in re.finditer(pattern, page):
        tracks.append( m['track'].split('/')[-1])
    return tracks

def get_files(url):
    files = []
    pattern = 'href=\"(?P<file>https://[a-zA-Z0-9\./%-]+).+songDownloadLink'
    page = __get_page(url)   
    #print(page)
    for m in re.finditer(pattern, page):
        files.append( m['file'])
    return files

def get_links(url):
    tracks = get_tracks(url)
    print(f'found {len(tracks)} tracks')
    files = []
    for track in tracks:
        track_url = url + '/' + track
        print(f'fetching files for track: {track} with url {track_url}')
        files.extend(get_files( track_url))
    return files

def get_links_threaded(url):
    tracks = get_tracks(url)
    print(f'found {len(tracks)} tracks')
    files = []
    threads_list = []
    q = queue.Queue()
    for track in tracks:
        track_url = url + '/' + track
        print(f'fetching files for track: {track} with url {track_url}')

        t = threading.Thread(target=lambda q, arg1: q.put(get_files(arg1)), args=(q, track_url))
        t.start()
        threads_list.append(t)

    for t in threads_list:
        t.join()

    while not q.empty():
        result = q.get()
        files.extend(result)
    return files    


def get_extension(filename):
    splits = filename.split('.')
    ext = None
    if len(splits) > 0:
        ext = splits[-1]
    return ext

def get_outpath(filename):
    ext = get_extension(filename)
    out_path = os.path.join(file_dir, filename)
    if ext:
        out_path = os.path.join(file_dir, ext, filename)
    return out_path

def download(url, out_path):
    print(f'downloading: {url} as "{out_path}"')
    phandle = urllib.request.urlopen(url)
    raw_page = phandle.read()
    phandle.close()    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fh = open(out_path, 'wb')
    fh.write(raw_page)
    fh.close()

def downloader(files_queue):
    while not files_queue.empty():
        item = files_queue.get()
        download(**item)
        time.sleep(0.1)

def start_downloads(file_urls):
    pool = []
    files_queue = queue.Queue()
    for url in file_urls:
        out_path = get_outpath( unquote(url.split('/')[-1]) )
        files_queue.put( {'url':url, 'out_path':out_path} )      

    for _ in range(4):
        t = threading.Thread(target=downloader, args=[files_queue])
        t.start()
        pool.append(t)

    for t in pool:
        t.join()


def main():
    init_arguments() #sets global args
    init_save_file_dir()
    #file_urls = get_links(args.url)
    file_urls = get_links_threaded(args.url)
    print(f'found {len(file_urls)} files to download')
    #for url in file_urls:
    #    out_path = get_outpath( unquote(url.split('/')[-1]) )
    #    download(url, out_path)
    start_downloads(file_urls)



if __name__ == "__main__":
    main()

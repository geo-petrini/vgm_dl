import re
import urllib.request
from urllib.parse import unquote
import os
import logging
import threading
import queue
import time

## WORK IN PROGRESS NOT IMPLEMENTED

class VGMDl():

    def __init__(self, url: str, output_folder: str = ".", threaded = True):
        self.url = url
        self.output_folder = output_folder
        self.threaded = threaded
        self.parser = VGMPageParser(url)

        self.file_urls = None
        self.albun_title = self.parser.get_albun_title()
        self.init_save_file_dir()

    def init_save_file_dir(self):
        self.file_dir = None
        if self.albun_title:
            print(f'album title: {self.albun_title}')
        if self.output_folder == '.' and self.albun_title != None:
            self.file_dir = os.path.join('.', self.albun_title)
        else:
            self.file_dir = self.output_folder   
    
    def _get_file_outpath(self, filename):
        ext = self._get_extension(filename)
        out_path = os.path.join(self.file_dir, filename)
        if ext:
            out_path = os.path.join(self.file_dir, ext, filename)
        return out_path   

    def _get_extension(self, filename):
        splits = filename.split('.')
        ext = None
        if len(splits) > 0:
            ext = splits[-1]
        return ext     

    def get_folder_from_title(self):
        folder = self.albun_title
        invalid_chars = ['\\',  '/',  ':', '*',  '?',  '"',  '<',  '>',  '|']
        for ic in invalid_chars:
            while ic in folder:
                folder = folder.replace(ic, ' ')
        
        #compress multipe spaces into one
        folder = re.sub('\s+',' ', folder)
        return folder
    
    def get_links(self):
        if not self.file_urls:
            self.file_urls = self.parser.get_links()
        return self.file_urls
    
    def start_downloads(self, urls:list = None):
        if not urls: urls = self.get_links()

        if self.threaded:
            self._download_threaded()
        else:
            pass

    def get_progress(self):
        pass

    def __download_non_threaded(self):
        for url in self.file_urls:
            out_path = self._get_outpath( unquote(url.split('/')[-1]) )
            download(url, out_path)        

    def _downloader(self):
        while not self.files_queue.empty():
            item = self.files_queue.get()
            download(**item)
            time.sleep(0.1)

    def _download_threaded(self):
        pool = []
        self.files_queue = queue.Queue()
        for url in self.file_urls:
            out_path = self._get_file_outpath( unquote(url.split('/')[-1]) )
            self.files_queue.put( {'url':url, 'out_path':out_path} )      

        for _ in range(4):
            #t = threading.Thread(target=downloader, args=[files_queue])
            t = threading.Thread(target=self._downloader)
            t.start()
            pool.append(t)

        for t in pool:
            t.join()



class VGMPageParser():

    def __init__(self, url, threaded = False):
        self.url = url
        self.theaded = threaded

    def get_albun_title(self):
        pattern = '<title>(?P<title>.*) - Download'
        title = None
        page = get_page(self.url)
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

    def get_tracks(self, albun_url):
        tracks = []
        pattern = '<td class=\"playlistDownloadSong\"><a href=\"(?P<track>\/game-soundtracks\/album\/[0-9a-zA-Z\.%-]+\/[0-9a-zA-Z\.%-]+)\">'
        page = get_page(albun_url)
        for m in re.finditer(pattern, page):
            tracks.append( m['track'].split('/')[-1])
        return tracks   

    def get_track_files(self, url):
        files = []
        pattern = 'href=\"(?P<file>https://[a-zA-Z0-9\./%-]+).+songDownloadLink'
        page = get_page(url)   
        for m in re.finditer(pattern, page):
            files.append( m['file'])
        return files

    def get_links(self):
        tracks = self.get_tracks(self.url)
        print(f'found {len(tracks)} tracks')
        if self.theaded:
            return self._get_links_threaded(tracks)
        else:
            return self._get_links_non_threaded(tracks)
    
    def _get_links_non_threaded(self, tracks):
        files = []
        for track in tracks:
            track_url = self.url + '/' + track
            print(f'fetching files for track: {track} with url {track_url}')
            files.extend(self.get_track_files( track_url))
        return files

    def _get_links_threaded(self, tracks):
        files = []
        threads_list = []
        q = queue.Queue()
        for track in tracks:
            track_url = self.url + '/' + track
            print(f'fetching files for track: {track} with url {track_url}')

            t = threading.Thread(target=lambda q, arg1: q.put(self.get_track_files(arg1)), args=(q, track_url))
            t.start()
            threads_list.append(t)

        for t in threads_list:
            t.join()

        while not q.empty():
            result = q.get()
            files.extend(result)
        return files      

def get_page(url):
    try:
        phandle = urllib.request.urlopen(url)
        raw_page = phandle.read()
        page = raw_page.decode("utf8")
        phandle.close()
    except Exception as e:
        logging.exception(f'error processing {url}')
        return None
    return page

def download(url, out_path):
    print(f'downloading: {url} as "{out_path}"')
    phandle = urllib.request.urlopen(url)
    raw_page = phandle.read()
    phandle.close()    
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fh = open(out_path, 'wb')
    fh.write(raw_page)
    fh.close()

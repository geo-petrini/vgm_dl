import argparse

from  vgmdl import VGMDl, VGMPageParser



def init_arguments():
    global args
    parser = argparse.ArgumentParser(description='Video Game Music Downloader')
    parser.add_argument('url', default=None, help='Music page URL')
    parser.add_argument('-d', '--dir', default='.', help='Output directory')
    args = parser.parse_args()

def main():
    init_arguments() #sets global args
    dl = VGMDl(args.url, args.dir)
    dl.start_downloads()



if __name__ == "__main__":
    main()

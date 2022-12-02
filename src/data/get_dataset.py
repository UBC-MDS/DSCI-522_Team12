# author: Luke Yang
# date: 2022-11-24

"""
Downloads data csv data from the web to a local filepath as a csv format.
Usage: src/get_dataset.py --url=<url> [--out_filepath=<out_filepath>]
Options:
--url=<url>              URL from where to download the data (must be in standard csv format)
--out_file=<out_file>    Filename of the data, optional
"""

from docopt import docopt
import requests
import os
import time
import zipfile


def main(url, out_filepath = None):
    """
    downloads the data to the data/raw folder
    """
    filename = 'complaints'
    if out_filepath is None:
        out_filepath = os.path.join('data', 'raw', filename)
    try:
        assert len(url.split(' ')) == 1
        if os.path.exists(out_filepath+'.csv'):
            print("Data already exist")
            return 0
        zip_path = out_filepath+'.zip'
        csv_save_path = os.path.join('data', 'raw')
        print("Pulling the data from the web...")
        print("This may take up to 5 minutes...")
        start = time.time()
        r = requests.get(url, allow_redirects=True)
        mid = time.time()
        print("Downloading completed using",mid - start,'seconds.')
        print("Writing the content.")
        open(zip_path, 'wb').write(r.content)
        write_content_time = time.time()
        print("Writing completed using",write_content_time - mid,'seconds.')
        print("Unzipping the file")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(csv_save_path)
        print("Data downloaded using", time.time()-start,'seconds')
        os.remove(zip_path)
        return 0
    except Exception as req:
        print("An error occurred. Please try again and make sure you are using the correct command")
        print(req)
        return -1
    

if __name__ == "__main__":
    opt = docopt(__doc__)
    main(opt["--url"], opt["--out_filepath"])

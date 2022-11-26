# author: Luke Yang
# date: 2022-11-24

"""
Downloads data csv data from the web to a local filepath as a csv format.
Usage: src/get_dataset.py --url=<url> [--out_file_name=<out_file_name>]
Options:
--url=<url>              URL from where to download the data (must be in standard csv format)
--out_file=<out_file>    Filename of the data, optional
"""

from docopt import docopt
import requests
import os
import time
import zipfile

opt = docopt(__doc__)


def main(url, out_file_name):
    """
    downloads the data to the data/raw folder
    """
    
    if out_file_name is None:
        out_file_name = 'complaints.zip'
    try:
        zip_path = os.path.join('data', 'raw',out_file_name)
        csv_save_path = os.path.join('data', 'raw')
        print("Pulling from the web")
        start = time.time()
        r = requests.get(url, allow_redirects=True)
        mid = time.time()
        print("Downloading completed using",mid - start,'seconds.')
        print("Writing the content.")
        open(zip_path, 'wb').write(r.content)
        write_content_time = time.time()
        print("Downloading completed using",write_content_time - mid,'seconds.')
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
    main(opt["--url"], opt["--out_file_name"])

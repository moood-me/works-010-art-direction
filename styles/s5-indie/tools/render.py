"""SVG -> PNG with headless Chrome (one process per picture, small windows: light on the shared CPU)."""
import os
import re
import subprocess
import sys


def png(svg_path, png_path):
    s = open(svg_path).read()
    w = int(re.search(r'width="(\d+)"', s).group(1))
    h = int(re.search(r'height="(\d+)"', s).group(1))
    html = png_path + '.html'
    open(html, 'w').write(f'<html><body style="margin:0">{s}</body></html>')
    subprocess.run(['google-chrome', '--headless', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
                    f'--screenshot={os.path.abspath(png_path)}', f'--window-size={w},{h}',
                    'file://' + os.path.abspath(html)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
    os.remove(html)


if __name__ == '__main__':
    png(sys.argv[1], sys.argv[2])

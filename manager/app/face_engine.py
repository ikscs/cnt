#!/usr/local/bin/python
import sys
import requests

def main(url):
    response = requests.get(url)
    result = response.text
    return result


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f'Usage: {sys.argv[0]} <url>')
        exit(1)
    url = sys.argv[1]

    result = main(url)
    print(result)

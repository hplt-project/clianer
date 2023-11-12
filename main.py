#!/usr/bin/env python3

import argparse
from clianer.app import App

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()

    App(args).run()

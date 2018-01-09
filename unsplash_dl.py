#!/usr/bin/env python3

import os
import requests
from tqdm import tqdm
import argparse
from pprint import pprint
from json import load


COLLECTION_META = "https://api.unsplash.com/collections/{id}"
COLLECTION_PHOTOS = "https://api.unsplash.com/collections/{id}/photos"


def slugify(string):
    return "".join(x if x.isalnum() else "_" for x in string)


def main(args):
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument(
        "-t", "--token",
        help="Unsplash API token file. Default: token.json",
        default="token.json"
    )
    argument_parser.add_argument(
        "-o", "--output",
        help="Output folder. Default: derived from the title of collection"
    )
    argument_parser.add_argument(
        "collection_id",
        help="Collection id"
    )
    arguments = argument_parser.parse_args()
    TOKEN_FILE = arguments.token
    OUTPUT_FOLDER = arguments.output
    COLLECTION_ID = arguments.collection_id
    try:
        with open(TOKEN_FILE) as doc:
            token = load(doc)
    except Exception as E:
        print("Error!", str(E))
        return 1
    assert token["token_type"] == "bearer"
    if OUTPUT_FOLDER is None:
        collection_meta_request = requests.get(
            COLLECTION_META.format(id=COLLECTION_ID),
            headers={
                "Authorization": "Bearer {}".format(token["access_token"])
            }
        )
        if collection_meta_request.status_code != 200:
            print("Error!")
            pprint(collection_meta_request.json())
            return 1
        OUTPUT_FOLDER = slugify(collection_meta_request.json()["title"])
    try:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    except Exception as E:
        print("Error!", E)
        return 1

    collection_images_request = requests.get(
        COLLECTION_PHOTOS.format(id=COLLECTION_ID),
        params={
            "per_page": 50
        },
        headers={
            "Authorization": "Bearer {}".format(token["access_token"])
        }
    )
    if collection_images_request.status_code != 200:
        print("Error!")
        pprint(collection_images_request.json())
        return 1
    collection_json = collection_images_request.json()
    for image_json in tqdm(collection_json):
        image_url = image_json["urls"]["raw"]
        image_response = requests.get(image_url)
        if image_response.status_code == 200:
            with open(os.path.join(".", OUTPUT_FOLDER, image_json["id"] + ".jpg"), "wb") as image_file:
                image_file.write(image_response.content)
        else:
            print("Cannot load image with id='{}', continuing\u2026".format(image_json["id"]))
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))

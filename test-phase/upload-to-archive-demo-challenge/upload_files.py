"""
This script shows an example how to use GC-API to programmatically upload
files to an archive.

Remember, an archive is used to pull data per phase for a challenge. Each
phase has a designated archive. The archive is approached using its slug.

For your challenge, and this phase it is 'demo-challenge'.

Before you can run this script, you need to:
 * install gc-api (`pip install gcapi`)
 * update the EXPECTED_FILES
 * update the API_TOKEN with a personal token

Get a token from Grand Challenge:
  https://grand-challenge.org/settings/api-tokens/create/

For additional information about using gc-api and tokens, visit:
  https://grand-challenge.org/documentation/what-can-gc-api-be-used-for/#your-personal-api-token

Note that Grand-Challenge does its own post-processing on the files and the archive
will be filled with the result of this post-processing.

Check your uploaded results here:
 https://grand-challenge.org/archives/demo-challenge/

And the intermediate processing state here:
  https://grand-challenge.org/cases/uploads/

Happy uploading!
"""

from pathlib import Path

import gcapi


API_TOKEN = "REPLACE-ME-WITH-YOUR-TOKEN"

ARCHIVE_SLUG = "demo-challenge"

EXPECTED_CASES = [
    # for: color-fundus-image
    ["file0.example"],
    ["file1.example"],
    ["file2.example"],
]


def main():
    check_files()
    upload_files()
    return 0


def check_files():
    # Perform a sanity-check to see if we have all the files we expect
    for case in EXPECTED_CASES:
        for file in case:
            path = Path(file)
            if not path.exists():
                raise RuntimeError(
                    f"Could not find {path.absolute()}, check that you're running in the right directory"
                )


def upload_files():
    # Uploads files to the Grand-Challenge archive

    client = gcapi.Client(token=API_TOKEN)
    archive = client.archives.detail(slug=ARCHIVE_SLUG)
    archive_api_url = archive["api_url"]

    for case in EXPECTED_CASES:
        print(f"Uploading {case} to {archive['title']}")

        content = map_case_content_to_interfaces(case)
        archive_item = client.archive_items.create(archive=archive_api_url, values=[])
        client.update_archive_item(
            archive_item_pk=archive_item["pk"],
            values=content,
        )


def map_case_content_to_interfaces(case):
    return {
        "color-fundus-image": [Path(case[0])],
    }


if __name__ == "__main__":
    raise SystemExit(main())

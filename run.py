import json
import re
from functools import partial

# Import `readline` allows for reading longer lines on MacOS
import readline
import subprocess
import webbrowser


def getFirstURL() -> str:
    webbrowser.open_new_tab("https://slack.com/customize/emoji")
    print(
        "1. Open up the Chrome Developer Tab by pressing (CMD+Shift+C on MacOS or Ctrl+Shift+C on Windows)"
    )
    print("2. Navigate to the 'Network' tab.")
    print("3. Search for 'api/emoji.' in the \"Filter\" search.")
    print("4. Reload the Page.")
    print("5. Right Click on the result, select 'Copy', and then 'Copy as cURL'.")
    print("Paste the results here and hit enter again:")
    result = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
        except EOFError:
            break
        result.append(line)
    return " ".join(result)


def increase_count(obj):
    return obj.group(0).replace(obj.group(1), "999")


def set_page(idx, obj):
    return obj.group(0).replace(obj.group(1), str(idx))


def getEmojiJSONMap() -> str:
    curl_command = getFirstURL()
    curl_command = re.sub(r"\"count\"[\\a-z]+([0-9]+)", increase_count, curl_command)

    page = 1
    found = []
    emoji_to_url = {}

    while True:
        print(f"Fetching page {page}")
        output = subprocess.run(
            curl_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        try:
            json_blob = json.loads(output.stdout)
        except Exception as e:
            print("Failure!!!", e, output.stdout, output.stderr)
            continue

        found.append(json_blob)

        for emoji in json_blob["emoji"]:
            emoji_to_url[emoji["name"]] = emoji["url"]

        if json_blob["paging"]["pages"] == page:
            break

        page += 1
        curl_command = re.sub(
            r'"page"[\\a-z]+([0-9]+)', partial(set_page, page), curl_command
        )

    default_name = "emoji_exfil.json"
    suggested_file_name = input(
        f"Output file name ({default_name}), click enter to accept or type in a new one:\n"
    )
    if not suggested_file_name:
        suggested_file_name = default_name
    with open(suggested_file_name, "w") as f:
        json.dump(emoji_to_url, f, indent=2)


if __name__ == "__main__":
    getEmojiJSONMap()

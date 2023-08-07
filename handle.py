import sys
import tempfile
import urllib.request
import zipfile
import os
import shutil
import json
import glob
import hashlib
import base64

# get arguments from command line
commit = sys.argv[1]
print("commit: " + commit)

archive_url = f"https://github.com/EmulatorJS/EmulatorJS/archive/{commit}.zip"

# download to temp folder
temp_dir = tempfile.TemporaryDirectory()
print("temp_dir: " + temp_dir.name)

# download zip
zip_path = temp_dir.name + f"/emulatorjs-{commit}.zip"
print("zip_path: " + zip_path)
urllib.request.urlretrieve(archive_url, zip_path)
print("downloaded")

folder_name = "EmulatorJS-" + commit

# unzip to current folder
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    path = os.path.abspath(os.getcwd())
    print(f"unzipping to {path}")
    shutil.rmtree(folder_name, ignore_errors=True)
    zip_ref.extractall(path)

# delete EmulatorJS folder
print("deleted EmulatorJS folder")
shutil.rmtree("EmulatorJS", ignore_errors=True)

# rename folder
print("renamed folder")
os.rename(folder_name, "EmulatorJS")

# delete zip
print("deleted zip")
os.remove(zip_path)

# generate version
print("generating version")
emulatorjs_version = "./EmulatorJS/data/version.json"
# read json
with open(emulatorjs_version, "r") as f:
    data = json.load(f)
    ejs_num_version = str(data["current_version"])

# 40.5 to 4.0.5
semver = ejs_num_version[0] + "." + ejs_num_version[1] + "." + ejs_num_version[3:]
print("semver: " + semver)
semver_commit = semver + "-" + commit
print("semver_commit: " + semver_commit)

# update package.json version
print("updating package.json version")
package_json = "./package.json"
with open(package_json, "r") as f:
    data = json.load(f)
    data["version"] = semver_commit
    with open(package_json, "w") as f2:
        json.dump(data, f2, indent=2)

# recursively get files
print("recursively getting files")
files = glob.glob("./EmulatorJS/**/*", recursive=True)
print("files count: " + str(len(files)))

sri = {}
for file in files:
    if os.path.isdir(file):
        continue
    with open(file, "rb") as f:
        content = f.read()

        # Calculate sha256
        sha256 = hashlib.sha256(content).digest()
        sha256Base64 = base64.b64encode(sha256).decode('utf-8').strip()

        # Add to sri
        sri[file[2:]] = "sha256-" + sha256Base64

sri_result = {
    "version": semver_commit,
    "sri": sri
}

# write sri.json
print("writing sri.json")
with open("./sri.json", "w") as f:
    json.dump(sri_result, f, indent=2)

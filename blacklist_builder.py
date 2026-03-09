import argparse
import json
import os
import zipfile

DEFAULT_JARS_FOLDER = "hack_clients"
OUTPUT_FOLDER = "output"
OUTPUT_FILE = "modblacklist.json"


def extract_mod_info(jar_path):
    try:
        with zipfile.ZipFile(jar_path, 'r') as jar:
            if 'fabric.mod.json' not in jar.namelist():
                return None
            with jar.open('fabric.mod.json') as f:
                data = json.load(f)
                return {
                    'id':      data.get('id',      'unknown'),
                    'name':    data.get('name',    'unknown'),
                    'version': data.get('version', 'unknown'),
                }
    except (zipfile.BadZipFile, json.JSONDecodeError, KeyError):
        return None


def scan_folder(folder):
    results = []
    for filename in sorted(os.listdir(folder)):
        if not filename.endswith('.jar'):
            continue
        path = os.path.join(folder, filename)
        info = extract_mod_info(path)
        if info:
            info['file'] = filename
            results.append(info)
        else:
            print(f"  [SKIP] {filename} -- not a Fabric mod or unreadable")
    return results


def save_blacklist(path, ids):
    data = {
        "_info": "Mod IDs listed here will be rejected on join. Case-insensitive.",
        "blacklist": sorted(ids)
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--jars',
        default=os.path.join(script_dir, DEFAULT_JARS_FOLDER)
    )
    args = parser.parse_args()

    output_dir  = os.path.join(script_dir, OUTPUT_FOLDER)
    output_path = os.path.join(output_dir, OUTPUT_FILE)

    print(f"\n{'='*50}")
    print("  ModGuard Blacklist Builder -- by Treamhiler")
    print(f"{'='*50}\n")

    if not os.path.isdir(args.jars):
        os.makedirs(args.jars)
        print(f"[INFO] Created jars folder: {args.jars}")
        print(f"       Drop your hack client .jar files in there and run again.")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"[INFO] Created output folder: {output_dir}")

    print(f"[1/3] Scanning jars in: {args.jars}")
    found = scan_folder(args.jars)
    if not found:
        print("  No Fabric mods found. Make sure your jars are in the hack_clients folder.")
        return

    print(f"\n  Found {len(found)} Fabric mod(s):")
    for mod in found:
        print(f"    {mod['file']}")
        print(f"      ID: {mod['id']}  |  Name: {mod['name']}  |  Version: {mod['version']}")

    print(f"\n[2/3] Checking output: {output_path}")
    if os.path.exists(output_path):
        print(f"  [OVERWRITE] Existing modblacklist.json will be replaced.")
    else:
        print(f"  [CREATE] modblacklist.json will be created.")

    print(f"\n[3/3] Building blacklist...")
    new_ids = sorted(set(mod['id'].lower() for mod in found))
    for i in new_ids:
        print(f"      + {i}")

    save_blacklist(output_path, new_ids)

    print(f"\n{'='*50}")
    print(f"  Done! Blacklist has {len(new_ids)} entries.")
    print(f"  Saved to: {output_path}")
    print(f"  Copy output/modblacklist.json to your server's plugins/ModGuard/ folder.")
    print(f"  Then run /modguard reload on your server.")
    print(f"{'='*50}\n")


if __name__ == '__main__':
    main()
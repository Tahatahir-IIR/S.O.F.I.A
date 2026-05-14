import winreg
import os
import json

def get_registry_apps():
    apps = {}
    paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    for root, path in paths:
        try:
            with winreg.OpenKey(root, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, name) as subkey:
                            try:
                                val, _ = winreg.QueryValue(subkey, None)
                                if val: apps[name.lower().replace(".exe", "")] = val.strip('"').split(',')[0]
                            except:
                                try:
                                    disp, _ = winreg.QueryValueEx(subkey, "DisplayName")
                                    icon, _ = winreg.QueryValueEx(subkey, "DisplayIcon")
                                    if icon:
                                        clean_icon = icon.split(',')[0].strip('"')
                                        if clean_icon.lower().endswith(".exe"):
                                            apps[disp.lower()] = clean_icon
                                except: pass
                    except: continue
        except: continue
    return apps

def fast_scavenge():
    apps = {}
    # Only check top-level of these folders for performance
    roots = ["C:\\", "D:\\"]
    folders = ["wamp64", "wamp", "xampp", "Program Files", "Program Files (x86)"]
    
    for r in roots:
        for f in folders:
            path = os.path.join(r, f)
            if os.path.exists(path):
                # Search only 2 levels deep for root apps
                for root, dirs, files in os.walk(path):
                    if root.count(os.sep) - path.count(os.sep) > 2:
                        continue
                    for file in files:
                        if file.lower().endswith(".exe"):
                            if not any(x in file.lower() for x in ["uninstall", "setup", "update"]):
                                apps[file.lower().replace(".exe", "")] = os.path.join(root, file)
    return apps

def update_db():
    print("[Indexer] Running Optimized Hybrid Scraper...")
    all_apps = fast_scavenge()
    all_apps.update(get_registry_apps())
    
    # Core Overrides
    all_apps.update({"chrome": "chrome", "edge": "msedge", "powerpoint": "powerpnt", "wampserver": all_apps.get("wampmanager", "wampmanager")})
    
    with open("C:/S.O.F.I.A/outputs/apps.json", "w") as f:
        json.dump(all_apps, f, indent=4)
    print(f"[Indexer] Indexed {len(all_apps)} applications.")

if __name__ == "__main__":
    update_db()

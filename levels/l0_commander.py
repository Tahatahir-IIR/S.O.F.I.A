import os
import subprocess
import re
import json

class L0Commander:
    def __init__(self):
        self.commands = []
        self._load_defaults()

    def _load_defaults(self):
        # Default commands
        self.register(r"open (chrome|browser)", lambda *args: self._run("start chrome"))
        self.register(r"open edge", lambda *args: self._run("start msedge"))
        self.register(r"open discord", lambda *args: self._run("start discord:"))
        self.register(r"open (calculator|calc)", lambda *args: self._run("calc"))
        self.register(r"open (notepad|editor)", lambda *args: self._run("notepad"))
        self.register(r"open (terminal|cmd|powershell)", lambda *args: self._run("start powershell"))
        self.register(r"what time is it", self.get_time)

    def register(self, pattern, action):
        self.commands.append((re.compile(pattern, re.IGNORECASE), action))

    def match_and_execute(self, query):
        query = query.lower().strip()
        
        # 1. Check hardcoded patterns first
        for pattern, action in self.commands:
            match = pattern.match(query)
            if match:
                print(f"[L0] Match found for: {query}")
                result = action(*match.groups()) if match.groups() else action()
                return result or "Command executed successfully."
        
        # 2. Dynamic App Dictionary Check
        if query.startswith("open "):
            app_target = query.replace("open ", "").strip()
            return self._launch_from_dict(app_target)
            
        return None

    def _launch_from_dict(self, app_name):
        db_path = "C:/S.O.F.I.A/outputs/apps.json"
        if not os.path.exists(db_path):
            return None
            
        try:
            with open(db_path, "r") as f:
                apps = json.load(f)
            
            # Common aliases for stubborn apps
            aliases = {
                "powerpoint": ["powerpnt", "microsoft powerpoint"],
                "word": ["winword", "microsoft word"],
                "excel": ["excel", "microsoft excel"],
                "cmd": ["cmd.exe", "command prompt"]
            }
            
            targets = [app_name]
            if app_name in aliases:
                targets.extend(aliases[app_name])

            # Try exact matches then fuzzy
            for target in targets:
                # Direct check
                if target in apps:
                    exec_path = f'"{apps[target]}"' if " " in apps[target] and "--" not in apps[target] else apps[target]
                    return self._run(f'start "" {exec_path}')
                
                # Fuzzy check (Both directions)
                for name, cmd in apps.items():
                    if target in name or name in target:
                        exec_path = f'"{cmd}"' if " " in cmd and "--" not in cmd else cmd
                        return self._run(f'start "" {exec_path}')
        except Exception as e:
            return f"Error reading app dictionary: {e}"
        return None

    def _run(self, cmd):
        try:
            os.system(cmd)
            return f"Executing system command: {cmd}"
        except Exception as e:
            return f"Failed to execute command: {e}"

    def get_time(self):
        from datetime import datetime
        return f"The current time is {datetime.now().strftime('%H:%M')}."

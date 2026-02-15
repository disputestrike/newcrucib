"""
CrucibAI Sublime Text Plugin
115-agent autonomous code generation for Sublime Text
"""

import sublime
import sublime_plugin
import requests
import json
import threading
from typing import Optional, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = ""
TIMEOUT = 30


class CrucibaiCommand(sublime_plugin.TextCommand):
    """Base class for CrucibAI commands"""

    def get_settings(self):
        """Get plugin settings"""
        return sublime.load_settings("CrucibAI.sublime-settings")

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Optional[Dict]:
        """Make HTTP request to CrucibAI API"""
        try:
            url = f"{API_BASE_URL}{endpoint}"
            headers = {
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }

            if method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=TIMEOUT)
            else:
                response = requests.get(url, headers=headers, timeout=TIMEOUT)

            if response.status_code == 200:
                return response.json()
            else:
                sublime.error_message(f"API Error: {response.status_code}")
                return None
        except Exception as e:
            sublime.error_message(f"Request failed: {str(e)}")
            return None

    def get_selected_text(self) -> str:
        """Get selected text from editor"""
        view = self.view
        if view.sel():
            region = view.sel()[0]
            return view.substr(region)
        return ""

    def get_all_text(self) -> str:
        """Get all text from editor"""
        return self.view.substr(sublime.Region(0, self.view.size()))

    def insert_text(self, text: str, position: Optional[int] = None):
        """Insert text at position"""
        view = self.view
        if position is None:
            position = view.sel()[0].end() if view.sel() else 0

        view.run_command("insert", {"characters": text})

    def replace_selection(self, text: str):
        """Replace selected text"""
        view = self.view
        if view.sel():
            for region in view.sel():
                view.replace(region, text)


class CrucibaiGenerateCodeCommand(CrucibaiCommand):
    """Generate code using AI"""

    def run(self, edit):
        def on_input(prompt):
            if not prompt:
                return

            def generate():
                sublime.status_message("CrucibAI: Generating code...")

                data = {
                    "prompt": prompt,
                    "context": self.get_all_text(),
                    "language": self.view.syntax().name.lower() if self.view.syntax() else "text"
                }

                result = self.make_request("POST", "/api/generate", data)

                def on_done():
                    if result:
                        self.insert_text(result.get("code", ""))
                        sublime.status_message("✅ Code generated")
                    else:
                        sublime.status_message("❌ Generation failed")

                sublime.set_timeout(on_done, 0)

            threading.Thread(target=generate).start()

        self.view.window().show_input_panel(
            "Describe what to generate:",
            "",
            on_input,
            None,
            None
        )


class CrucibaiQuickFixCommand(CrucibaiCommand):
    """Quick fix code issues"""

    def run(self, edit):
        selected = self.get_selected_text()
        if not selected:
            sublime.error_message("Select code to fix")
            return

        def fix():
            sublime.status_message("CrucibAI: Fixing code...")

            data = {
                "code": selected,
                "language": self.view.syntax().name.lower() if self.view.syntax() else "text"
            }

            result = self.make_request("POST", "/api/fix", data)

            def on_done():
                if result:
                    self.replace_selection(result.get("fixed_code", ""))
                    sublime.status_message(f"✅ Fixed {result.get('issues_count', 0)} issues")
                else:
                    sublime.status_message("❌ Fix failed")

            sublime.set_timeout(on_done, 0)

        threading.Thread(target=fix).start()


class CrucibaiAnalyzeVibeCommand(CrucibaiCommand):
    """Analyze code vibe"""

    def run(self, edit):
        def analyze():
            sublime.status_message("CrucibAI: Analyzing vibe...")

            data = {
                "code": self.get_all_text(),
                "file_path": self.view.file_name() or "untitled"
            }

            result = self.make_request("POST", "/api/analyze-vibe", data)

            def on_done():
                if result:
                    vibe = result.get("vibe_name", "Unknown")
                    tone = result.get("emotional_tone", "Unknown")
                    energy = result.get("visual_energy", "Unknown")
                    message = f"🎨 Vibe: {vibe}\n📊 Tone: {tone}\n⚡ Energy: {energy}"
                    sublime.message_dialog(message)
                    sublime.status_message("✅ Vibe analyzed")
                else:
                    sublime.status_message("❌ Analysis failed")

            sublime.set_timeout(on_done, 0)

        threading.Thread(target=analyze).start()


class CrucibaiGenerateTestsCommand(CrucibaiCommand):
    """Generate tests"""

    def run(self, edit):
        def generate():
            sublime.status_message("CrucibAI: Generating tests...")

            data = {
                "code": self.get_all_text(),
                "language": self.view.syntax().name.lower() if self.view.syntax() else "text",
                "file_path": self.view.file_name() or "untitled"
            }

            result = self.make_request("POST", "/api/generate-tests", data)

            def on_done():
                if result:
                    # Create new file with tests
                    window = self.view.window()
                    test_view = window.new_file()
                    test_view.insert(edit, 0, result.get("test_code", ""))
                    test_view.set_syntax_file("Packages/Python/Python.sublime-syntax")
                    sublime.status_message(f"✅ Tests generated ({result.get('coverage', 0)}% coverage)")
                else:
                    sublime.status_message("❌ Test generation failed")

            sublime.set_timeout(on_done, 0)

        threading.Thread(target=generate).start()


class CrucibaiRefactorCommand(CrucibaiCommand):
    """Refactor code"""

    def run(self, edit):
        def refactor():
            sublime.status_message("CrucibAI: Refactoring...")

            data = {
                "code": self.get_all_text(),
                "language": self.view.syntax().name.lower() if self.view.syntax() else "text"
            }

            result = self.make_request("POST", "/api/refactor", data)

            def on_done():
                if result:
                    # Replace all code
                    region = sublime.Region(0, self.view.size())
                    self.view.replace(edit, region, result.get("refactored_code", ""))
                    improvement = result.get("performance_gain", 0)
                    sublime.status_message(f"✅ Refactored ({improvement}% improvement)")
                else:
                    sublime.status_message("❌ Refactoring failed")

            sublime.set_timeout(on_done, 0)

        threading.Thread(target=refactor).start()


class CrucibaiGenerateDocsCommand(CrucibaiCommand):
    """Generate documentation"""

    def run(self, edit):
        def generate():
            sublime.status_message("CrucibAI: Generating documentation...")

            data = {
                "code": self.get_all_text(),
                "language": self.view.syntax().name.lower() if self.view.syntax() else "text",
                "file_path": self.view.file_name() or "untitled"
            }

            result = self.make_request("POST", "/api/generate-docs", data)

            def on_done():
                if result:
                    # Create new markdown file
                    window = self.view.window()
                    doc_view = window.new_file()
                    doc_view.insert(edit, 0, result.get("documentation", ""))
                    doc_view.set_syntax_file("Packages/Markdown/Markdown.sublime-syntax")
                    sublime.status_message("✅ Documentation generated")
                else:
                    sublime.status_message("❌ Documentation generation failed")

            sublime.set_timeout(on_done, 0)

        threading.Thread(target=generate).start()


class CrucibaiSettingsCommand(sublime_plugin.WindowCommand):
    """Open CrucibAI settings"""

    def run(self):
        self.window.run_command("edit_settings", {
            "base_file": "${packages}/CrucibAI/CrucibAI.sublime-settings",
            "default": """{
    // CrucibAI API URL
    "api_url": "http://localhost:8000",
    
    // CrucibAI API Key
    "api_key": "",
    
    // Auto-analyze on save
    "auto_analyze": true,
    
    // Enable voice input
    "enable_voice": true,
    
    // Enable vibe analysis
    "enable_vibe": true
}"""
        })


class CrucibaiStatusCommand(sublime_plugin.WindowCommand):
    """Show CrucibAI status"""

    def run(self):
        def check_status():
            try:
                response = requests.get(f"{API_BASE_URL}/api/health", timeout=5)
                status = "✅ Connected" if response.status_code == 200 else "❌ Disconnected"
            except:
                status = "❌ Disconnected"

            sublime.message_dialog(f"CrucibAI Status: {status}")

        threading.Thread(target=check_status).start()


# Event listeners
class CrucibaiEventListener(sublime_plugin.EventListener):
    """Listen for editor events"""

    def on_post_save_async(self, view):
        """Auto-analyze on save"""
        settings = sublime.load_settings("CrucibAI.sublime-settings")
        if settings.get("auto_analyze", True):
            # Could implement auto-analysis here
            pass

    def on_hover(self, view, point, hover_zone):
        """Show hover information"""
        if hover_zone == sublime.HOVER_TEXT:
            # Could implement hover info here
            pass


def plugin_loaded():
    """Plugin loaded"""
    global API_KEY
    settings = sublime.load_settings("CrucibAI.sublime-settings")
    API_KEY = settings.get("api_key", "")
    print("✅ CrucibAI plugin loaded")


def plugin_unloaded():
    """Plugin unloaded"""
    print("CrucibAI plugin unloaded")

"""MORS Auto Clicker — modern Windows desktop app. Copyright (c) 2026 MORS."""
import ctypes
import json
import threading
import time
import tkinter as tk
import webbrowser
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

DISCORD = "https://discord.gg/ANHebepXT9"
TIKTOK = "https://www.tiktok.com/@m_9gc"
CONFIG = Path.home() / "AppData" / "Local" / "MORS" / "auto_clicker.json"

USER32 = ctypes.windll.user32 if hasattr(ctypes, "windll") else None
VK = {"SPACE": 0x20, "ENTER": 0x0D, "TAB": 0x09, "ESC": 0x1B,
      "BACKSPACE": 0x08, "DELETE": 0x2E, "UP": 0x26, "DOWN": 0x28,
      "LEFT": 0x25, "RIGHT": 0x27, "HOME": 0x24, "END": 0x23,
      "PAGEUP": 0x21, "PAGEDOWN": 0x22, "INSERT": 0x2D,
      "CTRL": 0x11, "CONTROL": 0x11, "SHIFT": 0x10, "ALT": 0x12}
VK.update({f"F{n}": 0x6F + n for n in range(1, 13)})
ACCENT = "#6D3DEA"
ACCENT_HOVER = "#875BFF"
COLORS = {
    "Dark": {"bg": "#0C0C16", "side": "#131322", "card": "#19192B", "line": "#29283D",
             "text": "#F4F1FF", "muted": "#A09AAF", "field": "#232238"},
    "Light": {"bg": "#F7F6FC", "side": "#FFFFFF", "card": "#FFFFFF", "line": "#E4E0EF",
              "text": "#211936", "muted": "#736A88", "field": "#F2F0F9"}
}
WORDS = {
    "English": {
        "mouse": "Mouse Clicker", "keyboard": "Keyboard Presser", "settings": "Settings",
        "about": "About MORS", "subtitle": "Your precision automation studio",
        "interval": "Interval (milliseconds)", "delay": "Start delay (milliseconds)",
        "cycles": "Repeat cycles", "infinite": "Repeat until stopped",
        "mouse_button": "Mouse button", "double": "Double click",
        "fixed": "Click at fixed coordinates", "capture": "Capture cursor",
        "position": "Click position", "key_sequence": "Key sequence",
        "key_hint": "Type SPACE, A, ENTER, CTRL+S, or A,B,C (comma = sequence)",
        "start": "START  ·  F6", "stop": "STOP  ·  F8",
        "ready": "Ready", "running": "Running", "stopping": "Stopping",
        "appearance": "Appearance", "language": "Language", "theme": "Theme",
        "social": "Community & support", "details": "Designed by MORS for Windows",
        "hint": "F6: start/pause  •  F8: emergency stop", "save": "Save preferences",
        "saved": "Preferences saved.", "invalid": "Invalid input",
        "intro_mouse": "Repeat mouse clicks at your chosen speed and position.",
        "intro_keyboard": "Repeat keyboard inputs and combinations reliably.",
        "intro_settings": "Make the app look and feel right for you.",
        "intro_about": "Original Windows utility developed by MORS.",
        "copy": "© 2026 MORS. All rights reserved.",
        "controls": "Automation controls", "options": "Behavior",
        "connected": "Open official links", "position_current": "Cursor position",
        "mode": "Work mode", "active_mouse": "Mouse automation",
        "active_keyboard": "Keyboard automation"
    },
    "العربية": {
        "mouse": "النقر التلقائي", "keyboard": "ضغطات الكيبورد", "settings": "الإعدادات",
        "about": "عن MORS", "subtitle": "أدوات أتمتة دقيقة وسهلة",
        "interval": "الفاصل الزمني (مللي ثانية)", "delay": "تأخير البداية (مللي ثانية)",
        "cycles": "عدد مرات التكرار", "infinite": "استمرار حتى الإيقاف",
        "mouse_button": "زر الماوس", "double": "نقرة مزدوجة",
        "fixed": "النقر عند إحداثيات محددة", "capture": "التقاط موضع المؤشر",
        "position": "موضع النقر", "key_sequence": "تسلسل المفاتيح",
        "key_hint": "مثال SPACE أو A أو ENTER أو CTRL+S أو A,B,C",
        "start": "تشغيل  ·  F6", "stop": "إيقاف  ·  F8",
        "ready": "جاهز", "running": "يعمل الآن", "stopping": "جار الإيقاف",
        "appearance": "المظهر", "language": "اللغة", "theme": "السمة",
        "social": "المجتمع والدعم", "details": "صممه MORS لنظام Windows",
        "hint": "F6: تشغيل/إيقاف  •  F8: إيقاف طوارئ", "save": "حفظ الإعدادات",
        "saved": "تم حفظ الإعدادات.", "invalid": "إدخال غير صحيح",
        "intro_mouse": "نقر متكرر بسرعة وموضع تختارهما بنفسك.",
        "intro_keyboard": "أتمتة المفاتيح والمجموعات والتسلسلات.",
        "intro_settings": "خصص لغة التطبيق ومظهره كما تحب.",
        "intro_about": "أداة مستقلة لنظام ويندوز من تطوير MORS.",
        "copy": "© 2026 MORS. جميع الحقوق محفوظة.",
        "controls": "التحكم في الأتمتة", "options": "خيارات التشغيل",
        "connected": "الروابط الرسمية", "position_current": "موضع المؤشر",
        "mode": "وضع التشغيل", "active_mouse": "أتمتة الماوس",
        "active_keyboard": "أتمتة الكيبورد"
    }
}

def parse_key(part):
    part = part.strip().upper()
    if len(part) == 1 and part in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
        return ord(part)
    if part not in VK:
        raise ValueError("Unsupported key: " + part)
    return VK[part]

def parse_sequence(raw):
    steps = []
    for step in raw.split(","):
        names = [x.strip() for x in step.split("+")]
        if not names or any(not x for x in names):
            raise ValueError("Empty key in sequence")
        steps.append([parse_key(x) for x in names])
    return steps

def execute_keys(steps, stopped):
    for combo in steps:
        if stopped.is_set():
            return
        pressed = []
        try:
            for key in combo:
                USER32.keybd_event(key, 0, 0, 0)
                pressed.append(key)
            stopped.wait(0.04)
        finally:
            for key in reversed(pressed):
                USER32.keybd_event(key, 0, 2, 0)
        if stopped.wait(0.05):
            return

def mouse_action(button, is_double):
    down, up = {"Left": (2, 4), "Right": (8, 16), "Middle": (32, 64)}[button]
    for index in range(2 if is_double else 1):
        USER32.mouse_event(down, 0, 0, 0, 0)
        USER32.mouse_event(up, 0, 0, 0, 0)
        if is_double and index == 0:
            time.sleep(0.06)

def get_cursor_position():
    class POINT(ctypes.Structure):
        _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
    p = POINT()
    if not USER32.GetCursorPos(ctypes.byref(p)):
        raise OSError("Unable to read cursor position")
    return p.x, p.y

def validate(settings):
    interval = int(settings["interval"])
    delay = int(settings["delay"])
    cycles = int(settings["cycles"])
    x, y = int(settings["x"]), int(settings["y"])
    if not 20 <= interval <= 3600000:
        raise ValueError("Interval: 20–3600000 ms")
    if not 0 <= delay <= 600000:
        raise ValueError("Start delay: 0–600000 ms")
    if not 1 <= cycles <= 10000000:
        raise ValueError("Repeat cycles: 1–10000000")
    if not -100000 <= x <= 100000 or not -100000 <= y <= 100000:
        raise ValueError("Coordinates are out of range")
    if settings["button"] not in ("Left", "Right", "Middle"):
        raise ValueError("Unsupported mouse button")
    sequence = parse_sequence(settings["keys"]) if settings["page"] == "keyboard" else []
    return interval, delay, cycles, x, y, sequence

class MorsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MORS Auto Clicker — Windows")
        self.geometry("1000x680")
        self.minsize(850, 600)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.values = {
            "interval": tk.StringVar(value="1000"), "delay": tk.StringVar(value="0"),
            "cycles": tk.StringVar(value="10"), "keys": tk.StringVar(value="SPACE"),
            "x": tk.StringVar(value="0"), "y": tk.StringVar(value="0"),
            "button": tk.StringVar(value="Left"), "infinite": tk.BooleanVar(value=False),
            "fixed": tk.BooleanVar(value=False), "double": tk.BooleanVar(value=False),
        }
        self.language = "English"
        self.theme = "Dark"
        self.page = "mouse"
        self.active = False
        self.worker = None
        self.stop_event = threading.Event()
        self.last_f6 = False
        self.last_f8 = False
        self._read_settings()
        self.render()
        self.after(90, self.poll_hotkeys)

    def word(self, key):
        return WORDS[self.language][key]

    def color(self, name):
        return COLORS[self.theme][name]

    def _read_settings(self):
        try:
            data = json.loads(CONFIG.read_text(encoding="utf-8"))
            if data.get("language") in WORDS:
                self.language = data["language"]
            if data.get("theme") in COLORS:
                self.theme = data["theme"]
            for k, var in self.values.items():
                if k in data:
                    var.set(data[k])
        except (OSError, ValueError, TypeError, KeyError, tk.TclError):
            pass

    def save(self):
        CONFIG.parent.mkdir(parents=True, exist_ok=True)
        data = {k: v.get() for k, v in self.values.items()}
        data.update({"language": self.language, "theme": self.theme})
        CONFIG.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def label(self, parent, text, size=13, bold=False, muted=False):
        return ctk.CTkLabel(parent, text=text,
                            text_color=self.color("muted" if muted else "text"),
                            font=ctk.CTkFont(family="Segoe UI", size=size,
                                             weight="bold" if bold else "normal"))

    def card(self, parent):
        return ctk.CTkFrame(parent, fg_color=self.color("card"), corner_radius=18,
                            border_color=self.color("line"), border_width=1)

    def entry(self, parent, variable, width=170):
        return ctk.CTkEntry(parent, textvariable=variable, width=width, height=42,
                            corner_radius=9, fg_color=self.color("field"),
                            border_color=self.color("line"),
                            text_color=self.color("text"))

    def button(self, parent, text, command, accent=False, width=140):
        return ctk.CTkButton(parent, text=text, command=command, width=width,
                             height=42, corner_radius=10,
                             fg_color=ACCENT if accent else self.color("field"),
                             hover_color=ACCENT_HOVER if accent else self.color("line"),
                             text_color="#FFFFFF" if accent else self.color("text"),
                             font=ctk.CTkFont("Segoe UI", 13, "bold"))

    def switch(self, parent, key, label):
        return ctk.CTkSwitch(parent, text=label, variable=self.values[key],
                             progress_color=ACCENT, button_color="#FFFFFF",
                             text_color=self.color("text"),
                             font=ctk.CTkFont("Segoe UI", 12))

    def field(self, parent, title, variable):
        cell = ctk.CTkFrame(parent, fg_color="transparent")
        self.label(cell, title, muted=True).pack(anchor="w", pady=(0, 6))
        self.entry(cell, variable, width=190).pack(fill="x")
        return cell

    def select_page(self, page):
        self.page = page
        self.render()

    def set_theme(self, value):
        if value not in COLORS: return
        self.theme = value
        self.save()
        self.render()

    def set_language(self, value):
        if value not in WORDS: return
        self.language = value
        self.save()
        self.render()

    def render(self):
        ctk.set_appearance_mode(self.theme.lower())
        for child in self.winfo_children():
            child.destroy()
        self.configure(fg_color=self.color("bg"))
        base = ctk.CTkFrame(self, fg_color="transparent")
        base.pack(fill="both", expand=True)

        side = ctk.CTkFrame(base, width=225, corner_radius=0, fg_color=self.color("side"))
        side.pack(side="left", fill="y")
        side.pack_propagate(False)
        self.label(side, "MORS", size=29, bold=True).pack(anchor="w", padx=26, pady=(32, 0))
        ctk.CTkFrame(side, width=45, height=4, fg_color=ACCENT, corner_radius=5).pack(anchor="w", padx=26, pady=(5, 38))
        items = [("mouse", "◉", "mouse"), ("keyboard", "⌨", "keyboard"),
                 ("settings", "⚙", "settings"), ("about", "ⓘ", "about")]
        for page, symbol, token in items:
            selected = page == self.page
            ctk.CTkButton(side, text=f"  {symbol}   {self.word(token)}", anchor="w",
                          command=lambda x=page:self.select_page(x), height=48,
                          fg_color=ACCENT if selected else "transparent",
                          hover_color=ACCENT_HOVER if selected else self.color("field"),
                          text_color="#FFFFFF" if selected else self.color("text"),
                          corner_radius=11,
                          font=ctk.CTkFont("Segoe UI", 13, "bold" if selected else "normal")
                          ).pack(fill="x", padx=15, pady=5)
        self.label(side, "MORS  ·  v2.0 BETA", size=11, muted=True).pack(side="bottom", pady=23)

        content = ctk.CTkScrollableFrame(base, fg_color="transparent",
                                         scrollbar_button_color=self.color("line"))
        content.pack(side="left", fill="both", expand=True, padx=28, pady=24)
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(2, 22))
        self.label(header, self.word(self.page), size=25, bold=True).pack(anchor="w")
        self.label(header, self.word("intro_" + self.page), size=12, muted=True).pack(anchor="w", pady=(5,0))
        if self.page in ("mouse", "keyboard"):
            self.render_automation(content)
        elif self.page == "settings":
            self.render_settings(content)
        else:
            self.render_about(content)

    def render_automation(self, parent):
        panel = self.card(parent)
        panel.pack(fill="x", pady=(0,16))
        heading = ctk.CTkFrame(panel, fg_color="transparent")
        heading.pack(fill="x", padx=22, pady=(18,10))
        self.label(heading, self.word("controls"), size=16, bold=True).pack(anchor="w")
        fields = ctk.CTkFrame(panel, fg_color="transparent")
        fields.pack(fill="x", padx=22, pady=8)
        for idx, (title, var) in enumerate([
            (self.word("interval"), self.values["interval"]),
            (self.word("delay"), self.values["delay"]),
            (self.word("cycles"), self.values["cycles"])
        ]):
            cell = self.field(fields, title, var)
            cell.grid(row=0, column=idx, padx=(0,12), sticky="ew")
            fields.columnconfigure(idx, weight=1)
        self.switch(panel, "infinite", self.word("infinite")).pack(anchor="w", padx=22, pady=(8,22))
        options = self.card(parent)
        options.pack(fill="x", pady=(0,16))
        self.label(options, self.word("options"), size=16, bold=True).pack(anchor="w", padx=22, pady=(18,12))
        if self.page == "mouse":
            line = ctk.CTkFrame(options, fg_color="transparent")
            line.pack(fill="x", padx=22, pady=8)
            self.label(line, self.word("mouse_button")).pack(side="left", padx=(0,14))
            ctk.CTkOptionMenu(line, variable=self.values["button"],
                              values=["Left", "Right", "Middle"],
                              fg_color=ACCENT, button_color="#5633B9", width=150).pack(side="left")
            self.switch(options, "double", self.word("double")).pack(anchor="w", padx=22, pady=10)
            self.switch(options, "fixed", self.word("fixed")).pack(anchor="w", padx=22, pady=(5,10))
            point = ctk.CTkFrame(options, fg_color="transparent")
            point.pack(fill="x", padx=22, pady=(0,20))
            self.label(point, "X").pack(side="left", padx=(0,6))
            self.entry(point,self.values["x"], 85).pack(side="left",padx=(0,14))
            self.label(point, "Y").pack(side="left",padx=(0,6))
            self.entry(point,self.values["y"],85).pack(side="left",padx=(0,14))
            self.button(point,self.word("capture"),self.capture, width=165).pack(side="left")
        else:
            self.label(options,self.word("key_sequence"),muted=True).pack(anchor="w",padx=22,pady=(6,6))
            self.entry(options,self.values["keys"]).pack(fill="x",padx=22,pady=(0,8))
            self.label(options,self.word("key_hint"),size=11,muted=True).pack(anchor="w",padx=22,pady=(0,22))
        control = self.card(parent)
        control.pack(fill="x")
        row = ctk.CTkFrame(control, fg_color="transparent")
        row.pack(fill="x", padx=22, pady=(22,12))
        self.button(row,self.word("start"),self.start,accent=True,width=180).pack(side="left",padx=(0,12))
        self.button(row,self.word("stop"),self.halt,width=150).pack(side="left")
        self.status_label = self.label(control, self.word("running") if self.active else self.word("ready"),
                                       size=13, bold=True)
        self.status_label.pack(anchor="w",padx=22,pady=(0,8))
        self.label(control,self.word("hint"),size=11,muted=True).pack(anchor="w",padx=22,pady=(0,20))

    def render_settings(self,parent):
        panel=self.card(parent)
        panel.pack(fill="x")
        self.label(panel,self.word("appearance"),size=17,bold=True).pack(anchor="w",padx=24,pady=(24,18))
        self.label(panel,self.word("language"),muted=True).pack(anchor="w",padx=24)
        ctk.CTkOptionMenu(panel,values=["English","العربية"],command=self.set_language,
                          fg_color=ACCENT,button_color="#5633B9",width=210
                          ).pack(anchor="w",padx=24,pady=(6,18))
        # set current value after CTkOptionMenu construction
        language_menu=panel.winfo_children()[-1]
        language_menu.set(self.language)
        self.label(panel,self.word("theme"),muted=True).pack(anchor="w",padx=24)
        ctk.CTkSegmentedButton(panel,values=["Dark","Light"],command=self.set_theme,
                               selected_color=ACCENT,selected_hover_color=ACCENT_HOVER
                               ).pack(anchor="w",padx=24,pady=(8,24))
        theme_selector=panel.winfo_children()[-1]
        theme_selector.set(self.theme)
        self.button(parent,self.word("save"),self.save_and_status,accent=True).pack(anchor="w",pady=22)

    def render_about(self,parent):
        panel=self.card(parent)
        panel.pack(fill="x")
        self.label(panel,"MORS",size=34,bold=True).pack(anchor="w",padx=24,pady=(23,6))
        self.label(panel,self.word("details"),size=14).pack(anchor="w",padx=24)
        self.label(panel,self.word("copy"),muted=True).pack(anchor="w",padx=24,pady=(6,24))
        self.label(panel,self.word("social"),size=17,bold=True).pack(anchor="w",padx=24,pady=(0,10))
        links=ctk.CTkFrame(panel,fg_color="transparent")
        links.pack(anchor="w",padx=24,pady=(0,24))
        self.button(links,"Discord",lambda:webbrowser.open(DISCORD),accent=True).pack(side="left",padx=(0,12))
        self.button(links,"TikTok",lambda:webbrowser.open(TIKTOK)).pack(side="left")

    def save_and_status(self):
        try:
            self.save()
            messagebox.showinfo("MORS",self.word("saved"))
        except OSError as exc:
            messagebox.showerror("MORS",str(exc))

    def capture(self):
        try:
            x,y=get_cursor_position()
            self.values["x"].set(str(x))
            self.values["y"].set(str(y))
            self.values["fixed"].set(True)
        except Exception as exc:
            messagebox.showerror("MORS",str(exc))

    def snapshot(self):
        data={k:v.get() for k,v in self.values.items()}
        data["page"]=self.page
        return data

    def start(self):
        if self.active:
            return
        if USER32 is None:
            messagebox.showerror("MORS","Windows is required.")
            return
        try:
            data=self.snapshot()
            config=validate(data)
            self.save()
        except (ValueError, OSError, TypeError) as exc:
            messagebox.showerror(self.word("invalid"),str(exc))
            return
        self.stop_event.clear()
        self.active=True
        self._set_status(self.word("running"))
        self.worker=threading.Thread(target=self._worker,args=(data,config),daemon=True)
        self.worker.start()

    def _worker(self,data,config):
        interval,delay,cycles,x,y,steps=config
        try:
            if self.stop_event.wait(delay/1000):
                return
            n=0
            while not self.stop_event.is_set() and (data["infinite"] or n<cycles):
                if data["page"]=="mouse":
                    if data["fixed"]:
                        USER32.SetCursorPos(x,y)
                    mouse_action(data["button"],data["double"])
                else:
                    execute_keys(steps,self.stop_event)
                n+=1
                if self.stop_event.wait(interval/1000):
                    break
        except Exception as exc:
            try:
                self.after(0,lambda msg=str(exc):self._set_status("Error: "+msg))
            except RuntimeError:
                pass
        finally:
            try:
                self.after(0,self._done)
            except RuntimeError:
                pass

    def _set_status(self,text):
        if hasattr(self,"status_label") and self.status_label.winfo_exists():
            self.status_label.configure(text=text)

    def _done(self):
        self.active=False
        self._set_status(self.word("ready"))

    def halt(self):
        self.stop_event.set()
        if self.active:
            self._set_status(self.word("stopping"))

    def poll_hotkeys(self):
        if not self.winfo_exists():
            return
        if USER32 is not None:
            f6=bool(USER32.GetAsyncKeyState(0x75)&0x8000)
            f8=bool(USER32.GetAsyncKeyState(0x77)&0x8000)
            if f8 and not self.last_f8:
                self.halt()
            elif f6 and not self.last_f6:
                if self.active:self.halt()
                elif self.page in ("mouse","keyboard"):self.start()
            self.last_f6=f6
            self.last_f8=f8
        self.after(90,self.poll_hotkeys)

    def close(self):
        self.halt()
        try:
            self.save()
        except OSError:
            pass
        self.destroy()

if __name__ == "__main__":
    MorsApp().mainloop()

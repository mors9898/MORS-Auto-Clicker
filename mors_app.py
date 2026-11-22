"""MORS Auto Clicker - independent Windows utility, © 2026 MORS."""
import ctypes
import json
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk, messagebox
import webbrowser

USER32 = ctypes.windll.user32
VK = {"SPACE":32,"ENTER":13,"TAB":9,"ESC":27,"UP":38,"DOWN":40,"LEFT":37,"RIGHT":39,"BACKSPACE":8,"DELETE":46}
for i in range(1,13): VK["F"+str(i)] = 111+i
def keycode(name):
    name=name.strip().upper()
    if len(name)==1 and name.isalnum(): return ord(name)
    return VK.get(name)
def press_key(name):
    keys=name.upper().split("+")
    codes=[]
    for p in keys:
        p=p.strip()
        code={"CTRL":17,"CONTROL":17,"SHIFT":16,"ALT":18}.get(p,keycode(p))
        if code is None: raise ValueError("Invalid key: "+p)
        codes.append(code)
    for c in codes: USER32.keybd_event(c,0,0,0)
    time.sleep(.025)
    for c in reversed(codes): USER32.keybd_event(c,0,2,0)
def click(which,double=False):
    which=which.lower()
    flags={"left":(2,4),"right":(8,16),"middle":(32,64)}[which]
    for _ in range(2 if double else 1):
        USER32.mouse_event(flags[0],0,0,0,0)
        USER32.mouse_event(flags[1],0,0,0,0)
        if double: time.sleep(.045)
def cursor():
    class POINT(ctypes.Structure):
        _fields_=[("x",ctypes.c_long),("y",ctypes.c_long)]
    p=POINT()
    USER32.GetCursorPos(ctypes.byref(p))
    return p.x,p.y
class App:
    def __init__(self,root):
        self.root=root
        self.root.title("MORS Auto Clicker  |  © 2026 MORS")
        self.root.geometry("630x620")
        self.root.minsize(540,540)
        self.stop=threading.Event()
        self.running=False
        self.thread=None
        self.lastf6=False
        self.lastf8=False
        self.kind=tk.StringVar(value="Mouse")
        self.interval=tk.StringVar(value="1000")
        self.delay=tk.StringVar(value="0")
        self.repeats=tk.StringVar(value="10")
        self.forever=tk.BooleanVar(value=False)
        self.button=tk.StringVar(value="left")
        self.double=tk.BooleanVar(value=False)
        self.fixed=tk.BooleanVar(value=False)
        self.x=tk.StringVar(value="0")
        self.y=tk.StringVar(value="0")
        self.keys=tk.StringVar(value="SPACE")
        self.status=tk.StringVar(value="Ready • F6 start/stop • F8 emergency stop")
        self.config_path=Path.home()/".mors_auto_clicker.json"
        self._load()
        self._build()
        self.root.after(90,self._hotkeys)
        self.root.protocol("WM_DELETE_WINDOW",self._close)
    def _build(self):
        self.root.configure(bg="#151923")
        style=ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TFrame",background="#151923")
        style.configure("TLabel",background="#151923",foreground="#e9ecf3",font=("Segoe UI",10))
        style.configure("TButton",font=("Segoe UI",10),padding=8)
        style.configure("TRadiobutton",background="#151923",foreground="#e9ecf3")
        style.configure("TCheckbutton",background="#151923",foreground="#e9ecf3")
        frame=ttk.Frame(self.root,padding=20)
        frame.pack(fill="both",expand=True)
        ttk.Label(frame,text="MORS  /  AUTO CLICKER",font=("Segoe UI",20,"bold")).pack(anchor="w")
        ttk.Label(frame,text="Independent Windows mouse & keyboard automation",font=("Segoe UI",9)).pack(anchor="w",pady=(0,16))
        kinds=ttk.Frame(frame);kinds.pack(fill="x")
        for name in ("Mouse","Keyboard"):
            ttk.Radiobutton(kinds,text=name,value=name,variable=self.kind).pack(side="left",padx=(0,18))
        def row(label,var):
            f=ttk.Frame(frame);f.pack(fill="x",pady=5)
            ttk.Label(f,text=label,width=24).pack(side="left")
            ttk.Entry(f,textvariable=var).pack(side="left",fill="x",expand=True)
        row("Interval (milliseconds)",self.interval)
        row("Start delay (milliseconds)",self.delay)
        row("Repeat cycles",self.repeats)
        ttk.Checkbutton(frame,text="Repeat until stopped",variable=self.forever).pack(anchor="w",pady=5)
        ttk.Label(frame,text="Mouse click settings").pack(anchor="w",pady=(12,4))
        mouse=ttk.Frame(frame);mouse.pack(fill="x")
        ttk.Combobox(mouse,textvariable=self.button,values=["left","right","middle"],state="readonly",width=12).pack(side="left")
        ttk.Checkbutton(mouse,text="Double click",variable=self.double).pack(side="left",padx=10)
        ttk.Checkbutton(mouse,text="Fixed position",variable=self.fixed).pack(side="left",padx=10)
        points=ttk.Frame(frame);points.pack(fill="x",pady=6)
        ttk.Label(points,text="X").pack(side="left")
        ttk.Entry(points,textvariable=self.x,width=9).pack(side="left",padx=5)
        ttk.Label(points,text="Y").pack(side="left")
        ttk.Entry(points,textvariable=self.y,width=9).pack(side="left",padx=5)
        ttk.Button(points,text="Use cursor position",command=self._capture).pack(side="left",padx=8)
        ttk.Label(frame,text="Keyboard keys (one key or combo, e.g. SPACE or CTRL+S)").pack(anchor="w",pady=(10,4))
        ttk.Entry(frame,textvariable=self.keys).pack(fill="x")
        buttons=ttk.Frame(frame);buttons.pack(fill="x",pady=(20,10))
        ttk.Button(buttons,text="START  (F6)",command=self.start).pack(side="left",fill="x",expand=True,padx=(0,5))
        ttk.Button(buttons,text="STOP  (F8)",command=self.halt).pack(side="left",fill="x",expand=True,padx=(5,0))
        ttk.Label(frame,textvariable=self.status,wraplength=560).pack(anchor="w",pady=(4,12))
        links=ttk.Frame(frame);links.pack(fill="x",side="bottom")
        ttk.Button(links,text="MORS Discord",command=lambda:webbrowser.open("https://discord.gg/ANHebepXT9")).pack(side="left",padx=(0,8))
        ttk.Button(links,text="MORS TikTok",command=lambda:webbrowser.open("https://www.tiktok.com/@m_9gc")).pack(side="left")
        ttk.Label(links,text="© 2026 MORS").pack(side="right")
    def _capture(self):
        x,y=cursor();self.x.set(str(x));self.y.set(str(y));self.fixed.set(True)
    def _validate(self):
        interval=int(self.interval.get())
        delay=int(self.delay.get())
        repeats=int(self.repeats.get())
        if not 20<=interval<=3600000: raise ValueError("Interval must be 20–3600000 ms")
        if not 0<=delay<=600000: raise ValueError("Delay must be 0–600000 ms")
        if not 1<=repeats<=10000000: raise ValueError("Repeat cycles must be 1–10000000")
        x,y=int(self.x.get()),int(self.y.get())
        if not -100000<=x<=100000 or not -100000<=y<=100000: raise ValueError("Position out of range")
        if self.kind.get()=="Keyboard" and not self.keys.get().strip(): raise ValueError("Enter a key")
        if self.kind.get()=="Keyboard":
            for name in self.keys.get().split(","):
                for part in name.strip().split("+"):
                    p=part.strip().upper()
                    if p not in ("CTRL","CONTROL","SHIFT","ALT") and keycode(p) is None: raise ValueError("Unsupported key: "+p)
        return interval,delay,repeats,x,y
    def start(self):
        if self.running:return
        try: interval,delay,repeats,x,y=self._validate()
        except (ValueError,TypeError) as exc:
            messagebox.showerror("MORS Auto Clicker",str(exc));return
        self._save()
        self.stop.clear();self.running=True
        config=(interval,delay,repeats,x,y,self.kind.get(),self.forever.get(),self.button.get(),self.double.get(),self.fixed.get(),self.keys.get())
        self.status.set("Running (F8 stops immediately)")
        self.thread=threading.Thread(target=self._run,args=(config,),daemon=True)
        self.thread.start()
    def _run(self,c):
        interval,delay,repeats,x,y,kind,forever,button,double,fixed,keys=c
        try:
            if self.stop.wait(delay/1000):return
            index=0
            while not self.stop.is_set() and (forever or index<repeats):
                if kind=="Mouse":
                    if fixed: USER32.SetCursorPos(x,y)
                    click(button,double)
                else:
                    for key in keys.split(","):
                        if self.stop.is_set():break
                        press_key(key.strip())
                index+=1
                if self.stop.wait(interval/1000):break
        except Exception as exc:
            self.root.after(0,lambda e=str(exc):self.status.set("Error: "+e))
        finally:
            self.root.after(0,self._done)
    def _done(self):
        self.running=False
        self.status.set("Stopped • F6 start/stop • F8 emergency stop")
    def halt(self):
        self.stop.set()
        self.status.set("Stopping...")
    def _hotkeys(self):
        if not self.root.winfo_exists():return
        f6=bool(USER32.GetAsyncKeyState(0x75)&0x8000)
        f8=bool(USER32.GetAsyncKeyState(0x77)&0x8000)
        if f8 and not self.lastf8:self.halt()
        elif f6 and not self.lastf6:
            if self.running:self.halt()
            else:self.start()
        self.lastf6=f6;self.lastf8=f8
        self.root.after(90,self._hotkeys)
    def _load(self):
        try:
            obj=json.loads(self.config_path.read_text(encoding="utf-8"))
            for name in ("interval","delay","repeats","button","x","y","keys","kind"):
                if name in obj:getattr(self,name).set(obj[name])
            for name in ("forever","fixed","double"):
                if name in obj:getattr(self,name).set(bool(obj[name]))
        except (OSError,ValueError,TypeError,KeyError):pass
    def _save(self):
        obj={name:getattr(self,name).get() for name in ("interval","delay","repeats","button","x","y","keys","kind","forever","fixed","double")}
        try:self.config_path.write_text(json.dumps(obj,indent=2),encoding="utf-8")
        except OSError:pass
    def _close(self):
        self.halt();self._save();self.root.destroy()
if __name__=="__main__":
    App(tk.Tk()).root.mainloop()

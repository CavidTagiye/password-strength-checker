import tkinter as tk
from tkinter import ttk
from math import log10
from decimal import Decimal, getcontext

# Higher precision for log-based time formatting
getcontext().prec = 40

# Character sets
LOWERS = set("abcdefghijklmnopqrstuvwxyz")
UPPERS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
DIGITS = set("0123456789")
SYMBOLS = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")  # common ASCII punctuation

COMMON_PASSWORDS = {
    "123456","password","123456789","qwerty","12345678","111111","123123","abc123",
    "12345","password1","iloveyou","admin","welcome","monkey","dragon","letmein",
    "login","princess","qwerty123","football","1q2w3e4r","zaq12wsx","shadow","sunshine"
}

SEQUENCES = [
    "abcdefghijklmnopqrstuvwxyz",
    "qwertyuiopasdfghjklzxcvbnm",
    "0123456789"
]

class PasswordMeterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Password Strength & Crack Time Estimator")
        self.geometry("780x540")
        self.minsize(720, 520)
        self.configure(padx=16, pady=16)

        self.style = ttk.Style(self)
        if "clam" in self.style.theme_names():
            self.style.theme_use("clam")

        # Progressbar styles for dynamic color
        self.style.configure("Green.Horizontal.TProgressbar", troughcolor="#e6f4ea", background="#22c55e")
        self.style.configure("Yellow.Horizontal.TProgressbar", troughcolor="#fff7cc", background="#f59e0b")
        self.style.configure("Red.Horizontal.TProgressbar", troughcolor="#ffe6e6", background="#ef4444")
        self.style.configure("Blue.Horizontal.TProgressbar", troughcolor="#e6f0ff", background="#3b82f6")

        self._build_ui()
        self._evaluate("")

    def _build_ui(self):
        # Header
        title = ttk.Label(self, text="Password Strength & Crack Time Estimator", font=("Segoe UI", 16, "bold"))
        subtitle = ttk.Label(self, text=("Type your password – we will score it by length, variety and patterns, "
            "plus estimate crack time at different speeds."))
        title.grid(row=0, column=0, sticky="w")
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 12))

        # Input frame
        inframe = ttk.Frame(self)
        inframe.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        inframe.columnconfigure(1, weight=1)

        ttk.Label(inframe, text="Password:", font=("Segoe UI", 11)).grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.var_password = tk.StringVar()
        self.entry = ttk.Entry(inframe, textvariable=self.var_password, show="*")
        self.entry.grid(row=0, column=1, sticky="ew")
        self.entry.bind("<KeyRelease>", lambda e: self._evaluate(self.var_password.get()))

        self.show_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(inframe, text="Show", variable=self.show_var, command=self._toggle_show).grid(row=0, column=2, padx=(8,0))

        # Overall meter
        meter_frame = ttk.LabelFrame(self, text="Overall Score (0–100)")
        meter_frame.grid(row=3, column=0, sticky="ew", pady=(4, 10))
        meter_frame.columnconfigure(0, weight=1)

        self.overall_pb = ttk.Progressbar(meter_frame, maximum=100, style="Green.Horizontal.TProgressbar")
        self.overall_pb.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        self.lbl_overall = ttk.Label(meter_frame, text="",
                                     font=("Segoe UI", 11, "bold"))
        self.lbl_overall.grid(row=0, column=1, padx=10)

        # Detail meters
        details = ttk.Frame(self)
        details.grid(row=4, column=0, sticky="nsew")
        self.rowconfigure(4, weight=1)
        details.columnconfigure(0, weight=1)
        details.columnconfigure(1, weight=1)

        # Left: category scores
        left = ttk.LabelFrame(details, text="Category Scores")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        left.columnconfigure(1, weight=1)

        self.length_pb = self._cat_row(left, 0, "Length")
        self.variety_pb = self._cat_row(left, 1, "Variety")
        self.pattern_pb = self._cat_row(left, 2, "Pattern/Penalty")
        self.entropy_pb = self._cat_row(left, 3, "Entropy (relative)")

        # Right: crack times
        right = ttk.LabelFrame(details, text="Crack Time Estimate")
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        cols = ("Speed (estimate)", "Average crack time")
        self.tree = ttk.Treeview(right, columns=cols, show="headings", height=8)
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=10, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        right.rowconfigure(0, weight=1)

        # Footer info
        self.lbl_info = ttk.Label(self, text="Note: Time is an average brute‑force estimate (N/2). Entropy and pool are inferred from used character classes only.")
        self.lbl_info.grid(row=5, column=0, sticky="w", pady=(8,0))

    def _cat_row(self, parent, r, label):
        ttk.Label(parent, text=label).grid(row=r, column=0, sticky="w", padx=8, pady=6)
        pb = ttk.Progressbar(parent, maximum=100, style="Blue.Horizontal.TProgressbar")
        pb.grid(row=r, column=1, sticky="ew", padx=(0,8))
        return pb

    def _toggle_show(self):
        self.entry.configure(show="" if self.show_var.get() else "*")

    def _evaluate(self, pwd: str):
        # Compute basic features
        length = len(pwd)
        contains_lower = any(ch in LOWERS for ch in pwd)
        contains_upper = any(ch in UPPERS for ch in pwd)
        contains_digit = any(ch in DIGITS for ch in pwd)
        contains_symbol = any(ch in SYMBOLS for ch in pwd)

        # Character pool size inferred from used sets (attacker assumption for this estimator)
        pool = 0
        if contains_lower: pool += 26
        if contains_upper: pool += 26
        if contains_digit: pool += 10
        if contains_symbol: pool += len(SYMBOLS)
        pool = max(pool, 1)

        # Category: length score (0-30)
        if length == 0:
            length_score = 0
        elif length < 6:
            length_score = 8
        elif length < 10:
            length_score = 18
        elif length < 14:
            length_score = 26
        else:
            length_score = 30

        # Category: variety score (0-30)
        variety_classes = sum([contains_lower, contains_upper, contains_digit, contains_symbol])
        variety_score = {0:0, 1:8, 2:18, 3:26, 4:30}.get(variety_classes, 0)

        # Pattern penalties (start from 30 and subtract)
        penalty = 0
        # Common password exact match
        if pwd.lower() in COMMON_PASSWORDS:
            penalty += 20
        # Repeated single-char or two-char patterns
        if length >= 3 and (len(set(pwd)) == 1):
            penalty += 18
        # Detect increasing sequences of 4+ in known sequences
        penalty += self._sequence_penalty(pwd)
        # Simple leet reversals of common words (e.g., p@ssw0rd)
        if self._looks_like_common_leet(pwd):
            penalty += 8
        pattern_score = max(0, 30 - penalty)

        # Entropy (relative 0-10 -> 0-10 mapped to 0-10, then scaled to 10 points)
        entropy_bits = 0.0 if length == 0 else length * (log10(pool) / log10(2))
        # Map entropy to 0..10 (very rough): 0b -> 0, 60b+ -> 10
        entropy_score = max(0, min(10, int((entropy_bits / 60) * 10)))
        entropy_score_scaled = entropy_score * 10  # convert to 0..100 for bar, will cap at 100

        # Overall score (weighted)
        overall = int(min(100, length_score + variety_score + pattern_score + entropy_score))

        # Update overall bar & text
        self.overall_pb.configure(style=self._level_style(overall))
        self.overall_pb['value'] = overall
        self.lbl_overall.configure(text=f"{overall} / 100  —  {self._label_for_score(overall)}")

        # Update category bars
        self.length_pb['value'] = length_score * (100/30)
        self.variety_pb['value'] = variety_score * (100/30)
        self.pattern_pb['value'] = pattern_score * (100/30)
        self.entropy_pb['value'] = min(100, entropy_score_scaled)

        # Update crack time table
        for i in self.tree.get_children():
            self.tree.delete(i)
        gps_options = [
            ("Typical PC (~10^6/s)", 10**6),
            ("High-end GPU (~10^9/s)", 10**9),
            ("Small cluster (~10^12/s)", 10**12),
            ("Large cluster (~10^15/s)", 10**15),
        ]
        if length == 0:
            for name, _ in gps_options:
                self.tree.insert('', 'end', values=(name, "—"))
            return

        # Use log10 to avoid huge integers: T_avg ≈ (N/2)/gps, with N = pool^length
        log10N = Decimal(length) * Decimal(log10(pool))
        log10_two = Decimal(log10(2))
        for name, gps in gps_options:
            log10T = log10N - log10_two - Decimal(log10(gps))
            nice = self._format_time_from_log10(log10T)
            self.tree.insert('', 'end', values=(name, nice))

    def _sequence_penalty(self, pwd: str) -> int:
        p = pwd.lower()
        max_hit = 0
        for seq in SEQUENCES:
            # forward
            max_hit = max(max_hit, self._longest_run_in_sequence(p, seq))
            # backward
            max_hit = max(max_hit, self._longest_run_in_sequence(p, seq[::-1]))
        return 0 if max_hit < 4 else 6 + (max_hit - 4)  # penalize 4+ length runs

    def _longest_run_in_sequence(self, s: str, seq: str) -> int:
        longest = 0
        current = 1
        for i in range(1, len(s)):
            prev = s[i-1]
            cur = s[i]
            if prev in seq and cur in seq:
                if seq.find(cur) - seq.find(prev) == 1:
                    current += 1
                    longest = max(longest, current)
                else:
                    current = 1
            else:
                current = 1
        return longest

    def _looks_like_common_leet(self, pwd: str) -> bool:
        p = pwd.lower()
        leet_map = str.maketrans({"@":"a","$":"s","0":"o","1":"l","!":"i","3":"e","7":"t"})
        de_leet = p.translate(leet_map)
        for w in ("password","letmein","dragon","monkey","welcome"):
            if w in de_leet:
                return True
        return False

    def _label_for_score(self, s: int) -> str:
        if s < 30: return "Very Weak"
        if s < 50: return "Weak"
        if s < 70: return "Fair"
        if s < 85: return "Strong"
        return "Very Strong"

    def _level_style(self, s: int) -> str:
        if s < 50: return "Red.Horizontal.TProgressbar"
        if s < 70: return "Yellow.Horizontal.TProgressbar"
        return "Green.Horizontal.TProgressbar"

    def _format_time_from_log10(self, log10_seconds: Decimal) -> str:
        # If extremely small
        if log10_seconds < Decimal(-3):
            return "\u003c 1ms"
        # Compute rough seconds = 10^x using Decimal
        seconds = Decimal(10) ** log10_seconds
        # Humanize progressively without huge integer ops
        # Ranges
        minute = Decimal(60)
        hour = minute * 60
        day = hour * 24
        year = day * Decimal(365.25)

        if seconds < Decimal('1'):
            ms = seconds * Decimal(1000)
            return f"{ms.quantize(Decimal('1.'))} ms"
        if seconds < minute:
            return f"{seconds.quantize(Decimal('1.'))} s"
        if seconds < hour:
            m = (seconds / minute)
            return f"{m.quantize(Decimal('1.'))} min"
        if seconds < day:
            h = (seconds / hour)
            return f"{h.quantize(Decimal('1.'))} hour"
        if seconds < year:
            d = (seconds / day)
            return f"{d.quantize(Decimal('1.'))} days"
        if seconds < year * 1000:
            y = (seconds / year)
            return f"{y.quantize(Decimal('1.'))} years"
        # Very large: scientific
        exp = int(log10_seconds)  # floor
        return f"≈ 10^{exp} seconds"

if __name__ == "__main__":
    app = PasswordMeterApp()
    app.mainloop()

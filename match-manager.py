import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

FILE_NAME = "match_details.json"

def load_matches():
    if not os.path.exists(FILE_NAME):
        return []
    with open(FILE_NAME, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_matches(matches):
    with open(FILE_NAME, "w", encoding="utf-8") as f:
        json.dump(matches, f, indent=4, ensure_ascii=False)

def parse_date(date_str):
    """
    Accepts and validates date in ddmmyyyy format (e.g., 20102025 for 20 Oct 2025)
    Returns the same format if valid, else shows error and returns None
    """
    try:
        if len(date_str) != 8 or not date_str.isdigit():
            raise ValueError
        # Validate by trying to parse
        datetime.strptime(date_str, "%d%m%Y")
        return date_str  # keep same format
    except ValueError:
        messagebox.showerror("Invalid Date", "Please enter the date in ddmmyyyy format (e.g., 20102025).")
        return None


class MatchManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("⚽ Match Manager")
        self.root.geometry("750x420")
        self.root.configure(bg="#f3f3f3")

        self.matches = load_matches()

        # Title
        tk.Label(root, text="⚽ Match Manager", font=("Segoe UI", 18, "bold"), bg="#f3f3f3").pack(pady=10)

        # Frame for list
        frame = tk.Frame(root, bg="#f3f3f3")
        frame.pack(fill="both", expand=True, padx=20)

        columns = ("home", "away", "date", "time")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=12)
        self.tree.heading("home", text="Home Team")
        self.tree.heading("away", text="Away Team")
        self.tree.heading("date", text="Date (ddmmyyyy)")
        self.tree.heading("time", text="Time")

        self.tree.column("home", width=150)
        self.tree.column("away", width=150)
        self.tree.column("date", width=120, anchor="center")
        self.tree.column("time", width=80, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.refresh_tree()

        # Button frame
        btn_frame = tk.Frame(root, bg="#f3f3f3")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Add Match", width=15, command=self.add_match, bg="#0078d4", fg="white").grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Edit Match", width=15, command=self.edit_match, bg="#ffaa00", fg="black").grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Delete Match", width=15, command=self.delete_match, bg="#d9534f", fg="white").grid(row=0, column=2, padx=5)
        tk.Button(btn_frame, text="Delete All", width=15, command=self.delete_all_matches, bg="#8b0000", fg="white").grid(row=0, column=3, padx=5)
        tk.Button(btn_frame, text="Exit", width=15, command=root.destroy, bg="#555555", fg="white").grid(row=0, column=4, padx=5)

    def refresh_tree(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for m in self.matches:
            self.tree.insert("", "end", values=(m["homeTeam"], m["awayTeam"], m["fixtureDate"], m["fixtureTime"]))

    def add_match(self):
        popup = MatchDialog(self.root, "Add Match")
        if popup.result:
            match = popup.result
            parsed_date = parse_date(match["fixtureDate"])
            if not parsed_date:
                return
            match["fixtureDate"] = parsed_date
            self.matches.append(match)
            save_matches(self.matches)
            self.refresh_tree()
            messagebox.showinfo("Success", "✅ Match added successfully!")

    def edit_match(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a match to edit.")
            return
        index = self.tree.index(selected)
        match = self.matches[index]

        popup = MatchDialog(self.root, "Edit Match", match)
        if popup.result:
            updated = popup.result
            parsed_date = parse_date(updated["fixtureDate"])
            if not parsed_date:
                return
            updated["fixtureDate"] = parsed_date
            self.matches[index] = updated
            save_matches(self.matches)
            self.refresh_tree()
            messagebox.showinfo("Success", "✅ Match updated successfully!")

    def delete_match(self):
        selected = self.tree.focus()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a match to delete.")
            return
        index = self.tree.index(selected)
        match = self.matches[index]
        confirm = messagebox.askyesno("Confirm Delete", f"Delete {match['homeTeam']} vs {match['awayTeam']}?")
        if confirm:
            self.matches.pop(index)
            save_matches(self.matches)
            self.refresh_tree()
            messagebox.showinfo("Deleted", "🗑️ Match deleted successfully!")

    def delete_all_matches(self):
        if not self.matches:
            messagebox.showinfo("No Matches", "There are no matches to delete.")
            return
        confirm = messagebox.askyesno("Confirm Delete All", "⚠️ This will delete ALL matches. Continue?")
        if confirm:
            self.matches.clear()
            save_matches(self.matches)
            self.refresh_tree()
            messagebox.showinfo("Deleted", "🗑️ All matches deleted successfully!")


class MatchDialog(simpledialog.Dialog):
    def __init__(self, parent, title, match=None):
        self.match = match or {
            "homeTeam": "",
            "awayTeam": "",
            "streamSource": "",
            "fixtureDate": "",
            "fixtureTime": ""
        }
        super().__init__(parent, title)

    def body(self, frame):
        tk.Label(frame, text="Home Team:").grid(row=0, column=0, sticky="e")
        tk.Label(frame, text="Away Team:").grid(row=1, column=0, sticky="e")
        tk.Label(frame, text="Stream Source:").grid(row=2, column=0, sticky="e")
        tk.Label(frame, text="Date (ddmmyyyy):").grid(row=3, column=0, sticky="e")
        tk.Label(frame, text="Time (HH:MM):").grid(row=4, column=0, sticky="e")

        self.home_entry = tk.Entry(frame)
        self.away_entry = tk.Entry(frame)
        self.source_entry = tk.Entry(frame)
        self.date_entry = tk.Entry(frame)
        self.time_entry = tk.Entry(frame)

        self.home_entry.grid(row=0, column=1, padx=5, pady=3)
        self.away_entry.grid(row=1, column=1, padx=5, pady=3)
        self.source_entry.grid(row=2, column=1, padx=5, pady=3)
        self.date_entry.grid(row=3, column=1, padx=5, pady=3)
        self.time_entry.grid(row=4, column=1, padx=5, pady=3)

        # Pre-fill values if editing
        self.home_entry.insert(0, self.match["homeTeam"])
        self.away_entry.insert(0, self.match["awayTeam"])
        self.source_entry.insert(0, self.match["streamSource"])
        self.date_entry.insert(0, self.match["fixtureDate"])
        self.time_entry.insert(0, self.match["fixtureTime"])

        return self.home_entry

    def apply(self):
        self.result = {
            "homeTeam": self.home_entry.get().strip(),
            "awayTeam": self.away_entry.get().strip(),
            "streamSource": self.source_entry.get().strip(),
            "fixtureDate": self.date_entry.get().strip(),
            "fixtureTime": self.time_entry.get().strip(),
        }


if __name__ == "__main__":
    root = tk.Tk()
    app = MatchManagerApp(root)
    root.mainloop()

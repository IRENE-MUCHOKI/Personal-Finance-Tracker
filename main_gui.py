import csv
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class CSV:
    """Keeps the same CSV file and column structure as the original project."""

    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initialize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            pd.DataFrame(columns=cls.COLUMNS).to_csv(cls.CSV_FILE, index=False)
        except pd.errors.EmptyDataError:
            pd.DataFrame(columns=cls.COLUMNS).to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def read_transactions(cls):
        cls.initialize_csv()
        try:
            df = pd.read_csv(cls.CSV_FILE)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=cls.COLUMNS)

        # Ensure the file has the expected columns.
        for column in cls.COLUMNS:
            if column not in df.columns:
                df[column] = ""

        if df.empty:
            return pd.DataFrame(columns=cls.COLUMNS)

        df["date"] = pd.to_datetime(
            df["date"], format=cls.FORMAT, errors="coerce"
        )
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0)
        df["category"] = df["category"].astype(str)
        df["description"] = df["description"].fillna("").astype(str)
        return df.dropna(subset=["date"])

    @classmethod
    def add_entry(cls, date, amount, category, description):
        cls.initialize_csv()
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }
        with open(cls.CSV_FILE, "a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)


class FinanceTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Personal Finance Tracker")
        self.root.geometry("1180x760")
        self.root.minsize(950, 650)
        self.root.configure(bg="#F4F1F8")

        self.purple = "#76549A"
        self.green = "#23865B"
        self.red = "#D45454"
        self.background = "#F4F1F8"
        self.white = "#FFFFFF"

        CSV.initialize_csv()
        self.build_interface()
        self.refresh_data()

    def build_interface(self):
        title = tk.Label(
            self.root,
            text="PERSONAL FINANCE TRACKER",
            font=("Arial", 22, "bold"),
            bg=self.background,
            fg=self.purple,
        )
        title.pack(pady=(18, 12))

        # Summary cards
        summary = tk.Frame(self.root, bg=self.background)
        summary.pack(fill="x", padx=20, pady=5)

        self.income_value = self.create_summary_card(
            summary, "TOTAL INCOME", self.green
        )
        self.expense_value = self.create_summary_card(
            summary, "TOTAL EXPENSES", self.red
        )
        self.balance_value = self.create_summary_card(
            summary, "CURRENT BALANCE", self.purple
        )

        # Main area
        main_area = tk.Frame(self.root, bg=self.background)
        main_area.pack(fill="both", expand=True, padx=20, pady=15)

        self.build_form(main_area)
        self.build_history_and_chart(main_area)

    def create_summary_card(self, parent, heading, color):
        card = tk.Frame(parent, bg=self.white, height=90)
        card.pack(side="left", fill="x", expand=True, padx=7)
        card.pack_propagate(False)

        tk.Label(
            card, text=heading, font=("Arial", 10, "bold"),
            bg=self.white, fg="#555555"
        ).pack(pady=(13, 4))

        value = tk.Label(
            card, text="KSh 0.00", font=("Arial", 17, "bold"),
            bg=self.white, fg=color
        )
        value.pack()
        return value

    def build_form(self, parent):
        form = tk.LabelFrame(
            parent, text=" Add Transaction ",
            font=("Arial", 12, "bold"), bg=self.white,
            padx=16, pady=16
        )
        form.pack(side="left", fill="y", padx=(0, 12))

        tk.Label(form, text="Date (DD-MM-YYYY)", bg=self.white).pack(anchor="w")
        self.date_entry = tk.Entry(form, width=27, font=("Arial", 10))
        self.date_entry.pack(pady=(5, 13))
        self.date_entry.insert(0, datetime.today().strftime(CSV.FORMAT))

        tk.Label(form, text="Amount (KSh)", bg=self.white).pack(anchor="w")
        self.amount_entry = tk.Entry(form, width=27, font=("Arial", 10))
        self.amount_entry.pack(pady=(5, 13))

        tk.Label(form, text="Category", bg=self.white).pack(anchor="w")
        self.category_box = ttk.Combobox(
            form, values=["Income", "Expense"],
            state="readonly", width=24
        )
        self.category_box.pack(pady=(5, 13))
        self.category_box.set("Expense")

        tk.Label(form, text="Description", bg=self.white).pack(anchor="w")
        self.description_entry = tk.Entry(form, width=27, font=("Arial", 10))
        self.description_entry.pack(pady=(5, 18))

        tk.Button(
            form, text="ADD TRANSACTION",
            command=self.add_transaction,
            bg=self.purple, fg="white",
            activebackground="#624381", activeforeground="white",
            font=("Arial", 10, "bold"), relief="flat",
            padx=12, pady=9, cursor="hand2"
        ).pack(fill="x")

        tk.Button(
            form, text="CLEAR FIELDS",
            command=self.clear_fields,
            bg="#E9E2F0", fg="#40334D",
            font=("Arial", 10), relief="flat",
            padx=12, pady=8, cursor="hand2"
        ).pack(fill="x", pady=(9, 0))

        tk.Label(
            form,
            text="Date format: DD-MM-YYYY\nExample: 05-11-2026",
            bg=self.white, fg="#777777",
            font=("Arial", 9), justify="left"
        ).pack(anchor="w", pady=(22, 0))

    def build_history_and_chart(self, parent):
        right = tk.Frame(parent, bg=self.background)
        right.pack(side="right", fill="both", expand=True)

        history = tk.LabelFrame(
            right, text=" Transaction History ",
            font=("Arial", 12, "bold"), bg=self.white,
            padx=10, pady=10
        )
        history.pack(fill="both", expand=True)

        table_container = tk.Frame(history, bg=self.white)
        table_container.pack(fill="both", expand=True)

        columns = ("date", "amount", "category", "description")
        self.table = ttk.Treeview(
            table_container, columns=columns,
            show="headings", height=9
        )

        headings = {
            "date": ("Date", 105),
            "amount": ("Amount (KSh)", 125),
            "category": ("Category", 100),
            "description": ("Description", 250),
        }
        for key, (label, width) in headings.items():
            self.table.heading(key, text=label)
            self.table.column(key, width=width, anchor="w")

        scrollbar = ttk.Scrollbar(
            table_container, orient="vertical", command=self.table.yview
        )
        self.table.configure(yscrollcommand=scrollbar.set)
        self.table.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        chart_frame = tk.LabelFrame(
            right, text=" Income vs Expenses ",
            font=("Arial", 12, "bold"), bg=self.white,
            padx=8, pady=8
        )
        chart_frame.pack(fill="both", expand=True, pady=(12, 0))
        self.chart_container = chart_frame

    def add_transaction(self):
        date_text = self.date_entry.get().strip()
        amount_text = self.amount_entry.get().strip()
        category = self.category_box.get()
        description = self.description_entry.get().strip()

        try:
            valid_date = datetime.strptime(date_text, CSV.FORMAT)
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror(
                "Invalid input",
                "Enter a valid date (DD-MM-YYYY) and an amount greater than zero."
            )
            return

        if category not in ("Income", "Expense"):
            messagebox.showerror("Missing category", "Choose Income or Expense.")
            return

        if not description:
            messagebox.showerror("Missing description", "Enter a description.")
            return

        CSV.add_entry(
            valid_date.strftime(CSV.FORMAT),
            amount,
            category,
            description
        )

        self.clear_fields()
        self.refresh_data()
        messagebox.showinfo("Saved", "Transaction added successfully.")

    def clear_fields(self):
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.today().strftime(CSV.FORMAT))
        self.amount_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.category_box.set("Expense")

    def refresh_data(self):
        df = CSV.read_transactions()

        for item in self.table.get_children():
            self.table.delete(item)

        if not df.empty:
            ordered = df.sort_values("date", ascending=False)
            for _, row in ordered.iterrows():
                self.table.insert(
                    "", tk.END,
                    values=(
                        row["date"].strftime(CSV.FORMAT),
                        f'{row["amount"]:,.2f}',
                        row["category"],
                        row["description"],
                    )
                )

        income = df.loc[df["category"] == "Income", "amount"].sum()
        expenses = df.loc[df["category"] == "Expense", "amount"].sum()
        balance = income - expenses

        self.income_value.config(text=f"KSh {income:,.2f}")
        self.expense_value.config(text=f"KSh {expenses:,.2f}")
        self.balance_value.config(text=f"KSh {balance:,.2f}")

        self.update_graph(df)

    def update_graph(self, df):
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        figure = Figure(figsize=(6.2, 2.6), dpi=100)
        axis = figure.add_subplot(111)

        if df.empty:
            axis.text(
                0.5, 0.5, "Add transactions to display your graph",
                ha="center", va="center", transform=axis.transAxes
            )
            axis.set_axis_off()
        else:
            daily = (
                df.groupby([df["date"].dt.date, "category"])["amount"]
                .sum()
                .unstack(fill_value=0)
                .sort_index()
            )
            if "Income" not in daily.columns:
                daily["Income"] = 0
            if "Expense" not in daily.columns:
                daily["Expense"] = 0

            axis.plot(
                daily.index, daily["Income"],
                marker="o", label="Income", color=self.green
            )
            axis.plot(
                daily.index, daily["Expense"],
                marker="o", label="Expense", color=self.red
            )
            axis.set_ylabel("Amount (KSh)")
            axis.set_xlabel("Date")
            axis.legend()
            axis.grid(True, alpha=0.25)
            figure.autofmt_xdate()

        axis.set_title("Income and Expenses Over Time")
        figure.tight_layout()

        canvas = FigureCanvasTkAgg(figure, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceTracker(root)
    root.mainloop()

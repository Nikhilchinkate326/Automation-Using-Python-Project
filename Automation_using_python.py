import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class DataAnalyzerApp:

    def __init__(self, root):
        self.root = root
        self.root.title("Corporate Data Analyzer")
        self.root.geometry("1200x750")

        self.file_path = None
        self.df = None
        self.report_df = None
        self.figure = None

        self.create_widgets()

    # ---------------- UI LAYOUT ----------------
    def create_widgets(self):

        # TOP FRAME (File Controls)
        top_frame = tk.LabelFrame(self.root, text="File Selection", padx=10, pady=10)
        top_frame.pack(fill="x", padx=10, pady=5)

        tk.Button(top_frame, text="Browse", width=12, command=self.browse_file).pack(side="left", padx=5)
        tk.Button(top_frame, text="Read", width=12, command=self.read_file).pack(side="left", padx=5)

        self.file_label = tk.Label(top_frame, text="No file selected", fg="blue")
        self.file_label.pack(side="left", padx=10)

        # INFO FRAME
        info_frame = tk.LabelFrame(self.root, text="Dataset Info", padx=10, pady=5)
        info_frame.pack(fill="x", padx=10, pady=5)

        self.info_text = tk.Text(info_frame, height=4)
        self.info_text.pack(fill="x")

        # MIDDLE FRAME (Split Left/Right)
        middle_frame = tk.Frame(self.root)
        middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # LEFT PANEL (Controls)
        left_panel = tk.LabelFrame(middle_frame, text="Report Builder", padx=10, pady=10)
        left_panel.pack(side="left", fill="y", padx=5)

        tk.Label(left_panel, text="Group By").pack(anchor="w")
        self.group_col = ttk.Combobox(left_panel, state="readonly", width=25)
        self.group_col.pack(pady=5)

        tk.Label(left_panel, text="Aggregation").pack(anchor="w")
        self.agg_method = ttk.Combobox(left_panel, state="readonly", width=25)
        self.agg_method['values'] = ["sum", "mean", "max", "min", "count", "median"]
        self.agg_method.pack(pady=5)

        tk.Label(left_panel, text="Value Column").pack(anchor="w")
        self.value_col = ttk.Combobox(left_panel, state="readonly", width=25)
        self.value_col.pack(pady=5)

        tk.Button(left_panel, text="Preview Report", width=20, command=self.generate_report).pack(pady=10)
        tk.Button(left_panel, text="Export Report", width=20, command=self.export_report).pack()

        # Chart Controls
        tk.Label(left_panel, text="Chart Type").pack(anchor="w", pady=(20, 0))
        self.chart_type = ttk.Combobox(left_panel, state="readonly", width=25)
        self.chart_type['values'] = ["Bar", "Column", "Line", "Pie"]
        self.chart_type.pack(pady=5)

        tk.Button(left_panel, text="Preview Chart", width=20, command=self.generate_chart).pack(pady=5)
        tk.Button(left_panel, text="Export Chart", width=20, command=self.export_chart).pack()

        # RIGHT PANEL (Table + Chart)
        right_panel = tk.Frame(middle_frame)
        right_panel.pack(side="right", fill="both", expand=True)

        # TABLE FRAME
        table_frame = tk.LabelFrame(right_panel, text="Report Preview")
        table_frame.pack(fill="both", expand=True, pady=5)

        self.tree = ttk.Treeview(table_frame)
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")

        self.tree.configure(yscrollcommand=scrollbar.set)

        # CHART FRAME
        self.chart_frame = tk.LabelFrame(right_panel, text="Chart Preview")
        self.chart_frame.pack(fill="both", expand=True, pady=5)

    # ---------------- FILE ----------------
    def browse_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv"), ("Excel", "*.xlsx *.xls")])
        if self.file_path:
            self.file_label.config(text=self.file_path)

    def read_file(self):
        if not self.file_path:
            messagebox.showerror("Error", "Select a file first")
            return

        try:
            if self.file_path.endswith(".csv"):
                self.df = pd.read_csv(self.file_path)
            else:
                self.df = pd.read_excel(self.file_path)

            self.display_info()
            self.detect_columns()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_info(self):
        self.info_text.delete("1.0", tk.END)
        info = f"Rows: {self.df.shape[0]} | Columns: {self.df.shape[1]}\n\n{list(self.df.columns)}"
        self.info_text.insert(tk.END, info)

    # ---------------- DETECT ----------------
    def detect_columns(self):
        text_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        num_cols = self.df.select_dtypes(include=['number']).columns.tolist()

        self.group_col['values'] = text_cols
        self.value_col['values'] = num_cols

    # ---------------- REPORT ----------------
    def generate_report(self):

        if self.df is None:
            messagebox.showerror("Error", "Read file first")
            return

        if not self.group_col.get() or not self.value_col.get() or not self.agg_method.get():
            messagebox.showerror("Error", "Select all options")
            return

        try:
            self.tree.delete(*self.tree.get_children())

            grouped = self.df.groupby(self.group_col.get())[self.value_col.get()]
            self.report_df = getattr(grouped, self.agg_method.get())().reset_index()

            self.report_df = self.report_df.sort_values(by=self.value_col.get(), ascending=False)

            self.display_table(self.report_df)

            # Clear old chart
            for widget in self.chart_frame.winfo_children():
                widget.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def display_table(self, df):
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"

        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        for row in df.values:
            self.tree.insert("", tk.END, values=list(row))

    # ---------------- EXPORT REPORT ----------------
    def export_report(self):
        if self.report_df is None:
            messagebox.showerror("Error", "No report available")
            return

        folder = os.path.dirname(self.file_path)

        self.report_df.to_excel(os.path.join(folder, "report.xlsx"), index=False)
        self.report_df.to_csv(os.path.join(folder, "report.csv"), index=False)

        messagebox.showinfo("Success", "Report exported successfully")

    # ---------------- CHART ----------------
    def generate_chart(self):

        if self.report_df is None:
            messagebox.showerror("Error", "Generate report first")
            return

        if not self.chart_type.get():
            messagebox.showerror("Error", "Select chart type")
            return

        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        fig, ax = plt.subplots(figsize=(6, 4))

        x = self.report_df.iloc[:, 0]
        y = self.report_df.iloc[:, 1]

        chart = self.chart_type.get()

        if chart == "Bar":
            ax.bar(x, y)
        elif chart == "Column":
            ax.barh(x, y)
        elif chart == "Line":
            ax.plot(x, y, marker='o')
        elif chart == "Pie":
            ax.pie(y, labels=x, autopct='%1.1f%%')

        ax.set_title("Report Chart")
        plt.xticks(rotation=45)

        self.figure = fig

        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # ---------------- EXPORT CHART ----------------
    def export_chart(self):
        if self.figure is None:
            messagebox.showerror("Error", "No chart to export")
            return

        folder = os.path.dirname(self.file_path)
        path = os.path.join(folder, "chart.png")

        self.figure.savefig(path)
        messagebox.showinfo("Success", f"Chart saved:\n{path}")


# RUN
if __name__ == "__main__":
    root = tk.Tk()
    app = DataAnalyzerApp(root)
    root.mainloop()
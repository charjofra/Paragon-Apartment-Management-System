import customtkinter as ctk
from models.user import User
from services.manager_service import ManagerService
from typing import TYPE_CHECKING
from tkinter import messagebox

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

if TYPE_CHECKING:
    from views.gui import App

class ManagerDashboard(ctk.CTkFrame):
    def __init__(self, parent: "App", user: User):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.service = ManagerService(user.user_id)

        # Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # Header
        self.header_frame = ctk.CTkFrame(self)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 0))

        label = ctk.CTkLabel(self.header_frame, text=f"Manager Dashboard — {user.full_name}",
                             font=("Arial", 20, "bold"))
        label.pack(side="left", padx=20, pady=10)

        logout_btn = ctk.CTkButton(self.header_frame, text="Logout",
                                    command=parent.logout, width=80)
        logout_btn.pack(side="right", padx=20, pady=10)

        # Tabs
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        self.tab_overview = self.tab_view.add("Overview")
        self.tab_locations = self.tab_view.add("Locations")
        self.tab_performance = self.tab_view.add("Performance")

        self.setup_overview_tab()
        self.setup_locations_tab()
        self.setup_performance_tab()

    def _clear(self, frame):
        for w in frame.winfo_children(): w.destroy()

    def _embed_figure(self, parent, fig):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
        return canvas

    # ── Overview Tab ─────────────────────────────────────────────────

    def setup_overview_tab(self):
        f = self.tab_overview
        self._clear(f)

        try:
            stats = self.service.get_aggregated_stats()
        except: 
            ctk.CTkLabel(f, text="Unable to load stats.").pack(pady=20)
            return

        # Cards
        cards = ctk.CTkFrame(f, fg_color="transparent")
        cards.pack(fill="x", padx=10, pady=10)
        
        items = [
            ("Total Locations", str(stats['locations'])),
            ("Total Units", str(stats['units'])),
            ("Avg Occupancy", f"{stats['occupancy_rate']:.1f}%"),
            ("Revenue (30d)", f"£{stats['monthly_revenue']:.2f}")
        ]

        for i, (t, v) in enumerate(items):
            c = ctk.CTkFrame(cards)
            c.grid(row=0, column=i, padx=5, sticky="nsew")
            cards.grid_columnconfigure(i, weight=1)
            ctk.CTkLabel(c, text=t, font=("Arial", 12)).pack(pady=(10,2))
            ctk.CTkLabel(c, text=v, font=("Arial", 18, "bold")).pack(pady=(0,10))

        ctk.CTkButton(f, text="Refresh", command=self.setup_overview_tab).pack(anchor="ne", padx=10)

    # ── Locations Tab ────────────────────────────────────────────────

    def setup_locations_tab(self):
        f = self.tab_locations
        self._clear(f)
        
        acts = ctk.CTkFrame(f)
        acts.pack(fill="x", pady=5)
        ctk.CTkButton(acts, text="Add New Location", command=self._add_location_popup).pack(side="left", padx=5)
        ctk.CTkButton(acts, text="Refresh", command=self.setup_locations_tab).pack(side="left", padx=5)
        
        sf = ctk.CTkScrollableFrame(f, label_text="Company Locations")
        sf.pack(fill="both", expand=True, pady=5)
        
        try: locs = self.service.get_all_locations()
        except: locs = []
        
        if not locs:
            ctk.CTkLabel(sf, text="No locations found.").pack(pady=20)
            return
            
        for l in locs:
            rf = ctk.CTkFrame(sf, height=50, fg_color=("gray85", "gray17"))
            rf.pack(fill="x", pady=6, padx=5)
            # Add city and address to the label
            label_text = f"{l['city']} - {l.get('address', 'No Address')}"
            ctk.CTkLabel(rf, text=label_text, font=("Arial", 14, "bold")).pack(side="left", padx=15, pady=10)
            ctk.CTkLabel(rf, text=f"ID: {l['location_id']}", text_color="gray").pack(side="right", padx=15, pady=10)

    def _add_location_popup(self):
        popup = ctk.CTkToplevel(self)
        popup.title("Expand Business")
        popup.geometry("400x300")
        
        ctk.CTkLabel(popup, text="New City", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        city_e = ctk.CTkEntry(popup)
        city_e.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(popup, text="Address", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10,0))
        addr_e = ctk.CTkEntry(popup)
        addr_e.pack(fill="x", padx=20, pady=5)
        
        def save():
            c, a = city_e.get().strip(), addr_e.get().strip()
            if not c:
                messagebox.showwarning("Error", "City required.", parent=popup)
                return
            try:
                self.service.create_location(c, a)
                messagebox.showinfo("Success", "Location added.", parent=popup)
                popup.destroy()
                self.setup_locations_tab()
                self.setup_overview_tab()
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=popup)
                
        ctk.CTkButton(popup, text="Create Location", command=save, fg_color="#2ecc71").pack(pady=20)

    # ── Performance Tab ──────────────────────────────────────────────

    def setup_performance_tab(self):
        f = self.tab_performance
        self._clear(f)
        
        # Select Location
        try: locs = self.service.get_all_locations()
        except: locs = []
        
        if not locs:
             ctk.CTkLabel(f, text="No locations available.").pack(pady=20)
             return
             
        sel_frame = ctk.CTkFrame(f)
        sel_frame.pack(fill="x", pady=5, padx=10)
        
        ctk.CTkLabel(sel_frame, text="Select Location:").pack(side="left", padx=5)
        
        loc_map = {f"{l['city']} ({l['address']})": l['location_id'] for l in locs}
        var = ctk.StringVar(value=list(loc_map.keys())[0])
        
        res_frame = ctk.CTkScrollableFrame(f)
        res_frame.pack(fill="both", expand=True, padx=10, pady=5)

        def load_stats(*args):
            # Clear previous result area
            for w in res_frame.winfo_children(): w.destroy()
            
            # get lid from map
            key = var.get()
            if key not in loc_map: return
            lid = loc_map[key]
            
            try:
                data = self.service.get_location_performance(lid)
            except Exception as e:
                ctk.CTkLabel(res_frame, text=f"Error: {e}").pack()
                return
                
            # Display Data
            # 1. Text Stats
            row1 = ctk.CTkFrame(res_frame, fg_color="transparent")
            row1.pack(fill="x", pady=10)
            
            stats_list = [
                f"Units: {data['total_units']}",
                f"Occ: {data['occupied_units']} ({data['occupancy_rate']:.1f}%)",
                f"Rev: £{data['revenue']:.2f}",
                f"Maint: £{data['maintenance_costs']:.2f}"
            ]
            for s in stats_list:
                c = ctk.CTkFrame(row1)
                c.pack(side="left", expand=True, fill="both", padx=5)
                ctk.CTkLabel(c, text=s, font=("Arial", 12, "bold")).pack(pady=10)
                
            # 2. Charts (Pie for Occupancy)
            fig = Figure(figsize=(5, 3), dpi=100)
            ax = fig.add_subplot(111)
            occ = data['occupied_units']
            vac = data['total_units'] - occ
            if data['total_units'] > 0:
                ax.pie([occ, vac], labels=['Occupied', 'Vacant'], colors=['#3498db', '#ecf0f1'], autopct='%1.1f%%')
                ax.set_title("Occupancy")
            else:
                ax.text(0.5, 0.5, "No Units", ha='center')
                
            c_chart = ctk.CTkFrame(res_frame, fg_color="transparent")
            c_chart.pack(pady=10, anchor="center")
            self._embed_figure(c_chart, fig)

        menu = ctk.CTkOptionMenu(sel_frame, variable=var, values=list(loc_map.keys()), command=load_stats)
        menu.pack(side="left", padx=5)
        
        ctk.CTkButton(sel_frame, text="Load", command=load_stats, width=60).pack(side="left", padx=5)
        
        # Initial load
        self.after(100, load_stats)

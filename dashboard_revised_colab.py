import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

d0 = df.copy()   # uses the cleaned data from earlier cells

MODES = ["Metro", "Tram", "Bus", "Park and Ride", "Bike Share", "E-Scooter"]
MODE_COLOURS = dict(zip(MODES, ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#6250d6"]))
WEATHER_ORDER = ["Clear", "Cloudy", "Windy", "Heatwave", "Rain", "Snow"]
LABELS = {"Average_Delay_Minutes": "Average delay (min)", "Customer_Rating": "Customer rating",
          "Transport_Mode": "Mode", "Route_Type": "Route type", "Month": "", "City": "",
          "Weather": "", "x": "", "y": "", "color": "per 10k"}
CARD = {"background": "white", "borderRadius": "10px", "padding": "12px 14px",
        "boxShadow": "0 1px 3px rgba(0,0,0,0.08)"}

def style(fig, title):
    fig.update_layout(title={"text": title, "x": 0.01, "font": {"size": 15}},
                      template="plotly_white", height=380,
                      margin={"l": 10, "r": 20, "t": 50, "b": 10},
                      legend={"title": ""})
    return fig

def kpi(id_, label, why):
    # label, value, and the whole-network value underneath for comparison
    return html.Div([html.Div(label, title=why, style={"fontSize": "12px", "color": "#52514e"}),
                     html.Div(id=id_, style={"fontSize": "22px", "fontWeight": "700"}),
                     html.Div(id=id_ + "_net", style={"fontSize": "11px", "color": "#52514e"})],
                    style={**CARD, "flex": "1", "minWidth": "118px", "padding": "10px 12px"})

def dropdown(id_, col, label):
    return html.Div([html.Div(label, style={"fontSize": "12px", "fontWeight": "600"}),
                     dcc.Dropdown(id=id_, options=sorted(d0[col].unique()), multi=True, placeholder="All")],
                    style={"flex": "1", "minWidth": "160px"})

app = Dash(__name__)
app.layout = html.Div(style={"background": "#f5f8fc", "padding": "16px", "fontFamily": "Arial"}, children=[
    html.H2("EcoMove Mobility – Performance Dashboard", style={"margin": "0"}),
    html.Div("Demand, reliability, finance, accessibility and sustainability, 2024–2025",
             style={"color": "#52514e", "marginBottom": "12px"}),

    # Filters
    html.Div(style={**CARD, "display": "flex", "gap": "12px", "flexWrap": "wrap", "marginBottom": "12px"}, children=[
        dropdown("country", "Country", "Country"),
        dropdown("city", "City", "City"),
        dropdown("mode", "Transport_Mode", "Transport mode"),
        dropdown("route", "Route_Type", "Route type"),
        dropdown("weather", "Weather", "Weather"),
        html.Div([html.Div("Day type", style={"fontSize": "12px", "fontWeight": "600"}),
                  dcc.RadioItems(id="event", options=["All", "Normal day", "Event day"], value="All", inline=True)],
                 style={"minWidth": "220px"}),
    ]),

    # KPI cards
    html.Div(style={"display": "flex", "gap": "10px", "flexWrap": "wrap", "marginBottom": "12px"}, children=[
        kpi("k_pax", "Avg passengers / record", "Demand (sales volume), not distorted by record counts"),
        kpi("k_ontime", "On-time %", "Reliability promised to passengers"),
        kpi("k_delay", "Avg delay", "Main driver of customer rating"),
        kpi("k_rating", "Customer rating", "Customer satisfaction (1–5)"),
        kpi("k_rec", "Cost recovery", "Ticket revenue as % of operating cost"),
        kpi("k_rev", "Ticket revenue", "Sales value from fares"),
        kpi("k_co2", "CO₂ saved", "Environmental benefit"),
        kpi("k_acc", "Complaints / 10k pax", "Accessibility, adjusted for passenger volume"),
    ]),

    html.Div(id="n_records", style={"fontSize": "12px", "color": "#52514e", "marginBottom": "8px"}),

    # Charts
    html.Div(style={"display": "grid", "gridTemplateColumns": "1fr", "gap": "12px"},
             children=[html.Div(dcc.Graph(id=g), style=CARD)
                       for g in ["g_trend", "g_city", "g_finance", "g_weather", "g_scatter", "g_access"]]),
])

KPIS = ["k_pax", "k_ontime", "k_delay", "k_rating", "k_rec", "k_rev", "k_co2", "k_acc"]
GRAPHS = ["g_trend", "g_city", "g_finance", "g_weather", "g_scatter", "g_access"]

def kpi_values(d):
    """The eight KPIs. Ratios of sums are used so that uneven record counts do not distort them."""
    pax, net = d["Passengers"].sum(), d["Net_Result_EUR"].sum()
    rec = d["Ticket_Revenue_EUR"].sum() / d["Operating_Cost_EUR"].sum() * 100
    rev = d["Ticket_Revenue_EUR"].sum()
    money = (f"{rev/1e6:.2f}M" if rev >= 1e6 else f"{rev/1e3:,.0f}k")
    return [f"{d['Passengers'].mean():,.0f}", f"{d['On_Time_Percentage'].mean():.1f}%",
            f"{d['Average_Delay_Minutes'].mean():.1f} min", f"{d['Customer_Rating'].mean():.2f} / 5",
            f"{rec:.1f}%", f"€{money}",
            f"{d['CO2_Saved_KG'].sum()/1000:,.0f} t",
            f"{d['Accessibility_Complaints'].sum()/pax*1e4:.1f}"], net, rec

NETWORK, _, _ = kpi_values(d0)

@app.callback(
    [Output(i, "children") for i in KPIS] + [Output(i + "_net", "children") for i in KPIS]
    + [Output(g, "figure") for g in GRAPHS] + [Output("n_records", "children")],
    [Input("country", "value"), Input("city", "value"), Input("mode", "value"),
     Input("route", "value"), Input("weather", "value"), Input("event", "value")])
def update(country, city, mode_f, route, weather, event):
    d = d0
    for col, val in [("Country", country), ("City", city), ("Transport_Mode", mode_f),
                     ("Route_Type", route), ("Weather", weather)]:
        if val:
            d = d[d[col].isin(val)]
    if event != "All":
        d = d[d["Event_Day"] == event]
    if d.empty:
        blank = style(go.Figure(), "No records match these filters")
        return ["–"] * 8 + [""] * 8 + [blank] * 6 + ["0 records selected"]

    vals, net, rec = kpi_values(d)
    vals[4] = html.Span(vals[4], style={"color": "#2a78d6" if rec >= 100 else "#e34948"})
    filtered = len(d) < len(d0)
    compare = [f"Network: {v}" if filtered else "Whole network" for v in NETWORK]
    compare[5] = compare[6] = "Total for selection"

    # 1 Time series – average demand per record, selection vs whole network
    t = d.groupby("Month")["Passengers"].mean().reset_index()
    tn = d0.groupby("Month")["Passengers"].mean().reset_index()
    f1 = go.Figure()
    if filtered:
        f1.add_trace(go.Scatter(x=tn["Month"], y=tn["Passengers"], name="Whole network",
                                line={"color": "#b7d3f6", "dash": "dash"}))
    f1.add_trace(go.Scatter(x=t["Month"], y=t["Passengers"], name="Selection", mode="lines+markers",
                            line={"color": "#2a78d6", "width": 2.5}))
    style(f1, "Average passengers per record by month").update_layout(yaxis_title="Passengers per record")
    # 2 Comparison – cities by average demand per record
    c = d.groupby("City", as_index=False).agg(P=("Passengers", "mean"), n=("Passengers", "size")).sort_values("P")
    f2 = style(px.bar(c, x="P", y="City", orientation="h", custom_data=["n"],
                      labels={"P": "Average passengers per record", "City": ""}),
               "Demand per record by city")
    f2.update_traces(marker_color="#2a78d6",
                     hovertemplate="%{y}<br>%{x:,.0f} passengers per record<br>%{customdata[0]} records<extra></extra>")
    # 3 Performance – cost recovery by mode, break-even line at 100%
    fm = d.groupby("Transport_Mode").agg(R=("Ticket_Revenue_EUR", "sum"), C=("Operating_Cost_EUR", "sum"))
    fm["rec"] = fm["R"] / fm["C"] * 100
    fm = fm.sort_values("rec").reset_index()
    f3 = go.Figure(go.Bar(x=fm["rec"], y=fm["Transport_Mode"], orientation="h", customdata=fm[["R", "C"]],
                          marker_color=["#2a78d6" if v >= 100 else "#e34948" for v in fm["rec"]],
                          hovertemplate="%{y}<br>Cost recovery %{x:.1f}%<br>Revenue €%{customdata[0]:,.0f}<br>Cost €%{customdata[1]:,.0f}<extra></extra>"))
    f3.add_vline(x=100, line_dash="dash", line_color="#0b0b0b", annotation_text="Break-even")
    style(f3, "Cost recovery by mode (revenue as % of operating cost)").update_layout(xaxis_title="%")
    # 4 Distribution – delays by weather
    w = [x for x in WEATHER_ORDER if x in d["Weather"].unique()]
    f4 = style(px.box(d, x="Weather", y="Average_Delay_Minutes", category_orders={"Weather": w}, labels=LABELS),
               "Delay distribution by weather (minutes)")
    f4.update_traces(marker_color="#2a78d6")
    # 5 Relationship – mean rating per one-minute delay band, by mode
    d = d.assign(Band=d["Average_Delay_Minutes"].clip(upper=12).round())
    s = d.groupby(["Band", "Transport_Mode"], as_index=False)["Customer_Rating"].mean()
    f5 = style(px.line(s, x="Band", y="Customer_Rating", color="Transport_Mode", markers=True,
                       color_discrete_map=MODE_COLOURS, category_orders={"Transport_Mode": MODES},
                       labels={"Band": "Average delay (minutes, rounded)", "Customer_Rating": "Mean rating",
                               "Transport_Mode": "Mode"}),
               "Mean customer rating by delay")
    # 6 Accessibility heatmap
    a = d.groupby(["Transport_Mode", "Route_Type"]).agg(c=("Accessibility_Complaints", "sum"),
                                                        p=("Passengers", "sum"))
    a = (a["c"] / a["p"] * 1e4).unstack()
    f6 = style(px.imshow(a, color_continuous_scale="Blues", text_auto=".1f", aspect="auto", labels=LABELS),
               "Accessibility complaints per 10k passengers")
    note = f"Showing {len(d):,} of {len(d0):,} records"
    return vals + compare + [f1, f2, f3, f4, f5, f6] + [note]

if __name__ == "__main__" and "STANDALONE" in globals():
    app.run(debug=False)
else:
    app.run(jupyter_mode="inline", height=3000)

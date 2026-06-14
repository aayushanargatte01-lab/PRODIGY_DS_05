
import argparse
import os
import sys
import warnings

warnings.filterwarnings("ignore")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default="US_Accidents.csv", help="Path to US_Accidents CSV")
    parser.add_argument("--outdir", default="outputs", help="Directory to save outputs")
    args = parser.parse_args()

    csv_path = args.csv
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    try:
        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import seaborn as sns
    except Exception:
        print("Missing required Python packages. Install pandas, numpy, matplotlib, seaborn.")
        sys.exit(1)

    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        sys.exit(1)

    print("Loading dataset (this may take a while)...")
    df = pd.read_csv(csv_path)

    for col in ["Start_Time", "End_Time", "Start_Time_Local", "End_Time_Local"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")

    if "Start_Time" in df.columns:
        df["hour"] = df["Start_Time"].dt.hour
        df["date"] = df["Start_Time"].dt.date
        df["weekday"] = df["Start_Time"].dt.day_name()

    if "Start_Lat" in df.columns and "Start_Lng" in df.columns:
        df_geo = df.dropna(subset=["Start_Lat", "Start_Lng"]).copy()
    else:
        df_geo = df.copy()

    if "hour" in df.columns:
        plt.figure(figsize=(8,4))
        sns.countplot(x="hour", data=df, color="#2b8cbe")
        plt.title("Accidents by Hour of Day")
        plt.xlabel("Hour")
        plt.ylabel("Number of Accidents")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "accidents_by_hour.png"), dpi=150)
        plt.close()

    if "weekday" in df.columns:
        order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        plt.figure(figsize=(7,4))
        sns.countplot(x="weekday", data=df, order=order, color="#7b3294")
        plt.title("Accidents by Weekday")
        plt.xlabel("")
        plt.ylabel("Number of Accidents")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "accidents_by_weekday.png"), dpi=150)
        plt.close()

    cond_cols = []
    for c in ["Weather_Condition","Weather_Condition.1","Wind_Direction","Precipitation(in)","Humidity(%)","Visibility(mi)"]:
        if c in df.columns:
            cond_cols.append(c)

    if "Weather_Condition" in df.columns:
        top = df["Weather_Condition"].value_counts().nlargest(10)
        plt.figure(figsize=(8,4))
        sns.barplot(x=top.values, y=top.index, palette="magma")
        plt.title("Top Weather Conditions for Accidents (top 10)")
        plt.xlabel("Count")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "top_weather_conditions.png"), dpi=150)
        plt.close()

    if set(["hour","weekday"]).issubset(df.columns):
        pivot = df.groupby(["weekday","hour"]).size().unstack(fill_value=0)
        pivot = pivot.reindex(index=order)
        plt.figure(figsize=(12,4))
        sns.heatmap(pivot, cmap="YlOrRd")
        plt.title("Accident frequency by Weekday and Hour")
        plt.xlabel("Hour")
        plt.ylabel("")
        plt.tight_layout()
        plt.savefig(os.path.join(outdir, "heatmap_weekday_hour.png"), dpi=150)
        plt.close()

    if "Start_Lat" in df_geo.columns and "Start_Lng" in df_geo.columns:
        try:
            import folium
            from folium.plugins import HeatMap

            m = folium.Map(location=[df_geo["Start_Lat"].mean(), df_geo["Start_Lng"].mean()], zoom_start=5)
            heat_data = df_geo[["Start_Lat","Start_Lng"]].dropna().values.tolist()
            HeatMap(heat_data, radius=8, blur=10).add_to(m)
            map_path = os.path.join(outdir, "accident_hotspots_map.html")
            m.save(map_path)
            print(f"Saved hotspot map to {map_path}")
        except Exception:
            print("Folium not available - skipping interactive map. Install folium to enable map output.")

    print(f"Outputs saved to {outdir}")

if __name__ == "__main__":
    main()

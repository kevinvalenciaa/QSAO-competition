import pandas as pd
import unicodedata


# Helper: normalize names (remove accents like ć → c)
def normalize_name(name):
   if isinstance(name, str):
       return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
   return name


# Load salary data
df = pd.read_excel("QSAO CASECOMP NBASALARY.xlsx")
df.columns = df.iloc[0]
df = df.iloc[1:]
df = df.rename(columns={"Player": "Name", "Tm": "Team"})


# Filter for Miami players
miami_df = df[df["Team"] == "MIA"].copy()
miami_df["2024-25"] = pd.to_numeric(miami_df["2024-25"], errors="coerce")
miami_df["Normalized Name"] = miami_df["Name"].apply(normalize_name)
miami_sorted = miami_df.sort_values(by="2024-25", ascending=False)


# Load player stats
player_stats = pd.read_excel("QSAO CASECOMP PLAYERDATA.xlsx")
player_stats_mia = player_stats[player_stats["Team"] == "MIA"].copy()
player_stats_mia["Normalized Name"] = player_stats_mia["Player"].apply(normalize_name)


# Merge using normalized names
miami_combined = miami_sorted.merge(
   player_stats_mia,
   on="Normalized Name",
   how="left",
   suffixes=("_salary", "_stats")
)


# Drop the Normalized Name column for cleanliness
miami_combined = miami_combined.drop(columns=["Normalized Name"])


# Final sort by salary
miami_combined["2024-25"] = pd.to_numeric(miami_combined["2024-25"], errors="coerce")
miami_combined = miami_combined.sort_values(by="2024-25", ascending=False)


# ------------------------------
# 🔢 Player Valuation Framework
# ------------------------------


# Convert key stat columns to numeric
for col in ["PTS", "AST", "TRB", "STL", "BLK", "TOV", "FG%", "3P%", "FT%"]:
   miami_combined[col] = pd.to_numeric(miami_combined[col], errors="coerce")


# Define valuation function
def compute_value(row):
   if pd.notnull(row["FG%"]) and pd.notnull(row["3P%"]) and pd.notnull(row["FT%"]):
       efficiency = (row["FG%"] + row["3P%"] + row["FT%"]) / 3
   else:
       efficiency = 0


   score = (
       row["PTS"] +
       1.5 * row["AST"] +
       1.2 * row["TRB"] +
       2 * row["STL"] +
       2 * row["BLK"] -
       row["TOV"]
   )
   return score * efficiency


# Apply value score and per-dollar metric
miami_combined["Value Score"] = miami_combined.apply(compute_value, axis=1)
miami_combined["Value per $M"] = miami_combined["Value Score"] / (miami_combined["2024-25"] / 1e6)


# Sort by best value
miami_combined = miami_combined.sort_values(by="Value per $M", ascending=False)


# ------------------------------
# 🧩 Archetype Classification Table
# ------------------------------


# Define archetype tags
def tag_archetype(row):
   if row["Pos"] in ["SG", "SF"] and row["3P%"] > 0.36 and row["STL"] > 0.7:
       return "3&D Wing"
   elif row["Pos"] in ["PG"] and row["AST"] > 4:
       return "Primary Ball Handler"
   elif row["Pos"] in ["PF", "C"] and row["3P%"] > 0.33 and row["BLK"] > 0.5:
       return "Stretch Big"
   elif row["Pos"] in ["C"] and row["BLK"] > 1.0 and row["TRB"] > 6:
       return "Rim Protector"
   elif row["Pos"] in ["SG", "PG"] and row["PTS"] > 15 and row["AST"] < 4:
       return "Scoring Guard"
   else:
       return "Versatile / Role Player"


# Apply archetype classification
miami_combined["Archetype"] = miami_combined.apply(tag_archetype, axis=1)


# Count of players per archetype
archetype_table = miami_combined["Archetype"].value_counts().reset_index()
archetype_table.columns = ["Archetype", "Player Count"]


# Display final outputs
print("\n🏀 Miami Heat Player Valuation:")
print(miami_combined[[
   "Name", "Pos", "2024-25", "PTS", "AST", "TRB", "STL", "BLK", "TOV",
   "FG%", "3P%", "FT%", "Value Score", "Value per $M", "Archetype"
]])


print("\n📊 Archetype Breakdown Table:")
print(archetype_table)


# Archetype breakdown with player names
archetype_summary = miami_combined.groupby("Archetype")["Name"].apply(list).reset_index()
archetype_summary.columns = ["Archetype", "Players"]


# Add player count
archetype_summary["Player Count"] = archetype_summary["Players"].apply(len)


# Display the updated breakdown
print("\n📋 Archetype Breakdown with Player Names:")
for index, row in archetype_summary.iterrows():
   print(f"\n🔹 {row['Archetype']} ({row['Player Count']} players):")
   for name in row["Players"]:
       print(f"   - {name}")

# Miami Heat 2025 Contract Status Breakdown
heat_fa_status = [
    {
        "Player": "Duncan Robinson",
        "Pos": "SF",
        "Age": 30.9,
        "2024 Salary": 18000000,
        "Status": "Player Option / $19.9M",
        "Free Agent?": "❓ Potential FA",
        "Explanation": "Becomes UFA only if he opts out of his $19.9M player option"
    },
    {
        "Player": "Davion Mitchell",
        "Pos": "PG",
        "Age": 26.5,
        "2024 Salary": 5237879,
        "Status": "Restricted FA / Bird",
        "Free Agent?": "✅ Confirmed FA (RFA)",
        "Explanation": "Restricted free agent — Heat can match outside offers"
    },
    {
        "Player": "Jaime Jaquez Jr.",
        "Pos": "SF",
        "Age": 24.1,
        "2024 Salary": 4249285,
        "Status": "Club Option / $3.9M",
        "Free Agent?": "❓ Potential FA",
        "Explanation": "Only becomes FA if Heat decline team option"
    },
    {
        "Player": "Keshad Johnson",
        "Pos": "PF",
        "Age": 23.8,
        "2024 Salary": 1340130,
        "Status": "Club Option / $2.0M",
        "Free Agent?": "❓ Potential FA",
        "Explanation": "Only becomes FA if Heat decline team option"
    },
    {
        "Player": "Isaiah Stevens",
        "Pos": "PG",
        "Age": 24.3,
        "2024 Salary": 0,
        "Status": "Two-Way RFA",
        "Free Agent?": "✅ Confirmed FA (RFA)",
        "Explanation": "Two-way contract expires; Heat can match offers"
    },
    {
        "Player": "Josh Christopher",
        "Pos": "SG",
        "Age": 23.2,
        "2024 Salary": 0,
        "Status": "Two-Way RFA",
        "Free Agent?": "✅ Confirmed FA (RFA)",
        "Explanation": "Two-way contract expires; Heat can match offers"
    },
    {
        "Player": "Dru Smith",
        "Pos": "SG",
        "Age": 27.2,
        "2024 Salary": 0,
        "Status": "Unclear",
        "Free Agent?": "❓ Likely FA",
        "Explanation": "Contract details unclear; likely expiring or two-way deal"
    }
]

# Display in table format
df = pd.DataFrame(heat_fa_status)
print("\n📋 Miami Heat - 2025 Contract Status Overview\n")
print(df[["Player", "Pos", "Age", "Status", "Free Agent?", "Explanation"]].to_string(index=False))

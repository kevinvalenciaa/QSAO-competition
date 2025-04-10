#!/usr/bin/env python3
# ========================================================================
# Miami Heat Player Analysis Script
# ========================================================================
# This script analyzes Miami Heat players by combining statistics and salary data.
# It performs the following main functions:
# 1. Loads and processes salary data from Excel
# 2. Loads and processes player statistics from Excel
# 3. Merges the data using normalized player names
# 4. Calculates player valuations based on performance metrics
# 5. Classifies players into archetypes based on stats
# 6. Provides detailed breakdown of 2025 contract statuses
# ========================================================================

import pandas as pd
import unicodedata


# ========================================================================
# DATA PREPARATION AND CLEANING FUNCTIONS
# ========================================================================

# Helper function: normalize player names (remove accents like ć → c)
# This helps with matching names across different datasets that might use
# different encodings or representations of the same name
def normalize_name(name):
   if isinstance(name, str):
       # Normalize Unicode characters and convert to ASCII (removing accents)
       return unicodedata.normalize('NFKD', name).encode('ASCII', 'ignore').decode('utf-8')
   return name


# ========================================================================
# LOADING AND PROCESSING SALARY DATA
# ========================================================================

# Load salary data from Excel file
df = pd.read_excel("QSAO CASECOMP NBASALARY.xlsx")

# Fix the headers (first row contains column names)
df.columns = df.iloc[0]
df = df.iloc[1:]  # Skip the first row since it's now used as header

# Standardize column names for consistency
df = df.rename(columns={"Player": "Name", "Tm": "Team"})


# ========================================================================
# FILTERING FOR MIAMI HEAT PLAYERS
# ========================================================================

# Extract only Miami Heat players (Team code: MIA)
miami_df = df[df["Team"] == "MIA"].copy()

# Convert salary column to numeric for proper sorting
miami_df["2024-25"] = pd.to_numeric(miami_df["2024-25"], errors="coerce")

# Add normalized names column to help with merging datasets
miami_df["Normalized Name"] = miami_df["Name"].apply(normalize_name)

# Sort players by salary (highest paid first)
miami_sorted = miami_df.sort_values(by="2024-25", ascending=False)


# ========================================================================
# LOADING AND PROCESSING PLAYER STATISTICS
# ========================================================================

# Load player statistics data from Excel file
player_stats = pd.read_excel("QSAO CASECOMP PLAYERDATA.xlsx")

# Filter for only Miami Heat players
player_stats_mia = player_stats[player_stats["Team"] == "MIA"].copy()

# Add normalized names for matching with salary data
player_stats_mia["Normalized Name"] = player_stats_mia["Player"].apply(normalize_name)


# ========================================================================
# MERGING SALARY AND STATISTICS DATA
# ========================================================================

# Combine salary and stats data using normalized names as the matching key
# Using left join to keep all salary entries, even if stats aren't found
miami_combined = miami_sorted.merge(
   player_stats_mia,
   on="Normalized Name",  # Join on normalized names to handle inconsistencies
   how="left",            # Keep all salary entries
   suffixes=("_salary", "_stats")  # Add suffixes to distinguish duplicate columns
)


# Remove the temporary normalized name column as it's no longer needed
miami_combined = miami_combined.drop(columns=["Normalized Name"])


# Ensure salary data is numeric and sort again by salary
miami_combined["2024-25"] = pd.to_numeric(miami_combined["2024-25"], errors="coerce")
miami_combined = miami_combined.sort_values(by="2024-25", ascending=False)


# ========================================================================
# PLAYER VALUATION FRAMEWORK
# ========================================================================

# Make sure all key statistics are in numeric format for calculations
for col in ["PTS", "AST", "TRB", "STL", "BLK", "TOV", "FG%", "3P%", "FT%"]:
   miami_combined[col] = pd.to_numeric(miami_combined[col], errors="coerce")


# Define a custom valuation function to assess player value
# This creates a single score based on weighted statistics and efficiency
def compute_value(row):
   # Calculate shooting efficiency if all percentages are available
   if pd.notnull(row["FG%"]) and pd.notnull(row["3P%"]) and pd.notnull(row["FT%"]):
       # Average of all shooting percentages
       efficiency = (row["FG%"] + row["3P%"] + row["FT%"]) / 3
   else:
       efficiency = 0

   # Calculate base score with weighted stats
   # - Points are counted at face value
   # - Assists are weighted 1.5x (creating shots for others)
   # - Rebounds are weighted 1.2x (extra possessions)
   # - Steals and blocks are weighted 2x (high-impact defensive plays)
   # - Turnovers are subtracted (negative impact)
   score = (
       row["PTS"] +
       1.5 * row["AST"] +
       1.2 * row["TRB"] +
       2 * row["STL"] +
       2 * row["BLK"] -
       row["TOV"]
   )
   
   # Final value = base score * efficiency (rewarding efficient production)
   return score * efficiency


# Calculate value scores for each player
miami_combined["Value Score"] = miami_combined.apply(compute_value, axis=1)

# Calculate value per million dollars of salary (efficiency metric)
miami_combined["Value per $M"] = miami_combined["Value Score"] / (miami_combined["2024-25"] / 1e6)


# Re-sort the data by value per dollar (best value first)
miami_combined = miami_combined.sort_values(by="Value per $M", ascending=False)


# ========================================================================
# PLAYER ARCHETYPE CLASSIFICATION
# ========================================================================

# Define a function to classify players into basketball archetypes
# based on their position and statistical profile
def tag_archetype(row):
   # 3&D Wing: Shooting guard or small forward with good 3PT% and steals
   if row["Pos"] in ["SG", "SF"] and row["3P%"] > 0.36 and row["STL"] > 0.7:
       return "3&D Wing"
   
   # Primary Ball Handler: Point guard with high assists
   elif row["Pos"] in ["PG"] and row["AST"] > 4:
       return "Primary Ball Handler"
   
   # Stretch Big: Power forward or center who can shoot 3s and block shots
   elif row["Pos"] in ["PF", "C"] and row["3P%"] > 0.33 and row["BLK"] > 0.5:
       return "Stretch Big"
   
   # Rim Protector: Center with high blocks and rebounds
   elif row["Pos"] in ["C"] and row["BLK"] > 1.0 and row["TRB"] > 6:
       return "Rim Protector"
   
   # Scoring Guard: Shooting guard or point guard focused on scoring
   elif row["Pos"] in ["SG", "PG"] and row["PTS"] > 15 and row["AST"] < 4:
       return "Scoring Guard"
   
   # Default category for players who don't fit other archetypes
   else:
       return "Versatile / Role Player"


# Apply the archetype classification to each player
miami_combined["Archetype"] = miami_combined.apply(tag_archetype, axis=1)


# Create a summary table of how many players are in each archetype
archetype_table = miami_combined["Archetype"].value_counts().reset_index()
archetype_table.columns = ["Archetype", "Player Count"]


# ========================================================================
# RESULTS DISPLAY - PLAYER VALUATION
# ========================================================================

# Display the detailed player valuation data
print("\n🏀 Miami Heat Player Valuation:")
print(miami_combined[[
   "Name", "Pos", "2024-25", "PTS", "AST", "TRB", "STL", "BLK", "TOV",
   "FG%", "3P%", "FT%", "Value Score", "Value per $M", "Archetype"
]])


# ========================================================================
# RESULTS DISPLAY - ARCHETYPE BREAKDOWN
# ========================================================================

# Display the count of players in each archetype
print("\n📊 Archetype Breakdown Table:")
print(archetype_table)


# Create a summary of players in each archetype category
archetype_summary = miami_combined.groupby("Archetype")["Name"].apply(list).reset_index()
archetype_summary.columns = ["Archetype", "Players"]


# Add player count column to the summary
archetype_summary["Player Count"] = archetype_summary["Players"].apply(len)


# Display a detailed breakdown of which players are in each archetype
print("\n📋 Archetype Breakdown with Player Names:")
for index, row in archetype_summary.iterrows():
   print(f"\n🔹 {row['Archetype']} ({row['Player Count']} players):")
   for name in row["Players"]:
       print(f"   - {name}")


# ========================================================================
# CONTRACT STATUS ANALYSIS FOR 2025
# ========================================================================

# Manually constructed dataset containing contract status information
# This data may not be readily available in the main dataset and requires additional research
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

# Convert the contract status data to a DataFrame for display
df = pd.DataFrame(heat_fa_status)

# Display the 2025 contract status information
print("\n📋 Miami Heat - 2025 Contract Status Overview\n")
print(df[["Player", "Pos", "Age", "Status", "Free Agent?", "Explanation"]].to_string(index=False))

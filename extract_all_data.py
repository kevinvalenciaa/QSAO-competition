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


# Load stats
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

# Display the results
print("\nMiami Heat Players with Stats and Salary Data:")
print("=" * 80)

# Define which columns to display
display_cols = ["Name", "Player", "Pos", "Age", "PTS", "TRB", "AST", "STL", "BLK"]

# Add salary columns
salary_cols = [col for col in miami_combined.columns if "20" in str(col) and "-" in str(col)]
display_cols.extend(salary_cols)

# Display the data with selected columns
with pd.option_context('display.max_columns', None, 'display.width', None):
    print(miami_combined[display_cols])

# Save the results to Excel
output_file = "Miami_Heat_Complete_Analysis.xlsx"
miami_combined.to_excel(output_file, index=False)
print(f"\nComplete dataset saved to: {output_file}")

# Summary statistics
print("\nSummary Statistics for Miami Heat Players:")
print("=" * 80)
print(f"Total players: {len(miami_combined)}")

# Salary statistics
if "2024-25" in miami_combined.columns:
    total_salary = miami_combined["2024-25"].sum()
    avg_salary = miami_combined["2024-25"].mean()
    print(f"Total 2024-25 salary commitment: ${total_salary:,.2f}")
    print(f"Average 2024-25 salary: ${avg_salary:,.2f}")

# Performance statistics
if "PTS" in miami_combined.columns:
    top_scorer = miami_combined.loc[miami_combined["PTS"].idxmax()]
    print(f"\nTop scorer: {top_scorer['Player']} - {top_scorer['PTS']} PPG")

if "TRB" in miami_combined.columns:
    top_rebounder = miami_combined.loc[miami_combined["TRB"].idxmax()]
    print(f"Top rebounder: {top_rebounder['Player']} - {top_rebounder['TRB']} RPG")

if "AST" in miami_combined.columns:
    top_assister = miami_combined.loc[miami_combined["AST"].idxmax()]
    print(f"Top assister: {top_assister['Player']} - {top_assister['AST']} APG")

"""
Bracket Matrix Scraper - Daily Seed Updates (IMPROVED)
Scrapes bracketmatrix.com for projected 2026 tournament seeds
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import sys
import urllib3
import re

# Suppress SSL warnings (needed for bracketmatrix.com)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def scrape_bracket_matrix():
    """
    Scrape Bracket Matrix for current seed projections
    Returns DataFrame with team names and projected seeds
    """
    print("🏀 Starting Bracket Matrix scraper...")
    
    url = "https://bracketmatrix.com/"
    
    try:
        # Fetch the page
        print(f"Fetching {url}...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        print(f"✓ Page fetched successfully (Status: {response.status_code})")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Save HTML for debugging if needed
        with open('debug_page.html', 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
        print("✓ Saved debug HTML to debug_page.html")
        
        teams_data = []
        
        # METHOD 1: Try to find the main bracket table
        print("\n🔍 METHOD 1: Looking for bracket table...")
        tables = soup.find_all('table')
        print(f"Found {len(tables)} tables on page")
        
        if tables:
            # Bracket Matrix typically has the bracket in the first or second table
            for idx, table in enumerate(tables[:3]):  # Check first 3 tables
                print(f"\nAnalyzing table {idx + 1}...")
                rows = table.find_all('tr')
                print(f"  - {len(rows)} rows")
                
                # Look at first few rows to understand structure
                for i, row in enumerate(rows[:5]):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    print(f"  Row {i}: {cell_texts}")
                
                # Try to extract data from this table
                for row_idx, row in enumerate(rows):
                    cells = row.find_all('td')
                    if not cells:
                        continue
                    
                    # Get all cell text
                    cell_texts = [cell.get_text(strip=True) for cell in cells]
                    
                    # Look for patterns like: seed number, team name
                    # Common formats:
                    # - "1" "Duke"
                    # - "1 Duke"
                    # - Row contains both seed and team
                    
                    for i, text in enumerate(cell_texts):
                        # Check if this cell contains a seed number (1-16)
                        if text.isdigit() and 1 <= int(text) <= 16:
                            seed = int(text)
                            # Team name is likely in the next cell or same cell
                            team_name = None
                            
                            # Try next cell
                            if i + 1 < len(cell_texts):
                                team_name = cell_texts[i + 1]
                            
                            # Or check if team name is in same cell after seed
                            if not team_name or team_name.isdigit():
                                # Try to find team in same cell
                                full_text = text
                                if len(cells) > i:
                                    full_text = cells[i].get_text(strip=True)
                                
                                # Parse formats like "1 Duke" or "1. Duke"
                                match = re.match(r'(\d+)[\.\s]+(.+)', full_text)
                                if match:
                                    seed = int(match.group(1))
                                    team_name = match.group(2).strip()
                            
                            if team_name and not team_name.isdigit() and len(team_name) > 1:
                                teams_data.append({
                                    'team': team_name,
                                    'seed': seed,
                                    'seed_str': f"{seed:02d}"
                                })
                                print(f"  ✓ Found: Seed {seed} - {team_name}")
        
        # METHOD 2: Look for specific Bracket Matrix patterns
        if not teams_data:
            print("\n🔍 METHOD 2: Looking for div/span patterns...")
            
            # Look for elements with team names
            team_elements = soup.find_all(['div', 'span'], class_=re.compile(r'team|school', re.I))
            print(f"Found {len(team_elements)} potential team elements")
            
            for elem in team_elements[:10]:  # Show first 10
                print(f"  - {elem.get_text(strip=True)}")
        
        # METHOD 3: Text-based parsing
        if not teams_data:
            print("\n🔍 METHOD 3: Looking for text patterns...")
            
            # Get all text and look for patterns like "1. Duke"
            page_text = soup.get_text()
            
            # Look for patterns: number followed by team name
            pattern = r'(?:^|\n)\s*(\d{1,2})[\.\s]+([A-Z][A-Za-z\s&\'\.]+?)(?:\s*\n|\s{2,})'
            matches = re.findall(pattern, page_text, re.MULTILINE)
            
            if matches:
                print(f"Found {len(matches)} pattern matches")
                for seed_str, team in matches[:20]:  # First 20 matches
                    if seed_str.isdigit():
                        seed = int(seed_str)
                        if 1 <= seed <= 16 and len(team.strip()) > 2:
                            team_clean = team.strip()
                            teams_data.append({
                                'team': team_clean,
                                'seed': seed,
                                'seed_str': f"{seed:02d}"
                            })
                            print(f"  ✓ Pattern match: Seed {seed} - {team_clean}")
        
        # Remove duplicates
        if teams_data:
            df = pd.DataFrame(teams_data)
            # Remove duplicates, keeping first occurrence
            df = df.drop_duplicates(subset=['team'], keep='first')
            df = df.sort_values('seed')
            
            print(f"\n✓ Successfully extracted {len(df)} unique teams")
            print("\nPreview of extracted data:")
            print(df.head(20))
            
            # Validation
            seed_counts = df.groupby('seed').size()
            print(f"\nSeeds distribution:")
            print(seed_counts)
            
            # Warning if something looks wrong
            if len(df) < 60:
                print(f"\n⚠️ WARNING: Only found {len(df)} teams. Expected ~68 for tournament.")
            
            if any(seed_counts > 8):
                print(f"\n⚠️ WARNING: Some seed numbers have >8 teams. Data might be incorrect.")
            
            return df
        else:
            print("\n❌ No team data could be extracted from any method")
            print("\n🔍 Saved page HTML to 'debug_page.html' for manual inspection")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Error fetching Bracket Matrix: {e}")
        return None
    except Exception as e:
        print(f"❌ Error parsing data: {e}")
        import traceback
        traceback.print_exc()
        return None

def save_seed_data(df, output_format='both'):
    """
    Save seed data to CSV and/or JSON
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if df is None or len(df) == 0:
        print("⚠️ No data to save")
        return False
    
    try:
        # Add metadata
        metadata = {
            'updated': timestamp,
            'source': 'bracketmatrix.com',
            'teams_count': len(df)
        }
        
        # Save as CSV
        if output_format in ['csv', 'both']:
            csv_file = 'projected_seeds_2026.csv'
            df.to_csv(csv_file, index=False)
            print(f"✓ Saved CSV: {csv_file}")
        
        # Save as JSON
        if output_format in ['json', 'both']:
            json_file = 'projected_seeds_2026.json'
            
            # Convert to list of dicts
            teams_list = df.to_dict('records')
            
            output_data = {
                'metadata': metadata,
                'teams': teams_list
            }
            
            with open(json_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            print(f"✓ Saved JSON: {json_file}")
        
        # Print summary
        print(f"\n📊 SUMMARY:")
        print(f"  Teams scraped: {len(df)}")
        print(f"  Seeds range: {df['seed'].min()} - {df['seed'].max()}")
        print(f"  Last updated: {timestamp}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving files: {e}")
        return False

def main():
    """Main execution"""
    print("=" * 60)
    print("BRACKET MATRIX SCRAPER - 2026 NCAA Tournament")
    print("=" * 60)
    print()
    
    # Scrape data
    df = scrape_bracket_matrix()
    
    # Save data
    if df is not None and len(df) > 0:
        success = save_seed_data(df, output_format='both')
        
        if success:
            print("\n✅ Scraping completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Failed to save data")
            sys.exit(1)
    else:
        print("\n❌ Scraping failed - no data extracted")
        print("Check 'debug_page.html' to see what the page looks like")
        sys.exit(1)

if __name__ == "__main__":
    main()

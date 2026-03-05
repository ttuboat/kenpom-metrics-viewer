"""
Bracket Matrix Scraper - Daily Seed Updates
Scrapes bracketmatrix.com for projected 2026 tournament seeds
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import sys
import urllib3

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
        # Note: verify=False is needed because bracketmatrix.com has SSL certificate issues
        # This is acceptable for public data scraping
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        print(f"✓ Page fetched successfully (Status: {response.status_code})")
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the main bracket table
        # Note: This selector may need adjustment based on actual site structure
        bracket_table = soup.find('table', {'class': 'matrix'}) or soup.find('table')
        
        if not bracket_table:
            print("⚠️ Could not find bracket table. Page structure may have changed.")
            print("Attempting alternative parsing...")
            # Try finding all tables
            tables = soup.find_all('table')
            print(f"Found {len(tables)} tables on page")
            if tables:
                bracket_table = tables[0]  # Use first table as fallback
        
        teams_data = []
        
        # Parse table rows
        if bracket_table:
            rows = bracket_table.find_all('tr')
            print(f"Found {len(rows)} rows in bracket table")
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                
                if len(cells) >= 2:
                    # Extract team name and seed
                    # Typical format: seed number in one column, team name in another
                    team_text = cells[0].get_text(strip=True)
                    seed_text = cells[1].get_text(strip=True) if len(cells) > 1 else ""
                    
                    # Parse seed number (e.g., "1", "2a", "11", etc.)
                    seed_num = None
                    if seed_text:
                        # Extract numeric part of seed
                        seed_clean = ''.join(filter(str.isdigit, seed_text))
                        if seed_clean:
                            seed_num = int(seed_clean)
                    
                    # Also check if seed is in team text (format like "1. Duke")
                    if not seed_num and team_text:
                        parts = team_text.split('.', 1)
                        if len(parts) == 2 and parts[0].strip().isdigit():
                            seed_num = int(parts[0].strip())
                            team_text = parts[1].strip()
                    
                    if team_text and seed_num:
                        teams_data.append({
                            'team': team_text,
                            'seed': seed_num,
                            'seed_str': f"{seed_num:02d}"
                        })
        
        if not teams_data:
            print("⚠️ No teams extracted. Trying alternative parsing method...")
            # Alternative: Look for specific patterns in page text
            text_content = soup.get_text()
            print(f"Page text preview: {text_content[:500]}")
        
        # Create DataFrame
        if teams_data:
            df = pd.DataFrame(teams_data)
            print(f"\n✓ Successfully extracted {len(df)} teams")
            print("\nPreview of extracted data:")
            print(df.head(10))
            return df
        else:
            print("\n❌ No team data could be extracted")
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
    if df is not None:
        success = save_seed_data(df, output_format='both')
        
        if success:
            print("\n✅ Scraping completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Failed to save data")
            sys.exit(1)
    else:
        print("\n❌ Scraping failed")
        sys.exit(1)

if __name__ == "__main__":
    main()

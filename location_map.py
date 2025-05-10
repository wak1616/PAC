import re
import folium

# Hardcoded coordinates for all locations
HARDCODED_COORDS = {
    "Center For Sight-University Park": (27.3881, -82.4637),
    "Center For Sight-Pelican Plaza": (27.2324, -82.4969),
    "Center For Sight-US41 Sarasota": (27.3109, -82.5298),
    "Center For Sight-Siesta Drive": (27.3027, -82.5335),
    "Center For Sight-Venice": (27.0999, -82.4159),
    "Center For Sight-Jacaranda": (27.1291, -82.3798),
    "Center For Sight-AMARA (1370 Venice)": (27.0987, -82.4142),  # Renamed from "Center For Sight-1370 Venice"
    "Center For Sight-Englewood": (26.9387, -82.3372),
    "Center For Sight-North Port": (27.0431, -82.2352),
    "Center For Sight-Kings Hwy": (27.0122, -82.0522),
    "Center For Sight-Brantley Road": (26.5617, -81.8762),
    "Center For Sight-Naples": (26.2027, -81.8039),
    "Center For Sight-San Carlos Blvd": (26.4897, -81.9392),
    "LEA-Lady Lake Sunset Plaza": (28.9172, -81.9402),
    "LEA-Leesburg": (28.8101, -81.8701),
    "LEA-Tavares": (28.8196, -81.7103),
    "LEA-The Villages": (28.9341, -81.9592),
    "LEA-Wildwood": (28.8622, -82.0592),
    "RHC-Fort Myers": (26.5661, -81.8702),
    "RHC-Naples": (26.2432, -81.7746),
    "SFEC-Cape Coral": (26.6358, -81.9747),
    "SFEC-Fort Myers": (26.5372, -81.8492),
    "SFEC-Naples": (26.2727, -81.8007),
}

# Function to handle location name mapping (for updated location names)
def update_location_name(original_name):
    """
    Updates location names if needed (for backward compatibility with markdown file).
    """
    name_mapping = {
        "Center For Sight-1370 Venice": "Center For Sight-AMARA (1370 Venice)",
    }
    return name_mapping.get(original_name, original_name)

def parse_locations(markdown_file_path="Location Reference Guide.md"):
    """
    Parses the location reference guide markdown file to extract location details.
    """
    locations = []
    current_group = None
    current_sub_group = None
    location_name_buffer = None

    try:
        with open(markdown_file_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Match main group headers (e.g., ## Center For Sight (CFS))
                group_match = re.match(r"^##\s+(.+?)\s+\((.+?)\)", line)
                if group_match:
                    current_group = group_match.group(2)
                    current_sub_group = None  # Reset sub_group when a new main group is found
                    continue

                # Match sub-group headers (e.g., ### CFS North)
                sub_group_match = re.match(r"^###\s+(.+)", line)
                if sub_group_match:
                    current_sub_group = sub_group_match.group(1)
                    continue
                
                # Match specific group headers if no abbreviation
                if not current_group and re.match(r"^##\s+(.+)", line):
                    potential_group_match = re.match(r"^##\s+(.+)", line)
                    group_name_full = potential_group_match.group(1)
                    if "Center For Sight" in group_name_full:
                        current_group = "CFS"
                    elif "Lake Eye Associates" in group_name_full:
                        current_group = "LEA"
                    elif "Retina Health Center" in group_name_full:
                        current_group = "RHC"
                    elif "Southwest Florida Eye Care" in group_name_full:
                        current_group = "SFEC"
                    else:
                        current_group = group_name_full
                    current_sub_group = None
                    continue

                # Match location name headers (e.g., #### Center For Sight-University Park)
                name_match = re.match(r"^####\s+(.+)", line)
                if name_match:
                    original_name = name_match.group(1)
                    location_name_buffer = update_location_name(original_name)
                    continue

                # Match address lines
                address_match = re.match(r"^- \*\*Address:\*\*\s+(.+)", line)
                if address_match and location_name_buffer:
                    address = address_match.group(1)
                    group_for_map = current_sub_group if current_sub_group and current_group == "CFS" else current_group
                    locations.append({
                        "name": location_name_buffer,
                        "address": address,
                        "group": group_for_map
                    })
                    location_name_buffer = None
                    continue
    
    except FileNotFoundError:
        print(f"Error: File not found at {markdown_file_path}")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []

    return locations

def create_location_map(locations, output_filename="locations_map.html"):
    """
    Creates an HTML map with markers for each location using hardcoded coordinates.
    """
    # Define color scheme for groups
    group_colors = {
        "CFS North": "red",
        "CFS Mid": "blue",
        "CFS South": "green",
        "LEA": "purple",
        "RHC": "orange",
        "SFEC": "darkred"
    }

    # Default map center (approximate center of Florida)
    map_center = [28.0, -81.5]
    
    # Create map
    location_map = folium.Map(location=map_center, zoom_start=7)

    # Add markers for each location
    missing_coords = []
    
    for loc in locations:
        name = loc['name']
        group = loc.get('group', "")
        # Default to gray if group not in color mapping
        color = group_colors.get(group, "gray")
        address = loc['address']
        
        # Get coordinates from hardcoded dictionary
        coords = HARDCODED_COORDS.get(name)
        
        if coords:
            latlon = coords
            popup_html = f"<b>{name}</b><br>Group: {group}<br>Address: {address}"
        else:
            # If no coordinates are found, place at map center and mark
            missing_coords.append(name)
            latlon = map_center
            color = "gray"
            popup_html = f"<b>{name}</b><br><span style='color:red;'>No coordinates found!</span><br>Address: {address}"
        
        # Add marker
        folium.Marker(
            location=latlon,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=name,
            icon=folium.Icon(color=color)
        ).add_to(location_map)

    # Add a legend to the map
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 200px; height: auto; 
                border:2px solid grey; z-index:9999; font-size:14px;
                background-color:white; padding: 10px;
                border-radius: 5px;
               ">
      <span style="font-weight: bold; font-size: 16px;">Legend</span><br>
      <span style="background-color:red; width:15px; height:15px; display:inline-block; border-radius:50%;"></span> CFS North<br>
      <span style="background-color:blue; width:15px; height:15px; display:inline-block; border-radius:50%;"></span> CFS Mid<br>
      <span style="background-color:green; width:15px; height:15px; display:inline-block; border-radius:50%;"></span> CFS South<br>
      <span style="background-color:purple; width:15px; height:15px; display:inline-block; border-radius:50%;"></span> LEA<br>
      <span style="background-color:orange; width:15px; height:15px; display:inline-block; border-radius:50%;"></span> RHC<br>
      <span style="background-color:darkred; width:15px; height:15px; display:inline-block; border-radius:50%;"></span> SFEC<br>
    </div>
    '''
    
    # Add the legend as an HTML element to the map
    location_map.get_root().html.add_child(folium.Element(legend_html))

    # Report any missing coordinates
    if missing_coords:
        print("Warning: The following locations have no hardcoded coordinates:")
        for name in missing_coords:
            print(f"- {name}")

    # Save map
    try:
        location_map.save(output_filename)
        print(f"Map saved to {output_filename}")
    except Exception as e:
        print(f"Error saving map: {e}")

if __name__ == "__main__":
    # Parse locations from markdown file
    locations = parse_locations()
    
    if not locations:
        print("No locations were parsed. Exiting.")
        exit()
    
    print(f"Successfully parsed {len(locations)} locations.")
    
    # Create map using hardcoded coordinates
    create_location_map(locations) 
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
    Creates an HTML map with markers for each location using hardcoded coordinates,
    and adds functionality to calculate distance from an entered ZIP code.
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
    
    # HTML and JavaScript for ZIP code input and distance calculation
    zip_input_html = """
    <div id="zipControl" style="position: fixed; top: 10px; right: 10px; z-index:1000; background-color:white; padding:10px; border:1px solid grey; border-radius:5px; box-shadow: 0 0 10px rgba(0,0,0,0.2);">
        <label for="zipCodeInput" style="font-weight:bold;">Enter Patient's ZIP Code: </label>
        <input type="text" id="zipCodeInput" placeholder="e.g., 34201" style="padding: 5px; border: 1px solid #ccc; border-radius: 3px;">
        <p id="zipErrorMessage" style="color:red; font-size:0.9em; margin-top:5px;"></p>
    </div>
    """

    # IMPORTANT: The geocoding function below uses Nominatim (OpenStreetMap).
    # This is a free service with usage policies (e.g., rate limits, no heavy use).
    # For production applications, consider using a dedicated geocoding service with an API key.
    distance_calculation_js = """
    <script>
        var zipCodeMarker = null; // To keep track of the ZIP code marker on the map
        var leafletMapInstance = null; // To store the reference to the Leaflet map object
        var distancePolyline = null; // To keep track of the distance line on the map

        function getLeafletMap() {
            if (leafletMapInstance) return leafletMapInstance;
            // Try to find the map instance Folium creates (often global like map_xxxx)
            for (const key in window) {
                if (window[key] instanceof L.Map && document.getElementById(window[key]._container.id)) {
                    leafletMapInstance = window[key];
                    return leafletMapInstance;
                }
            }
            // Fallback if the global variable isn't found directly or is obfuscated
            const mapDiv = document.querySelector('.folium-map'); // Common class for Folium map container
            if (mapDiv && mapDiv._leaflet_map) { // _leaflet_map is an internal Leaflet property
                leafletMapInstance = mapDiv._leaflet_map;
                return leafletMapInstance;
            }
            console.warn("Leaflet map object not found. ZIP marker functionality may be limited.");
            return null;
        }

        function updateZipMarker(lat, lon) {
            const map = getLeafletMap();
            if (!map) return;

            if (zipCodeMarker) {
                map.removeLayer(zipCodeMarker);
                zipCodeMarker = null;
            }

            if (lat !== undefined && lon !== undefined) {
                try {
                    var personIcon;
                    if (L.AwesomeMarkers && L.AwesomeMarkers.icon) { // Folium usually includes AwesomeMarkers
                         personIcon = L.AwesomeMarkers.icon({
                            icon: 'user',
                            prefix: 'fa', // Font Awesome
                            markerColor: 'cadetblue',
                            iconColor: 'white'
                        });
                    } else { // Fallback basic icon if AwesomeMarkers isn't available for some reason
                        console.warn("L.AwesomeMarkers.icon not available, using default marker for ZIP location.");
                        personIcon = L.icon({ // A very basic fallback
                            iconUrl: 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA8AAAAWCAYAAAAfD8YZAAAAAXNSR0IArs4c6QAAADhlWElmTU0AKgAAAAgAAYdpAAQAAAABAAAAGgAAAAAAA6ABAAMAAAABAAEAAKACAAQAAAABAAAAD6ADAAQAAAABAAAAFgAAAAAVfLGDAAAAYklEQVQoFY3RQQrAIAwEwXNUIcGLXoILEkNFfCgmhDpTqZCGuLdwHzf5g+D5AvsJ8wQGM9UPmjVIwGgqjNptxN2M1xMVR3e1U7C0B3D9K4e8n0gKHNoJ08h61gAAAABJRU5ErkJggg==', // Tiny blue dot
                            iconSize: [15, 22],
                            iconAnchor: [7, 22],
                        });
                    }
                    zipCodeMarker = L.marker([lat, lon], { icon: personIcon, zIndexOffset: 1000 }).addTo(map);
                    map.setView([lat, lon], 10); // Pan and zoom to the ZIP code location
                } catch (e) {
                    console.error("Error creating ZIP marker:", e);
                }
            }
        }

        function clearDistanceLine() {
            const map = getLeafletMap();
            if (!map) return;
            if (distancePolyline) {
                map.removeLayer(distancePolyline);
                distancePolyline = null;
            }
        }

        async function getCoordsFromZip(zip) {
            const zipErrorMsg = document.getElementById('zipErrorMessage');
            if (zipErrorMsg) zipErrorMsg.textContent = "";

            if (!zip || !/^\\d{5}$/.test(zip)) {
                if (zipErrorMsg && zip !== "") zipErrorMsg.textContent = "Please enter a valid 5-digit ZIP code.";
                updateZipMarker(undefined, undefined); // Remove marker if ZIP is invalid
                clearDistanceLine(); // Remove line if ZIP is invalid
                return null;
            }
            try {
                const response = await fetch(`https://nominatim.openstreetmap.org/search?postalcode=${zip}&country=US&format=json&limit=1`);
                if (!response.ok) {
                    console.error("Geocoding API request failed:", response.status);
                    if (zipErrorMsg) zipErrorMsg.textContent = "Geocoding service error. Try again later.";
                    updateZipMarker(undefined, undefined);
                    clearDistanceLine();
                    return null;
                }
                const data = await response.json();
                if (data && data.length > 0) {
                    const coords = { lat: parseFloat(data[0].lat), lon: parseFloat(data[0].lon) };
                    updateZipMarker(coords.lat, coords.lon); // Add/update marker
                    // Do not clear distance line here, wait for button click or new zip input
                    return coords;
                } else {
                    if (zipErrorMsg) zipErrorMsg.textContent = "ZIP code not found.";
                    updateZipMarker(undefined, undefined); // Remove marker if ZIP not found
                    clearDistanceLine(); // Remove line if ZIP not found
                    return null;
                }
            } catch (error) {
                console.error("Error fetching ZIP coordinates:", error);
                if (zipErrorMsg) zipErrorMsg.textContent = "Network error during geocoding.";
                updateZipMarker(undefined, undefined);
                clearDistanceLine();
                return null;
            }
        }

        function haversineDistance(coords1, coords2) { // coords = {lat, lon} in degrees
            function toRad(x) { return x * Math.PI / 180; }
            const R = 3958.8; // Earth radius in miles
            const dLat = toRad(coords2.lat - coords1.lat);
            const dLon = toRad(coords2.lon - coords1.lon);
            const lat1Rad = toRad(coords1.lat);
            const lat2Rad = toRad(coords2.lat);
            const a = Math.sin(dLat / 2) * Math.sin(dLat / 2) +
                      Math.cos(lat1Rad) * Math.cos(lat2Rad) *
                      Math.sin(dLon / 2) * Math.sin(dLon / 2);
            const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
            return R * c;
        }

        async function calculateAndShowDistance(markerId, locLat, locLon) {
            const zipInput = document.getElementById('zipCodeInput');
            const zipCode = zipInput.value.trim();
            const distanceDiv = document.getElementById(`distance-info-${markerId}`);
            const button = document.getElementById(`calc-button-${markerId}`);

            if (!distanceDiv || !button) {
                console.error("Popup elements not found for markerId:", markerId);
                return;
            }

            distanceDiv.innerHTML = "<em>Calculating...</em>";
            button.disabled = true;
            document.getElementById('zipErrorMessage').textContent = ""; // Clear global zip error
            clearDistanceLine(); // Clear previous line before drawing a new one

            const zipCoords = await getCoordsFromZip(zipCode);

            if (zipCoords) {
                const locCoords = { lat: locLat, lon: locLon };
                const distance = haversineDistance(zipCoords, locCoords);
                distanceDiv.innerHTML = `Distance from ${zipCode}: <strong>${distance.toFixed(2)} miles</strong>.`;
                
                // Draw the line
                const map = getLeafletMap();
                if (map) {
                    const latlngs = [
                        [locLat, locLon],       // Location coordinates
                        [zipCoords.lat, zipCoords.lon] // ZIP code coordinates
                    ];
                    try {
                         distancePolyline = L.polyline(latlngs, {color: '#ff7800', weight: 3, opacity: 0.7, dashArray: '5, 5'}).addTo(map);
                    } catch (e) {
                        console.error("Error drawing distance line:", e);
                    }
                }

            } else {
                // Error message is handled by getCoordsFromZip or if zipCoords is null
                distanceDiv.innerHTML = `<span style='color:red;'>Could not calculate distance. Check ZIP code in the input box.</span>`;
                // No line to draw if zipCoords are invalid
            }
            button.disabled = false;
        }

        document.addEventListener('DOMContentLoaded', (event) => {
            // Initialize map instance early
            getLeafletMap();

            const zipInput = document.getElementById('zipCodeInput');
            if (zipInput) {
                zipInput.addEventListener('input', async () => {
                    const zipCode = zipInput.value.trim();
                    const zipErrorMsg = document.getElementById('zipErrorMessage');
                    if (zipErrorMsg) zipErrorMsg.textContent = ""; // Clear previous error on new input

                    // Reset distance displays in popups
                    const allDistanceDivs = document.querySelectorAll('[id^="distance-info-"]');
                    allDistanceDivs.forEach(div => {
                        if (div.innerHTML.includes("miles") || div.innerHTML.includes("Calculating") || div.innerHTML.includes("Could not calculate")) {
                             div.innerHTML = "<span style=\\'color: #e09600;\\'>ZIP changed. Click button to recalculate.</span>";
                        }
                    });
                    const allCalcButtons = document.querySelectorAll('[id^="calc-button-"]');
                    allCalcButtons.forEach(btn => btn.disabled = false);
                    clearDistanceLine(); // Clear line when zip input changes

                    if (/^\\d{5}$/.test(zipCode)) {
                        await getCoordsFromZip(zipCode); // This will geocode and attempt to place the marker
                    } else {
                        if (zipCode !== "") { // Only show error if not empty and invalid
                           if (zipErrorMsg) zipErrorMsg.textContent = "Enter a valid 5-digit ZIP.";
                        }
                        updateZipMarker(undefined, undefined); // Remove marker if ZIP is invalid or cleared
                        clearDistanceLine(); // Also clear line if zip becomes invalid
                    }
                });
            }
        });
    </script>
    """

    for idx, loc in enumerate(locations):
        name = loc['name']
        group = loc.get('group', "")
        color = group_colors.get(group, "gray") # Default to gray if group not in color mapping
        address = loc['address']
        marker_id_str = f"marker-{idx}"
        
        coords = HARDCODED_COORDS.get(name)
        
        popup_html_content = ""

        if coords:
            latlon = coords
            popup_html_content = f"""
<b>{name}</b><br>
Group: {group}<br>
Address: {address}<br>
<div id="distance-info-{marker_id_str}" style="margin-top:5px; margin-bottom:5px;"></div>
<button id="calc-button-{marker_id_str}" onclick="calculateAndShowDistance('{marker_id_str}', {latlon[0]}, {latlon[1]})" style="margin-top:5px; padding: 3px 7px; font-size:0.9em; cursor:pointer; border:1px solid #007bff; background-color:#007bff; color:white; border-radius:3px;">Calculate distance from ZIP</button>
"""
        else:
            missing_coords.append(name)
            latlon = map_center # Place at map center if no coords
            color = "gray" # Mark as gray
            popup_html_content = f"<b>{name}</b><br><span style='color:red;'>No coordinates found for this location!</span><br>Address: {address}"
        
        folium.Marker(
            location=latlon,
            popup=folium.Popup(popup_html_content, max_width=350),
            tooltip=name,
            icon=folium.Icon(color=color)
        ).add_to(location_map)

    # Add the ZIP code input box to the map
    location_map.get_root().html.add_child(folium.Element(zip_input_html))
    
    # Add the JavaScript for distance calculation to the map
    location_map.get_root().html.add_child(folium.Element(distance_calculation_js))

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
    create_location_map(locations, output_filename="docs/locations_map.html") 
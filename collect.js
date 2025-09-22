// collect.js
const fs = require("fs");

// CONFIG
const STEP = 1; // Degree step for lat/lng
const LIMIT = 10; // Max coordinates checked per run
const RETRY_LIMIT = 3; // Retry per coordinate on failure

// Load last progress
let progress = { lat: -90, lng: -180 };
if (fs.existsSync("progress.json")) {
  progress = JSON.parse(fs.readFileSync("progress.json", "utf8"));
}

// Load existing coordinates
let coordinates = [];
if (fs.existsSync("coordinates.json")) {
  coordinates = JSON.parse(fs.readFileSync("coordinates.json", "utf8"));
}

// Ensure API key exists
const API_KEY = process.env.GOOGLE_MAPS_API_KEY;
if (!API_KEY) {
  console.error("Error: GOOGLE_MAPS_API_KEY not set in environment variables.");
  process.exit(1);
}

// Check one coordinate via Street View Metadata API
async function checkCoordinate(lat, lng) {
  const url = `https://maps.googleapis.com/maps/api/streetview/metadata?location=${lat},${lng}&radius=50000&key=${API_KEY}`;

  for (let attempt = 1; attempt <= RETRY_LIMIT; attempt++) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data; // returns full JSON including location.lat/lng and status
    } catch (err) {
      console.warn(
        `Attempt ${attempt} failed for ${lat},${lng}: ${err.message}`
      );
      if (attempt < RETRY_LIMIT) await new Promise((r) => setTimeout(r, 1000)); // retry delay
    }
  }
  return false;
}

// Main loop
async function run() {
  let { lat, lng } = progress;
  let checked = 0;
  let newCount = 0;

  while (lat <= 90 && checked < LIMIT) {
    while (lng <= 180 && checked < LIMIT) {
      const result = await checkCoordinate(lat, lng);

      if (result && result.status === "OK") {
        const panoLat = Number(result.location.lat.toFixed(6));
        const panoLng = Number(result.location.lng.toFixed(6));

        const coord = { lat: panoLat, lng: panoLng };
        coordinates.push(coord);
        newCount++;
        if (newCount >= LIMIT) {
          try {
            fs.writeFileSync(
              "coordinates.json",
              JSON.stringify(coordinates, null, 2)
            );
            console.log(`Saved ${coordinates.length} coordinates to file.`);
          } catch (err) {
            console.error("❌ Error writing to JSON file", err);
          }
          newCount = 0;
        }

        console.log(`✅ Found panorama at: ${panoLat},${panoLng}`);
      } else if (result) {
        console.log(`❌ No imagery at: ${lat},${lng}`);
      }

      checked++;
      // Save progress after each coordinate
      progress = { lat, lng };
      fs.writeFileSync("progress.json", JSON.stringify(progress, null, 2));

      lng += STEP;
    }

    if (lng > 180) {
      lng = -180;
      lat += STEP;
    }
  }

  console.log(`Run complete. Checked ${checked} coordinates. Progress saved.`);
}

run();

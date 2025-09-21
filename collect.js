// collect.js
const fs = require("fs");

// CONFIG
const STEP = 1; // Degree step for latitude & longitude
const LIMIT = 10000; // Max coordinates checked per run
const RETRY_LIMIT = 3; // Retry per coordinate on failure

// Load last progress
let progress = { lat: -90, lng: -180 };
if (fs.existsSync("progress.json")) {
  progress = JSON.parse(fs.readFileSync("progress.json", "utf8"));
}

// Load existing coordinates
let coordinates = [];
if (fs.existsSync("coordinates.json")) {
  coordinates = fs
    .readFileSync("coordinates.json", "utf8")
    .split("\n")
    .filter(Boolean)
    .map(JSON.parse);
}

const API_KEY = process.env.GOOGLE_MAPS_API_KEY;
if (!API_KEY) {
  console.error("Error: GOOGLE_MAPS_API_KEY not set in environment variables.");
  process.exit(1);
}

// Check one coordinate
async function checkCoordinate(lat, lng) {
  const url = `https://maps.googleapis.com/maps/api/streetview/metadata?location=${lat},${lng}&radius=50000&key=${API_KEY}`;
  for (let attempt = 1; attempt <= RETRY_LIMIT; attempt++) {
    try {
      const res = await fetch(url);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      return data.status === "OK";
    } catch (err) {
      console.warn(
        `Attempt ${attempt} failed for ${lat},${lng}: ${err.message}`
      );
      if (attempt < RETRY_LIMIT) await new Promise((r) => setTimeout(r, 1000)); // wait before retry
    }
  }
  return false;
}

async function run() {
  let { lat, lng } = progress;
  let checked = 0;

  while (lat <= 90 && checked < LIMIT) {
    while (lng <= 180 && checked < LIMIT) {
      const ok = await checkCoordinate(lat, lng);
      if (ok) {
        const coord = { lat, lng };
        coordinates.push(coord);
        fs.appendFileSync("coordinates.json", JSON.stringify(coord) + "\n");
        console.log(`✅ Found: ${lat},${lng}`);
      }

      checked++;
      // Save progress after each coordinate
      fs.writeFileSync("progress.json", JSON.stringify({ lat, lng }, null, 2));

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

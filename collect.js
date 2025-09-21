// collect.js
const fs = require("fs");

const API_KEY = process.env.GOOGLE_MAPS_API_KEY;
const STEP = 1; // degree step
const LIMIT = 10000; // max checks per run

// Load progress
let progress = { lat: -90, lng: -180 };
if (fs.existsSync("progress.json")) {
  progress = JSON.parse(fs.readFileSync("progress.json", "utf8"));
}

// Load existing coordinates
let coordinates = [];
if (fs.existsSync("coordinates.json")) {
  coordinates = JSON.parse(fs.readFileSync("coordinates.json", "utf8"));
}

async function checkCoordinate(lat, lng) {
  const url = `https://maps.googleapis.com/maps/api/streetview/metadata?location=${lat},${lng}&radius=50000&key=${API_KEY}`;
  const res = await fetch(url);
  const data = await res.json();
  return data.status === "OK";
}

async function run() {
  let count = 0;
  let { lat, lng } = progress;

  while (lat <= 90 && count < LIMIT) {
    while (lng <= 180 && count < LIMIT) {
      const ok = await checkCoordinate(lat, lng);
      if (ok) {
        coordinates.push({ lat, lng });
        console.log(`✅ Found: ${lat}, ${lng}`);
      }
      count++;
      lng += STEP;
    }
    if (lng > 180) {
      lng = -180;
      lat += STEP;
    }
  }

  // Save coordinates & progress
  fs.writeFileSync("coordinates.json", JSON.stringify(coordinates, null, 2));
  fs.writeFileSync("progress.json", JSON.stringify({ lat, lng }, null, 2));

  console.log(`Run complete. Checked ${count} coordinates. Progress saved.`);
}

run();

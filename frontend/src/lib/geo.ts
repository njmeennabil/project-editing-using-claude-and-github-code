/** Ask the browser for the phone's location. */
export function locateMe(onFound: (lat: string, lon: string) => void, onError: (message: string) => void) {
  if (typeof navigator === "undefined" || !("geolocation" in navigator)) {
    onError("This browser can't share your location. Choose a division instead.");
    return;
  }
  navigator.geolocation.getCurrentPosition(
    (pos) => onFound(pos.coords.latitude.toFixed(4), pos.coords.longitude.toFixed(4)),
    (err) =>
      onError(
        err.code === err.PERMISSION_DENIED
          ? "Location access was not allowed. Choose a division instead, or allow location in your browser settings."
          : "Your location could not be found. Choose a division instead.",
      ),
    { enableHighAccuracy: false, timeout: 15000, maximumAge: 600000 },
  );
}

/** "2026-03-02" -> "2 Mar 2026" (same result on server and phone). */
export function niceDate(iso: string) {
  return new Date(`${iso}T00:00:00Z`).toLocaleDateString("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });
}

/*
    This script is used by index.html for navigation to the reminders page.

    The View Reminders button needs to send the browser's device ID to Flask so
    the backend can show only the reminders connected to that browser/device.

    When the user clicks View Reminders, this script gets or creates the device ID
    from localStorage and redirects the user to /reminders with the device_id in
    the URL query string.
*/

function getDeviceId() {
    let deviceId = localStorage.getItem("smartReminderDeviceId");

    if (!deviceId) {
        deviceId = "device-" + crypto.randomUUID();
        localStorage.setItem("smartReminderDeviceId", deviceId);
    }

    return deviceId;
}

function goToReminders() {
    const deviceId = getDeviceId();
    window.location.href = "/reminders?device_id=" + encodeURIComponent(deviceId);
}
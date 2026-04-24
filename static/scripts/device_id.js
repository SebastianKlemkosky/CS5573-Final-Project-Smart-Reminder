/*
    This script handles the browser/device ID for the Smart Reminder app.

    It checks the browser's localStorage for an existing Smart Reminder device ID.
    If one does not exist, it creates a new random ID and saves it in localStorage.

    This helps the app identify reminders from the same browser without requiring
    a full login system. The ID can be placed into a hidden form field so Flask can
    save reminders in SQLite under that browser/device.

    This script is mainly intended for pages that need access to the device ID.
*/



function getDeviceId() {
    let deviceId = localStorage.getItem("smartReminderDeviceId");

    if (!deviceId) {
        deviceId = "device-" + crypto.randomUUID();
        localStorage.setItem("smartReminderDeviceId", deviceId);
    }

    return deviceId;
}

function setDeviceIdInput() {
    const deviceInput = document.getElementById("device_id");

    if (deviceInput) {
        deviceInput.value = getDeviceId();
    }
}

window.onload = setDeviceIdInput;
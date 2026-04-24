/*
    This script is used by add_reminder.html.

    It has two main jobs. First, it gets or creates a browser/device ID using
    localStorage and places that ID into the hidden device_id form field. This
    lets Flask save the reminder under that browser/device in the SQLite database.

    Second, it controls the dynamic reminder form. When the user selects a reminder
    type, such as General, Health, Fitness, Work, or Relationships, the script hides
    the other form sections and only shows the fields for the selected type.

    This keeps all reminder types on one page instead of needing separate pages for
    each category.
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

function showFormFields() {
    let selectedType = document.getElementById("form_type").value;

    let allSections = document.querySelectorAll(".extra-fields");
    allSections.forEach(function(section) {
        section.style.display = "none";
    });

    let selectedSection = document.getElementById(selectedType + "-fields");
    if (selectedSection) {
        selectedSection.style.display = "block";
    }
}

window.onload = function() {
    setDeviceIdInput();
    showFormFields();
};
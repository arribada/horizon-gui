let getSelectedDevices = function () {

    let selected = Array.from(document.querySelectorAll(".deviceHeader[data-active]"));

    return selected.map(function (element) {

        return element.getAttribute("data-device");

    });

};

document.querySelectorAll(".deviceHeader").forEach(function (element) {

    let device = element.getAttribute("data-device");
    let deviceReportCells = document.querySelectorAll("tr [data-device='" + device + "']");

    element.addEventListener("click", function () {

        let isActive = element.getAttribute("data-active");

        deviceReportCells.forEach(function (tableCell) {

            if (!isActive) {

                tableCell.setAttribute("data-active", "true");

            } else {

                tableCell.removeAttribute("data-active");

            }

        })

        populateButtons();

    });

});

let populateButtons = function () {

    let selected = getSelectedDevices();

    let bulkActions = Array.from(document.querySelectorAll("[data-bulk='true']"));

    let singleActions = Array.from(document.querySelectorAll("[data-bulk='false']"));


    if (selected.length) {

        bulkActions.forEach(function (element) {

            element.removeAttribute("disabled");

        });

        if (selected.length === 1) {

            singleActions.forEach(function (element) {

                element.removeAttribute("disabled");

            });

        } else {

            singleActions.forEach(function (element) {

                element.setAttribute("disabled", true);

            });

        }

    } else {

        Array.from(document.querySelectorAll(".actions select, .actions button")).forEach(function (element) {

            element.setAttribute("disabled", true);

        });


    }

};

populateButtons();

document.querySelectorAll("input, select").forEach(function (element) {

    element.addEventListener("change", function (e) {

        if (e.target.value) {

            e.target.setAttribute("data-changed", "true");

        } else {

            e.target.removeAttribute("data-changed");

        }


    });

});

let triggerAction = function (e) {

    if (!getSelectedDevices().length) {

        return false;

    }

    let element = e.currentTarget;

    if (element.hasAttribute("disabled")) {

        return false;

    }

    let value;

    if (element.tagName.toLowerCase() === "select") {

        value = element.value;

        if (!value) {

            return false;

        }

    }

    let action = element.getAttribute("data-action");
    let selectedDevices = getSelectedDevices();

    let query = "";

    selectedDevices.forEach(function (device) {

        query += "devices[]=" + device + "&";

    });

    let targetURL = action + "?" + query;

    // Add value for select boxes

    if (value) {

        targetURL += "&value=" + value;

    }

    if (element.hasAttribute("data-warn") ) {
        let warning = "";
        if (element.hasAttribute("data-usermessage") ){
            warning = element.getAttribute("data-usermessage") + " " + selectedDevices.toString() + "";

        } else {

            warning = "Apply " + element.innerHTML + " to " + selectedDevices.toString() + "?";
        }

        showConfirm(warning, targetURL);

        return false;

    }
     else {

        document.location.href = targetURL;

    }

};

let showConfirm = function (warning, targetURL) {

    // Remove existing popup

    if (document.getElementById("popup")) {

        document.getElementById("popup").outerHTML = "";

    }

    let popup = `<section id="popup" class="are-you-sure">
                    <div class="pop-up navy">
                        <p>${warning}</p>
                        <div class="pop-up-buttons">
                            <button onclick="document.location.href='${targetURL}'">Yes</button>
                            <button onclick="document.getElementById('popup').outerHTML = ''">No</button>
                        </div>
                    </div>
                </section>`;

    document.querySelector("main").insertAdjacentHTML("afterbegin", popup);

};

let uploadPreset = function () {

    document.querySelectorAll("[data-preset]").forEach(function (element) {

        element.style.display = "none";

    });

    document.querySelector("[data-preset='upload']").style.display = "block";

};

let loadPreset = function (presetID) {

    Array.from(document.querySelectorAll("[data-preset-menu]")).forEach(function (menu) {

        if (menu.getAttribute("data-preset-menu") === presetID) {

            menu.setAttribute("data-selected", "true");

        } else {

            menu.removeAttribute("data-selected");

        }

    });

    document.querySelectorAll("[data-preset]").forEach(function (element) {


        if (element.getAttribute("data-preset") === presetID) {

            element.style.display = "block";

        } else {

            element.style.display = "none";

        }

    });

};

let deletePreset = function () {

    let preset = document.querySelector("[data-preset-menu][data-selected]").getAttribute("data-preset-menu");

    if (preset) {

        showConfirm("Are you sure you want to delete " + preset + " ?", "/presets?delete=" + preset);

    }

};

function displayLoadingPopup() {
    document.getElementById("loadingPopup").style.display = "block";
}


// Burger Menu

function toggleBurger() {
    //document.body.toggleAttribute("data-open");
}



function formatDate(date) {
    var d = new Date(date),
        month = '' + (d.getMonth() + 1),
        day = '' + d.getDate(),
        year = d.getFullYear();

    if (month.length < 2) 
        month = '0' + month;
    if (day.length < 2) 
        day = '0' + day;

    return [year, month, day].join('-');
}
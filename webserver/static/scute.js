let getSelectedDevices = function () {

    let selected = Array.from(document.querySelectorAll(".deviceHeader[data-active]"));

    return selected.map(function (element) {

        return element.getAttribute("data-device");

    });

};

document.querySelectorAll(".clickSelect").forEach(function (element) {

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

        });

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

                if (!element.classList.contains('notHidden')) {
                    element.setAttribute("disabled", true);
                }

            });

        }

    } else {

        Array.from(document.querySelectorAll(".actions select, .actions button")).forEach(function (element) {

            if (!element.classList.contains('notHidden')) {
                element.setAttribute("disabled", true);
            }

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

    // if (element.tagName.toLowerCase() === "select") {  // no longer a select..
    if (element.classList.contains('actionButton')){

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
    

    if (element.hasAttribute("data-warn") || element.hasAttribute("data-usermessage")) {

        let devicesDisplay = selectedDevices.join(', ');

        let warning = "Run " + element.innerHTML + " for " + devicesDisplay + "?";

        if(element.hasAttribute("data-usermessage")){
            let message = element.getAttribute("data-usermessage");
            if (selectedDevices.length === 1){
                message = message.replace('(s)', '');
            } else {
                message = message.replace('(s)', 's');
            }
            
            warning = message + '<br />' +  devicesDisplay; 

        }

        showConfirm(warning, targetURL);

        return false;

    } else {

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
                            <button onclick="okClickProcess('${targetURL}')">Yes</button>
                            <button onclick="document.getElementById('popup').outerHTML = ''">No</button>
                        </div>
                    </div>
                </section>`;

    document.querySelector("main").insertAdjacentHTML("afterbegin", popup);

};

let okClickProcess = function (targetURL){
    console.log(targetURL);
    // close the poptp this came from and redirect the page
    document.getElementById('popup').outerHTML = '';
    document.location.href = targetURL;

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
    document.body.toggleAttribute("data-open");
}
toggleBurger();

function formatDateTime(date) {
    var d = new Date(date),
        month = (d.getMonth() + 1).toString(),
        day = d.getDate().toString(),
        year = d.getFullYear().toString(),
        hour = d.getHours().toString(),
        minute = d.getMinutes().toString();

    return year + '-' + month.padStart(2, '0') + '-' + day.padStart(2, '0') + ' ' + hour.padStart(2, '0') + ':' + minute.padStart(2, '0');
}

function getFieldName(field){
    
    fieldName = field.id.split(".");
    return " - " + fieldName[1] + " (" + fieldName[0] + ") \n";
}

function confirmSubmitConfig(theForm) {
    
    lastHubTime = document.getElementById("time-hub").innerHTML;
    deviceIDString = document.getElementById("deviceIDString").innerHTML;


    changedFields = document.querySelectorAll("[data-changed]");

    if (changedFields.length == 0){

        message = 'No fields have been changed. \n\n';

    } else {
        
        message = changedFields.length + ' fields have changed. \n';

        fieldList =  Object.values(changedFields).map(getFieldName); // returns array 

        message += fieldList.join('') +  '\n\n'; // avoid the auto joining ','

    }

    message += 'Save This Config to Device "' + deviceIDString + '"? \n\nThe device time will be set to the Hub Time: ' + lastHubTime + ' \nHub Time can be updated in the SCRIPTS section.';


    return confirm(message);

}

function showHideDiv(targetID) {

    let x = document.getElementById(targetID);
    if (x.style.display === "none" || x.style.display === "") {
        x.style.display = "block";
    } else {
        x.style.display = "none";
    }

}


if(document.getElementById("warningFieldsChanged")){

    checkForChanges();

}

function checkForChanges(){
    changedFields = document.querySelectorAll("[data-changed]");
    let x = document.getElementById('warningFieldsChanged');
    if (changedFields.length != 0){
        x.style.display = "block";
        
    } else {
        x.style.display = "none";

    }
    setTimeout(checkForChanges, 1000);
}
   
    
    

let getSelectedDevices = function () {

    let selected = Array.from(document.querySelectorAll(".deviceHeader[data-active]"));

    return selected.map(function (element) {

        return element.getAttribute("data-device");

    });

};


document.querySelectorAll(".deviceHeader").forEach(function (element) {

    element.addEventListener("click", function (e) {

        let element = e.currentTarget;

        if (element.getAttribute("data-active")) {

            element.removeAttribute("data-active");

        } else {

            element.setAttribute("data-active", "true");

        }

        let selected = getSelectedDevices();

        let bulkActions = Array.from(document.querySelectorAll("[data-bulk='true']"));

        let singleActions = Array.from(document.querySelectorAll("[data-bulk='false']"));

        
        // cris messing about...
        if (element.getAttribute("data-onclick")) {
            //https://stackoverflow.com/questions/359788/how-to-execute-a-javascript-function-when-i-have-its-name-as-a-string

            window[element.getAttribute("data-onclick")](selected);

        }


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

            Array.from(document.querySelectorAll(".buttons-wrapper select, .buttons-wrapper button")).forEach(function (element) {

                element.setAttribute("disabled", true);

            });


        }

    });

});

document.querySelectorAll("input, select").forEach(function (element) {

    element.addEventListener("change", function (e) {

        if (e.target.value) {

            e.target.setAttribute("data-changed", "true");

        } else {

            e.target.removeAttribute("data-changed");

        }


    });

});

document.querySelectorAll("[data-action]").forEach(function (element) {

    element.addEventListener("click", function () {

        if (element.hasAttribute("disabled")) {

            return false;

        }

        let action = element.getAttribute("data-action");
        let selectedDevices = getSelectedDevices();

        let query = "";

        selectedDevices.forEach(function (device) {

            query += "devices[]=" + device + "&";

        });

        

        let targetURL = action + "?" + query;

        if (element.hasAttribute("data-warn")) {

            let warning = "Apply " + element.innerHTML + " to " + selectedDevices.toString() + "?";

            showConfirm(warning, targetURL);

            return false;

        } else {

            document.location.href = targetURL;

        }


    });

});

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


let savePreset = function () {

    let values = {};

    document.querySelectorAll("input, select").forEach(function (element) {

        // Ignore if exclude from preset

        if (element.parentElement.getAttribute("data-exlude-from-preset")) {

            return false;

        }

        let name = element.getAttribute("name");
        let value;

        if (element.tagName === "SELECT") {

            value = element.options[element.selectedIndex].value;

        } else {

            value = element.value;

        }

        values[name] = value;

    });

    alert("Not yet implemented but data will be " + JSON.stringify(values));

};

let loadPreset = function (presetID) {

    removeThisClassFrom('preset-list-item-selected', 'li');
    document.getElementById("preset-list-item-" + presetID).classList.add('preset-list-item-selected');

    // document.getElementById("presetDeleteWrapper").style.visibility = 'visible';
    document.getElementById("presetForm").style.visibility = 'visible';
    document.getElementById('presetHeading').textContent = presetList[presetID].name;
    // document.getElementById('presetDate').textContent = presetList[presetID].date;
    // document.getElementById("presetName").value = presetList[presetID].name;
    // document.getElementById("preseDescription").value = presetList[presetID].description;
    // document.getElementById("presetFields").value = JSON.stringify(presetList[presetID].presets);


};

let addPreset = function () {

    removeThisClassFrom('preset-list-item-selected', 'li');

    document.getElementById("presetDeleteWrapper").style.visibility = 'hidden';
    document.getElementById("presetForm").style.visibility = 'visible';
    document.getElementById('presetHeading').textContent = "Add Preset";
    document.getElementById('presetDate').textContent = '';
    document.getElementById("presetName").value = '';
    document.getElementById("preseDescription").value = '';
    document.getElementById("presetFields").value = '';

};

let deletePreset = function () {

    removeThisClassFrom('preset-list-item-selected', 'li');

    alert("Not yet implemented: deletePreset");

};


let removeThisClassFrom = function (thisClass, thisElement) {

    var target = document.querySelectorAll(thisElement + "." + thisClass);

    for (var i = 0; i < target.length; i++) {
        target[i].classList.remove(thisClass);
    }
};

hbnb = {
    // storage area for data obtained from API calls
    "data": {
        "places": [],
        "amenities": []
    },

    // messages to be displayed in website. e.g. errors, notifications, etc
    "msg": {
        "error": {
            "api": {
                "generic": "Unable to retrieve API data. Please ensure the server is active.",
            }
        }
    },

    showError: function(msg) {
        document.getElementById("error").innerHTML = msg
        document.getElementById("error").setAttribute('class', 'show');
    },
    hideLoader: function() {
        document.getElementById("loader").setAttribute('class', 'hide');
    },

    // general function used to load Places + Amenities data for Index page
    loadIndexData: async function() {
        const placesUrl = "http://localhost:5000/api/v1/places/";
        const amenitiesUrl = "http://localhost:5000/api/v1/amenities/";

        try {
            const placesResponse = await fetch(placesUrl);
            const amenitiesResponse = await fetch(amenitiesUrl);

            // Store the data I got from the async API calls
            hbnb.data.places = await placesResponse.json()
            hbnb.data.amenities = await amenitiesResponse.json()
        } catch(error) {
            // console.error("Error:", error);
            hbnb.showError(hbnb.msg.error.api.generic)
            throw new Error(error);
        }
    },
    placesPopulate: function(dataSource = hbnb.data.places) {
        const cardsListTag = document.querySelector("#places-list > .cards")
        cardsListTag.innerHTML = ""

        // Use innerHTML to add the HTML content to the page
        for (let place of dataSource) {
            // NOTE: Consider storing the HTML below elsewhere instead of within this function
            // e.g. hbnb.html.places.card
            amenities_spans = ``
            if (place.amenities.length > 0) {
                for (let amenity of place.amenities) {
                    amenities_spans += `<span class="` + amenity.toLowerCase().replace(" ", "-") + `"></span>`
                }
            }

            cardsListTag.innerHTML += `
                <li class="card">
                    <div>
                        <div class="title">` + place.title + `</div>
                        <div class="price">$` + place.price + `</div>
                        <div class="image"></div>
                        <div class="desc">` + place.description + `</div>
                        <div class="coords">
                            <span><b>Lat: </b>` + place.latitude + `</span>
                            <span><b>Lon: </b>` + place.longitude + `</span>
                        </div>
                        <div class="amenities">` + amenities_spans + `</div>
                    <div>
                </li>
            `;
        }
    },
    filterPriceOptionsPopulate: function() {
        let options = [50, 100, 250, 500]
        let selectElem = document.querySelector("#filter li.price select")

        for (let option of options) {
            selectElem.innerHTML += `
                <option value="` + option + `">
                    $` + option.toString() + `
                </option>
            `;
        }
    },
    filterAmenityCheckboxesPopulate: function() {
        let checkboxesHolder = document.querySelector("#filter li.amenities .filter-amenities")
        for (let amenity of hbnb.data.amenities) {
            checkboxesHolder.innerHTML += `
                <li>
                    <label>
                        <input type="checkbox" value="` + amenity.name.toLowerCase() + `" />
                        <span>` + amenity.name + `</span>
                    </label>
                </li>
            `;
        }
    },
    filterSearchInit: function() {
        const searchBtn = document.getElementById('search');
        searchBtn.addEventListener('click', function() {
            // Assemble the filter options
            const name = document.querySelector("#filter .filter-name")
            const price = document.querySelector("#filter .filter-price")
            const amenities = document.querySelectorAll("#filter .filter-amenities input")

            let amenitiesList = []
            for (let amenity of amenities) {
                if (amenity.checked) {
                    amenitiesList.push(amenity.value)
                }
            }

            let data = {
                "name": name.value,
                "price": price.value,
                "amenities": amenitiesList
            }
            console.log(data)

            const searchURL = "http://localhost:5000/api/v1/places/search";
            fetch(searchURL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(data),
            })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return response.json()
            }).then((json) => {
                console.log(json)
                hbnb.filterSearchAction(json)
            }).catch((e) => {
                console.error(e)
            }).finally(() => {
                console.log('search submitted!')
            })
        })
    },
    filterSearchAction: function(data) {
        // Get rid of existing Places + Regenerate the Places shown
        hbnb.placesPopulate(data)
    },
    loginModalInit: function() {
        let loginShowBtn = document.getElementById('login').querySelector("a");
        let loginModal = document.getElementById('login-modal');
        let loginSubmitBtn = document.getElementById('login-submit');
        let loginHideBtn = document.getElementById('login-cancel');
        let msgContainer = loginModal.querySelector(".modal .message");

        msgContainer.innerHTML = "";

        loginShowBtn.addEventListener('click', function(e) {
            //prevent redirection to login page
            e.preventDefault();

            // loginModal will unhide/appear
            loginModal.setAttribute('class', 'show');

            // enable the text fields and buttons
            hbnb.loginModalEnable(loginModal);
        })

        loginSubmitBtn.addEventListener('click', function() {
            hbnb.loginModalSubmit(loginModal);
        });

        loginHideBtn.addEventListener('click', function() {
            hbnb.loginModalDisable(loginModal);

            // loginModal will unhide/appear
            loginModal.setAttribute('class', 'hide');
        });
    },
    loginModalEnable: function(loginModal) {
        let inputs = loginModal.querySelectorAll("input");
        let buttons = loginModal.querySelectorAll("button");

        inputs[0].removeAttribute("disabled");
        inputs[1].removeAttribute("disabled");
        buttons[0].removeAttribute("disabled");
        buttons[1].removeAttribute("disabled");
    },
    loginModalDisable: function(loginModal) {
        let inputs = loginModal.querySelectorAll("input");
        let buttons = loginModal.querySelectorAll("button");

        inputs[0].setAttribute("disabled", "");
        inputs[1].setAttribute("disabled", "");
        buttons[0].setAttribute("disabled", "");
        buttons[1].setAttribute("disabled", "");
    },
    loginModalSubmit: function(loginModal) {
        hbnb.loginModalDisable(loginModal);

        let inputs = loginModal.querySelectorAll("input");
        const email = inputs[0].value
        const password = inputs[1].value

        let loginData = {
            email: email,
            password: password
        }

        // console.log('Submitting login information')
        // console.log(loginData)

        // Error check submitted info
        // NOTE: We should ideally encrypt the submitted data and not transmit it as plain-text
        if ((email.trim() == "") || (password.trim() == "")) {
            hbnb.loginErrorMessage(loginModal, "Invalid username / password")
        } else {
            //Show submission overlay
            let submitLoader = loginModal.querySelector(".submitting");
            submitLoader.setAttribute('class', 'submitting show');

            // API call starts here
            // curl -X POST "http://127.0.0.1:5000/api/v1/auth/login" -H "Content-Type: application/json" -d '{ "email": "john.doe@example.com", "password": "cowabunga" }'

            const searchURL = "http://localhost:5000/api/v1/auth/login";
            fetch(searchURL, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(loginData),
            })
            .then((response) => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                return response.json()
            }).then((json) => {
                console.log(json)
                // Remove modal
                loginModal.setAttribute('class', 'hide');

                // Store token somewhere
                localStorage.setItem("hbnb_v2_token", json.access_token);
                localStorage.setItem("hbnb_v2_token_owner", email);

                // Update upper-right bubble to indicate 'Logged-in' status
                hbnb.loggedInStateUpdate();
            }).catch((e) => {
                console.error(e)
                hbnb.loginErrorMessage(loginModal, e)
            }).finally(() => {
                console.log('Login completed!')
                submitLoader.setAttribute('class', 'submitting');
            })
        }
    },
    loginErrorMessage: function(loginModal, message) {
        let msgContainer = loginModal.querySelector(".modal .message");
        msgContainer.innerHTML = message;
    },
    loggedInStateUpdate: function() {
        //check if token and token_owner exists in localStorage
        // If exists, update the upper right bubble to indicate logged-in status
        const nav = document.getElementsByTagName("nav")[0];
        const email = document.getElementById("logout").querySelector(".email");

        const token = localStorage.getItem("hbnb_v2_token");
        const owner = localStorage.getItem("hbnb_v2_token_owner");

        if (owner && token) {
            nav.setAttribute("class", "logged-in");
            email.innerHTML = owner;
        }
    },
    logoutInit: function () {
        const nav = document.getElementsByTagName("nav")[0];
        const logout = document.getElementById("logout");

        logout.addEventListener('click', function(e){
            e.preventDefault();

            nav.setAttribute("class", "");

            localStorage.removeItem("hbnb_v2_token");
            localStorage.removeItem("hbnb_v2_token_owner");
        })
    },

    init: function() {
        const pageId = document.getElementsByTagName('body')[0].getAttribute('page-id')

        hbnb.loggedInStateUpdate();
        hbnb.logoutInit();

        switch(pageId) {
            case 'index':
                // 1. Load data for Amenities + Places
                hbnb.loadIndexData()
                .then(() => {
                    // 2. Populate filter with data
                    hbnb.filterAmenityCheckboxesPopulate()
                    hbnb.filterPriceOptionsPopulate()

                    // 3. Add Places data to website DOM
                    hbnb.placesPopulate()

                    // 4. Prepare the filter
                    hbnb.filterSearchInit()
                }).catch((e) => {
                    console.error(e)
                }).finally(() => {
                    // Hide the loader
                    hbnb.hideLoader()
                })
                break;
            case 'login':
                // TODO:
                break;
            case 'place':
                // TODO:
                break;
            case 'add_review':
                // TODO:
                break;
        }

        hbnb.loginModalInit();
    }
}

window.onload = function() {
  hbnb.init();
}

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
    // general function used to load data for Places + Amenities
    loadData: async function() {
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
    placesPopulate: function() {
        const cardsListTag = document.querySelector("#places-list > .cards")

        // Use innerHTML to add the HTML content to the page
        for (let place of hbnb.data.places) {
            // NOTE: Consider storing the HTML below elsewhere instead of within this function
            // e.g. hbnb.html.places.card
            amenities_spans = ``
            if (place.amenities.length > 0) {
                for (let amenity of place.amenities) {
                    amenities_spans += `<span class="` + amenity.toLowerCase() + `"></span>`
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
        let checkboxesHolder = document.querySelector("#filter li.amenities .choices")
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
    init: function() {
        // 1. Load data for Amenities + Places
        hbnb.loadData().then(() => {
            // 2. Populate filter with data
            hbnb.filterAmenityCheckboxesPopulate()
            hbnb.filterPriceOptionsPopulate()

            // 3. Add Places data to website DOM
            hbnb.placesPopulate()
        }).catch((e) => {
            console.error(e)
        }).finally(() => {
            // Hide the loader
            hbnb.hideLoader()
        })
    }
}

window.onload = function() {
  hbnb.init();
}
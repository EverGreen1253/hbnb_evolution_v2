
hbnb = {
    "msg": {
        "error": {
            "api": {
                "places": "Unable to connect to Places API. Please ensure the server is active.",
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
    placesLoad: function() {
        let apiErrorHappened = false
        const url = "http://localhost:5000/api/v1/places/";

        const placesPromise = new Promise((resolve, reject) => {
            try {
                const response = fetch(url);
                response.then((result) => {
                    resolve(result.json());
                }).catch((e) => {
                    // console.error(e)
                    hbnb.showError(hbnb.msg.error.api.places)
                    hbnb.hideLoader()
                    apiErrorHappened = true
                })
            } catch(error) {
                console.error("Error:", error);
                reject('Unable to fetch Places data');
            }
        });

        if (!apiErrorHappened) {
            placesPromise.then((result) => {
                hbnb.placesPopulate(result)
            }).catch((e) => {
                // console.error(e)
                hbnb.showError(hbnb.msg.error.api.places)
            }).finally(() => {
                hbnb.hideLoader()
            })
        }
    },
    placesPopulate: function(data) {
        const cardsListTag = document.querySelector("#places-list > .cards")

        // Use innerHTML to add the HTML content to the page
        for (let place of data) {
            console.log(place)
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
    filterAmenityPopulate: function() {
        amenities = ["Wi-Fi", "Toilet", "Shower", "Air Con"]
        let checkboxesHolder = document.querySelector("#filter li.amenities .choices")
        for (let amenity of amenities) {
            checkboxesHolder.innerHTML += `
                <li>
                    <label>
                        <input type="checkbox" value="` + amenity.toLowerCase() + `" />
                        <span>` + amenity + `</span>
                    </label>
                </li>
            `;
        }
    },
    init: function() {
        // 1. Init the filter options
        hbnb.filterPriceOptionsPopulate()
        hbnb.filterAmenityPopulate()

        // 2. Load Places data by calling the API
        hbnb.placesLoad()

        // NOTE: I tried loading the amenities via a Promise and that resulted in
        // it fighting with the Promise used to load the Places. The server died as
        // a result. lol
    }
}

window.onload = function() {
  hbnb.init();
}
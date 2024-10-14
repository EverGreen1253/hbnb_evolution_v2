
hbnb = {
  placesLoad: function() {
    const url = "http://localhost:5000/api/v1/places/";
    const placesPromise = new Promise((resolve, reject) => {
        try {
            const response =  fetch(url);
            response.then((result) => {
                resolve(result.json());
            })
        } catch(error) {
            console.error("Error:", error);
            reject('Unable to fetch Places data');
        }
    });

    placesPromise.then((result) => {
        hbnb.placesPopulate(result)
    }).catch((e) => {
        console.error(e)
    }).finally(() => {
        // Hide the loader
        document.getElementById("loader").setAttribute('class', 'hide');
    })
  },
  placesPopulate: function(data) {
    const cardsListTag = document.querySelector("#places-list > .cards")

    for (let place of data) {
        console.log(place)
        cardsListTag.innerHTML += `
            <li class="card">
                <div>
                    <div class="title">` + place.title + `</div>
                    <div class="details">
                        <div class="image"></div>
                        <div class="desc">
                            Description goes here
                        </div>
                        <div class="coords">
                            <span><b>Lat: </b>` + place.latitude + `</span>
                            <span><b>Lon: </b>` + place.longitude + `</span>
                        </div>
                    </div>
                <div>
            </li>
        `;
    }
  },
  init: function() {
    // 1. Load Places data by calling the API
    hbnb.placesLoad()
  }
}

window.onload = function() {
  hbnb.init();
}
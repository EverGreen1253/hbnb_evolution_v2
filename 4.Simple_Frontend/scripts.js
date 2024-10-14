
hbnb = {
  placesLoad: function() {
    const placesPromise = new Promise((resolve, reject) => {
        try {
            const response =  fetch("http://localhost:5000/api/v1/places/");
            response.then((result) => {
                resolve(result.json());
            })
        } catch(error) {
            console.error("Error:", error);
            reject('something happened');
        }
    });

    placesPromise.then((result) => {
    }).catch((e) => {
        // console.error(e)
        console.error('Something happened...');
    }).finally(() => {
        // Hide the loader
        document.getElementById("loader").setAttribute('class', 'hide');
    })
  },
  init: function() {
    // 1. Load Places data by calling the API
    hbnb.placesLoad()
  }
}

window.onload = function() {
  hbnb.init();
}
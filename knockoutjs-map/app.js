$('.button-collapse').sideNav({
      menuWidth: 300, // Default is 240
      closeOnClick: true // Closes side-nav on <a> clicks, useful for Angular/Meteor
    }
  );
  $('.collapsible').collapsible();
// information necessary to make yelp api calls
var auth = {
  consumerKey : "-yWqqu3hN0m5tffcgxH5dQ",
  consumerSecret : "YYkBOofPPdl2gJ5G4_9Y6HPsaHw",
  accessToken : "9ihPVtzou5GpqESTp19YZqsn9yYD6wLD",
  accessTokenSecret : "3UPX0i7ZELWRCz-9DPGJfsilf3s",
  serviceProvider : {
      signatureMethod : "HMAC-SHA1"
  }
};
accessor = {
  consumerSecret : auth.consumerSecret,
  tokenSecret : auth.accessTokenSecret
};

// An array of locations that will be displayed on the map
// Structure: name, latitude, longitude, label for the map, z-index, yelp id
var locations = [
  ['Westminster Abbey', 51.4993815, -0.1286692, 'A', 1, 'westminster-abbey-london'],
  ['London Eye', 51.503324, -0.1217317, 'B', 2, 'coca-cola-london-eye-london'],
  ['Shakespeare\'s Globe Theatre', 51.508076, -0.0993827, 'C', 3, 'shakespeares-globe-theatre-bankside'],
  ['Buckingham Palace', 51.501364, -0.1440787, 'D', 4, 'buckingham-palace-london'],
  ['Trafalgar Square', 51.50809, -0.1285907, 'E', 5, 'trafalgar-square-london'],
  ['St. Paul\'s Cathedral', 51.5138453, -0.1005393, 'F', 6, 'st-pauls-cathedral-london-4'],
  ['Platform 9 3/4', 51.5319304, -0.1263326, 'G', 7, 'platform-9-3-4-london'],
  ['Big Ben', 51.5007292, -0.1268141, 'H', 8, 'big-ben-london']
];

function loadError(resource) {
  Materialize.toast('Failed to load resource ' + resource, 4000);
}

// Create the map
var map;
var infoWindow;
function initMap() {
  map = new google.maps.Map(document.getElementById('map-container'), {
    zoom: 12,
    center: {lat: 51.5, lng: -0.12}
  });

  var locationViewModel = new LocationsViewModel();
  infoWindow = new google.maps.InfoWindow();
  // Once the map has been created, apply knockout so map objects can be controlled
  ko.applyBindings(locationViewModel);
}

/*
* An object that represents a location on the map
* name: the name of the location
* lat: the latitude value
* lng: the longitude value
* label: label for the google map marker
* zindex: the z-index for the marker
* yelpId: the ID used to get information from yelp
* parent: the LocationsViewModel that owns this location
*/
function Location(name, lat, lng, label, zindex, yelpId, parent) {
  var self = this;
  self.name = name;
  self.lat = lat;
  self.lng = lng;
  self.label = label;
  self.zindex = zindex;
  self.active = ko.observable(false);
  self.parent = parent;
  self.visiblePin = ko.observable(true);
  self.yelpId = yelpId

  // displayName is used on the collection-item <li> data-bind
  self.displayName = ko.computed(function () {
    return '(' + self.label + ') ' + self.name;
  });

  // Shows and hides pins on the map
  self.visiblePin.subscribe(function(currentState) {
    if(currentState) {
      self.marker.setVisible(currentState);
    } else {
      self.marker.setVisible(currentState);
    }
  });

  // Animate pins on the map
  self.active.subscribe(function(currentState) {
    if(currentState == true) {
      self.marker.setAnimation(google.maps.Animation.BOUNCE);
    } else {
      self.marker.setAnimation(null);
    }
  });

  // Creates the google map marker
  self.marker = new google.maps.Marker({
    position: {lat: self.lat, lng: self.lng},
    map: map,
    title: self.name,
    label: self.label,
    zIndex: self.zindex
  });


  // When the marker is clicked, call the LocationsViewModel.goToLocation function
  self.listener = google.maps.event.addListener(self.marker, 'click', function() {
    self.parent.goToLocation(self);
  });
}

Location.prototype.showInfoWindow = function() {
  var self = this;
  // set up the oauth object to authenticate to yelp
  var accessor = {
    consumerSecret : auth.consumerSecret,
    tokenSecret : auth.accessTokenSecret
  };

  var parameters = [];
  parameters.push(['callback', 'cb']);
  parameters.push(['oauth_consumer_key', auth.consumerKey]);
  parameters.push(['oauth_consumer_secret', auth.consumerSecret]);
  parameters.push(['oauth_token', auth.accessToken]);
  parameters.push(['oauth_signature_method', 'HMAC-SHA1']);

  // Set up for the XHR object
  // see: https://www.yelp.com/developers/documentation/v2/business
  var message = {
    'action' : 'https://api.yelp.com/v2/business/' + self.yelpId,
    'method' : 'GET',
    'parameters' : parameters
  };

  OAuth.setTimestampAndNonce(message);
  OAuth.SignatureMethod.sign(message, accessor);

  var parameterMap = OAuth.getParameterMap(message.parameters);

  $.ajax({
    'url' : message.action,
    'data' : parameterMap,
    'dataType' : 'jsonp',
    'cache': true
  })
  .done(function(data) {
      /*
      *  On successful request, populate the infoWindow
      * data.location.display_address is a human readable address
      * data.rating_img_url is a url for the star rating image
      * data.snippet_text is a description of the location
      * data.url is a link to the yelp page
      */
      if (!data) {
        Materialize.toast('Failed to connect to Yelp! Try again later', 4000);
      }
      data.location.display_address ? address = data.location.display_address : address = "Address not provided";
      data.rating_img_url ? rating_img_url = '<img src="' + data.rating_img_url  + '">"' : rating_img_url = "<div>Not rated yet</div>";
      data.snippet_text ? snippet_text = data.snippet_text : snippet_text = "No description provided";
      data.url ? url = '<a href="' + data.url + '"> View more on Yelp</a>' : url = "Not on Yelp";
      var content = '<h5>' + self.name + '</h5>' +
                    '<div>' + address + '</div>' +
                    rating_img_url +
                    '<p>' + snippet_text + '</p>' +
                    url;
      infoWindow.setContent(content);
      infoWindow.open(map, self.marker);

    }
  )
  .fail(function() {
    // If the request failed, let the user know with a Toast
      Materialize.toast('Failed to connect to Yelp! Try again later', 4000);
    }
  );
}

/*
* The knockout ViewModel
* locations: the array of locations this will control
* current_filter: blank, or the string a user has typed into the input box
*/
function LocationsViewModel() {
  var self = this;
  self.locations = ko.observableArray();
  self.current_filter = ko.observable('');

  // When the user enters something into the input field, begin filtering out collection-items and markers
  self.filter = ko.computed(function() {
    if (!self.current_filter()) {
      ko.utils.arrayForEach(self.locations(), function(location) {
        location.visiblePin(true);
      });
      return self.locations();
    } else {
      return ko.utils.arrayFilter(self.locations(), function(location) {
        var match = location.name.toLowerCase().indexOf(self.current_filter().toLowerCase()) >= 0;
        location.visiblePin(match);
        return match;
      })
    }
  });

  // Closes open infoWindows and opens this location's
  self.goToLocation = function(location) {
    // Close all InfoWindows first
    ko.utils.arrayForEach(self.locations(), function(location) {
      location.active(false);
    });
    location.active(true);
    location.showInfoWindow();
  };

  // Add the locations array as location objects to this ViewModel
  for(var i=0; i < locations.length; i++) {
    var location = new Location(locations[i][0], locations[i][1], locations[i][2], locations[i][3], locations[i][4], locations[i][5], self);
    self.locations.push(location);
  }
}

# neighborhood-map
This repository is an implementation of the Neighborhood Map project for Udacity's Fullstack nanodegree.

This is a single page application that uses [knockout.js](www.knockoutjs.com) to provide data binding. There is a full page Google Maps map centered on London, with a few popular locations highlighted. The left side of the page has a Material Design card with a collection of the locations, which can be filtered. Clicking on either the collection item or the map marker will generate an AJAX call to Yelp to acquire information about the location, and open an InfoWindow with that information.

Credits:
* [mnemonicflow](https://gist.github.com/mnemonicflow/1b90ef0d294c692d24458b8378054c81) for how to tie in OAuth to make the Yelp request from the client

# Usage
Simply open the index.html file in your browser. The page may also be previewed on [github.io](https://kimobu.github.io/neighborhood-map/)

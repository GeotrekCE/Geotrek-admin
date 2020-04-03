Leaflet.OverIntent
==================

Aiming is neater than clicking !

This plugins adds a new event ``mouseintent``, that differs from ``mouseover`` since
it reflects user intentions to aim a particular layer.

Observe the difference with the [online demo](http://makinacorpus.github.io/Leaflet.OverIntent/).


Usage
-----

```javascript

    var marker = L.marker([]).addTo(map);

    marker.on('mouseintent', function (e) {
        // User meant it !
    });
```

( *works with markers and vectorial layers* )

Authors
-------

[![Makina Corpus](http://depot.makina-corpus.org/public/logo.gif)](http://makinacorpus.com)

Leaflet.Spin
============

Shows a nice spin cursor on the map.

Requires [Spin.js](http://fgnass.github.com/spin.js/).

See [online demo](http://makinacorpus.github.io/Leaflet.Spin/).


Usage
-----


### Manually

```javascript
map.spin(true);  // on
...
map.spin(false);  // off
```

### Spin.js options

You can control apparence of wheel by passing options on first ``spin()`` call.

```javascript
map.spin(true, {lines: 13, length: 40});
```

[More details on available options](http://fgnass.github.io/spin.js/)...


### With AJAX / JQuery

```
    map.spin(true);
    $.ajax({url: 'http://server/api/'})
     .done(function() {
        map.spin(false);
      })
     .error(function () {
        map.spin(false);
      });

```


Using events:

```
    var layer = L.geoJson(null).addTo(map);
    
    layer.fire('data:loading');
    $.getJSON('http://server/path.geojson', function (data) {
        layer.fire('data:loaded');
        layer.addData(data);
    });

```

### With [Leaflet.AJAX](https://github.com/calvinmetcalf/leaflet-ajax/)

```

    var layer = L.geoJson.ajax();
    layer.addUrl('http://server/path.geojson');

```


Authors
-------

[![Makina Corpus](http://depot.makina-corpus.org/public/logo.gif)](http://makinacorpus.com)

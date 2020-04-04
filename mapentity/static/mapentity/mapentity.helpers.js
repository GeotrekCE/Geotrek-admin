// Toggable console.debug() function
console.debug = function () {
    if (window.SETTINGS && window.SETTINGS.debug) {
        if (arguments.length > 1)
            console.log(arguments);
        else
            console.log(arguments[0]);
    }
};

if (!Function.prototype.bind) {
    Function.prototype.bind = function (oThis) {
    if (typeof this !== "function") {
      // closest thing possible to the ECMAScript 5 internal IsCallable function
      throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
    }

    var aArgs = Array.prototype.slice.call(arguments, 1),
        fToBind = this,
        fNOP = function () {},
        fBound = function () {
          return fToBind.apply(this instanceof fNOP && oThis ? this : oThis,
                               aArgs.concat(Array.prototype.slice.call(arguments)));
        };

    fNOP.prototype = this.prototype;
    fBound.prototype = new fNOP();

    return fBound;
    };
}

/**
 * Get URL parameter in Javascript
 * source: http://stackoverflow.com/questions/1403888/get-url-parameter-with-jquery
 */
function getURLParameter(name) {
    var paramEncoded = (RegExp('[?|&]' + name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1],
        paramDecoded = decodeURIComponent(paramEncoded);
    if (typeof paramDecoded == 'string') {
        try {
            return JSON.parse(paramDecoded);
        }
        catch (e) {}
    }
    return paramDecoded;
}


/**!
 * @preserve parseColor
 * Copyright 2011 THEtheChad Elliott
 * Released under the MIT and GPL licenses.
 */
// Parse hex/rgb{a} color syntax.
// @input string
// @returns array [r,g,b{,o}]
parseColor = function(color) {

    var cache
      , p = parseInt // Use p as a byte saving reference to parseInt
      , color = color.replace(/\s\s*/g,'') // Remove all spaces
    ;//var

    // Checks for 6 digit hex and converts string to integer
    if (cache = /^#([\da-fA-F]{2})([\da-fA-F]{2})([\da-fA-F]{2})/.exec(color))
        cache = [p(cache[1], 16), p(cache[2], 16), p(cache[3], 16)];

    // Checks for 3 digit hex and converts string to integer
    else if (cache = /^#([\da-fA-F])([\da-fA-F])([\da-fA-F])/.exec(color))
        cache = [p(cache[1], 16) * 17, p(cache[2], 16) * 17, p(cache[3], 16) * 17];

    // Checks for rgba and converts string to
    // integer/float using unary + operator to save bytes
    else if (cache = /^rgba\(([\d]+),([\d]+),([\d]+),([\d]+|[\d]*.[\d]+)\)/.exec(color))
        cache = [+cache[1], +cache[2], +cache[3], +cache[4]];

    // Checks for rgb and converts string to
    // integer/float using unary + operator to save bytes
    else if (cache = /^rgb\(([\d]+),([\d]+),([\d]+)\)/.exec(color))
        cache = [+cache[1], +cache[2], +cache[3]];

    // Otherwise throw an exception to make debugging easier
    else throw Error(color + ' is not supported by parseColor');

    // Performs RGBA conversion by default
    isNaN(cache[3]) && (cache[3] = 1);

    // Adds or removes 4th value based on rgba support
    // Support is flipped twice to prevent erros if
    // it's not defined
    return cache.slice(0,3 + !!$.support.rgba);
};


function expandDatatableHeight(dTable) {
    var nTable = $(dTable.fnSettings().nTable),
        wrapper = nTable.parents('.dataTables_wrapper').first(),
        extraHead = 30 + nTable.position().top - wrapper.position().top,
        rowHeight = nTable.find('tbody tr').height();

    var displayLength = Math.floor((wrapper.height() - extraHead) / rowHeight);
    dTable.fnSettings()._iDisplayLength = Math.max(1, displayLength -1); //<thead>
    dTable.fnDraw(false);
};


function tr(s) {
    return MapEntity.i18n[s] || s;
}

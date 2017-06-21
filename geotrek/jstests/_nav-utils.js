var fs = require('fs');

module.exports = (function() {

    const PATH_COOKIES = '/tmp/cookies.txt';

    function setUp() {
        casper.options.viewportSize = {width: 1280, height: 768};
        casper.options.waitTimeout = 20000;
        casper.userAgent('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.97 Safari/537.11 FrontendTest');

        casper.on('remote.message', function(msg) {
            this.echo("...Console: " + msg);
        });

        casper.on('page.error', function(msg, trace) {
            this.echo("...Error: " + msg, "ERROR");
            for(var i=0; i<trace.length; i++) {
                var step = trace[i];
                this.echo('   ' + step.file + ' (line ' + step.line + ')', "ERROR");
            }
        });
    }

    function saveCookies(path) {
        path = path || PATH_COOKIES;
        var cookies = JSON.stringify(phantom.cookies);
        fs.write(path, cookies, 600);
    }

    function loadCookies(path) {
        path = path || PATH_COOKIES;
        var data = fs.read(path);
        phantom.cookies = JSON.parse(data);
    }

    return {
        baseurl: casper.cli.options['baseurl'],
        saveCookies: saveCookies,
        loadCookies: loadCookies,
        setUp: setUp
    };
})();

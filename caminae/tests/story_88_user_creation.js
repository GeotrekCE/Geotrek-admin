//==============================================================================
// Casper generated Thu Aug 02 2012 15:19:52 GMT+0200 (CEST)
//==============================================================================

var x = require('casper').selectXPath;
var casper = require('casper').create();
var baseurl = casper.cli.options['baseurl'];
casper.options.viewportSize = {width: 1146, height: 758};
casper.start(baseurl);

casper.waitForSelector("form",
    function success() {
        this.fill("form", {"username": "admin",
                           "password": "admin"}, true);
    },
    function fail() {
        this.test.assertExists("form");
});
casper.waitForSelector(x("//a[text()='Admin']"),
    function success() {
        this.test.assertExists(x("//a[text()='Admin']"));
        this.click(x("//a[text()='Admin']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Admin']"));
});
casper.waitForSelector(x("//a[text()='Utilisateurs']"),
    function success() {
        this.test.assertExists(x("//a[text()='Utilisateurs']"));
        this.click(x("//a[text()='Utilisateurs']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Utilisateurs']"));
});
casper.waitForSelector(x("//a[normalize-space(text())='Ajouter utilisateur']"),
    function success() {
        this.test.assertExists(x("//a[normalize-space(text())='Ajouter utilisateur']"));
        this.click(x("//a[normalize-space(text())='Ajouter utilisateur']"));
    },
    function fail() {
        this.test.assertExists(x("//a[normalize-space(text())='Ajouter utilisateur']"));
});
casper.waitForSelector("form#user_form input[name='username']",
    function success() {
        this.test.assertExists("form#user_form input[name='username']");
        this.click("form#user_form input[name='username']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='username']");
});
casper.waitForSelector("form#user_form",
    function success() {
        this.fill("form#user_form", {"username": "inewton"});
    },
    function fail() {
        this.test.assertExists("form#user_form");
});
casper.waitForSelector("form#user_form input[name='password1']",
    function success() {
        this.test.assertExists("form#user_form input[name='password1']");
        this.click("form#user_form input[name='password1']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='password1']");
});
casper.waitForSelector("form#user_form",
    function success() {
        this.fill("form#user_form", {"password1": "inewton"});
    },
    function fail() {
        this.test.assertExists("form#user_form");
});
casper.waitForSelector("form#user_form input[name='password2']",
    function success() {
        this.test.assertExists("form#user_form input[name='password2']");
        this.click("form#user_form input[name='password2']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='password2']");
});
casper.waitForSelector("form#user_form",
    function success() {
        this.fill("form#user_form", {"password2": "inewton"});
    },
    function fail() {
        this.test.assertExists("form#user_form");
});
casper.waitForSelector("form#user_form input[type=submit][value='Enregistrer']",
    function success() {
        this.test.assertExists("form#user_form input[type=submit][value='Enregistrer']");
        this.click("form#user_form input[type=submit][value='Enregistrer']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[type=submit][value='Enregistrer']");
});
// submit form
casper.waitForSelector("form#user_form input[name='first_name']",
    function success() {
        this.test.assertExists("form#user_form input[name='first_name']");
        this.click("form#user_form input[name='first_name']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='first_name']");
});
casper.waitForSelector("form#user_form input[name='first_name']",
    function success() {
        this.test.assertExists("form#user_form input[name='first_name']");
        this.click("form#user_form input[name='first_name']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='first_name']");
});
casper.waitForSelector("form#user_form input[name='first_name']",
    function success() {
        this.test.assertExists("form#user_form input[name='first_name']");
        this.click("form#user_form input[name='first_name']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='first_name']");
});
casper.waitForSelector("form#user_form",
    function success() {
        this.fill("form#user_form", {"first_name": "Isaac"});
    },
    function fail() {
        this.test.assertExists("form#user_form");
});
casper.waitForSelector("form#user_form input[name='last_name']",
    function success() {
        this.test.assertExists("form#user_form input[name='last_name']");
        this.click("form#user_form input[name='last_name']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[name='last_name']");
});
casper.waitForSelector("form#user_form",
    function success() {
        this.fill("form#user_form", {"last_name": "Newton"});
    },
    function fail() {
        this.test.assertExists("form#user_form");
});
casper.waitForSelector("form#user_form input[type=submit][value='Enregistrer']",
    function success() {
        this.test.assertExists("form#user_form input[type=submit][value='Enregistrer']");
        this.click("form#user_form input[type=submit][value='Enregistrer']");
    },
    function fail() {
        this.test.assertExists("form#user_form input[type=submit][value='Enregistrer']");
});
// submit form

casper.waitForSelector(x("//a[text()='Back to application']"),
    function success() {
        this.test.assertExists(x("//a[text()='Back to application']"));
        this.click(x("//a[text()='Back to application']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Back to application']"));
});
casper.waitForSelector(x("//a[text()='Logout']"),
    function success() {
        this.test.assertExists(x("//a[text()='Logout']"));
        this.click(x("//a[text()='Logout']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Logout']"));
});
casper.wait(3000);

casper.waitForSelector("form",
    function success() {
        this.fill("form", {"username": "inewton", "password": "inewton"}, true);
    },
    function fail() {
        this.test.assertExists("form");
});
casper.waitForSelector(x("//*[normalize-space(text())='inewton&nbsp;']"),
    function success() {
        this.test.assertExists(x("//*[normalize-space(text())='inewton&nbsp;']"));
      },
    function fail() {
        this.test.assertExists(x("//*[normalize-space(text())='inewton']&nbsp;"));
});
casper.waitForSelector(x("//*[text()='Tronçon']"),
    function success() {
        this.test.assertExists(x("//*[text()='Tronçon']"));
      },
    function fail() {
        this.test.assertExists(x("//*[text()='Tronçon']"));
});
casper.waitForSelector(x("//*[contains(text(), 'Longueur')]"),
    function success() {
        this.test.assertExists(x("//*[contains(text(), 'Longueur')]"));
      },
    function fail() {
        this.test.assertExists(x("//*[contains(text(), 'Longueur')]"));
});

casper.waitForSelector(x("//a[text()='Logout']"),
    function success() {
        this.test.assertExists(x("//a[text()='Logout']"));
        this.click(x("//a[text()='Logout']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Logout']"));
});
casper.wait(3000);
casper.waitForSelector("form",
    function success() {
        this.fill("form", {"username": "admin", "password": "admin"}, true);
    },
    function fail() {
        this.test.assertExists("form");
});
casper.waitForSelector(x("//a[text()='Admin']"),
    function success() {
        this.test.assertExists(x("//a[text()='Admin']"));
        this.click(x("//a[text()='Admin']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Admin']"));
});
casper.waitForSelector(x("//a[text()='Utilisateurs']"),
    function success() {
        this.test.assertExists(x("//a[text()='Utilisateurs']"));
        this.click(x("//a[text()='Utilisateurs']"));
    },
    function fail() {
        this.test.assertExists(x("//a[text()='Utilisateurs']"));
});
casper.waitForSelector("form#changelist-search",
    function success() {
        this.fill("form#changelist-search", {"q": "inewton"}, true);
    },
    function fail() {
        this.test.assertExists("form#changelist-search");
});
casper.waitForSelector("form#changelist-search input[type=submit][value='Rechercher']",
    function success() {
        this.test.assertExists("form#changelist-search input[type=submit][value='Rechercher']");
        this.click("form#changelist-search input[type=submit][value='Rechercher']");
    },
    function fail() {
        this.test.assertExists("form#changelist-search input[type=submit][value='Rechercher']");
});
// submit form
casper.waitForSelector("form#changelist-form input#action-toggle",
    function success() {
        this.test.assertExists("form#changelist-form input#action-toggle");
        this.click("form#changelist-form input#action-toggle");
    },
    function fail() {
        this.test.assertExists("form#changelist-form input#action-toggle");
});
casper.waitForSelector("input#action-toggle", function() {
    casper.evaluate(function() {
        var element = document.querySelectorAll("input#action-toggle")[0];
        element.name="unamed_field_1";
    });
});
casper.waitForSelector("form#changelist-form",
    function success() {
        this.fill("form#changelist-form", {"unamed_field_1": "on"}, true);
    },
    function fail() {
        this.test.assertExists("form#changelist-form");
});
casper.waitForSelector("form#changelist-form input#action-toggle",
    function success() {
        this.test.assertExists("form#changelist-form input#action-toggle");
        this.click("form#changelist-form input#action-toggle");
    },
    function fail() {
        this.test.assertExists("form#changelist-form input#action-toggle");
});
casper.waitForSelector("form#changelist-form",
    function success() {
        this.fill("form#changelist-form", {"action": "delete_selected"});
    },
    function fail() {
        this.test.assertExists("form#changelist-form");
});
casper.waitForSelector("form#changelist-form button[type=submit][value='0']",
    function success() {
        this.test.assertExists("form#changelist-form button[type=submit][value='0']");
        this.click("form#changelist-form button[type=submit][value='0']");
    },
    function fail() {
        this.test.assertExists("form#changelist-form button[type=submit][value='0']");
});
casper.waitForSelector("form input[type=submit][value='Oui, je suis sûr']",
    function success() {
        this.test.assertExists("form input[type=submit][value='Oui, je suis sûr']");
        this.click("form input[type=submit][value='Oui, je suis sûr']");
    },
    function fail() {
        this.test.assertExists("form input[type=submit][value='Oui, je suis sûr']");
});

casper.run(function() {this.test.renderResults(true);});

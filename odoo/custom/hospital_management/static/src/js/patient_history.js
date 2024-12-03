odoo.define('hospital_management.patient_history', function (require) {
    "use strict";

    var ListView = require('web.ListView');

    ListView.include({
        start: function () {
            this._super.apply(this, arguments);
            this.load_health_history();
        },

        load_health_history: function () {
            // Hastanın sağlık geçmişini yükleyen kod
        },
    });
});

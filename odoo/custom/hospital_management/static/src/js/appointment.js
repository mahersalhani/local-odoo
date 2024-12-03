odoo.define('hospital_management.appointment', function (require) {
    "use strict";

    var FormView = require('web.FormView');
    var rpc = require('web.rpc');

    FormView.include({
        on_save: function () {
            var self = this;
            var doctor_id = this.recordData.doctor_id;
            var appointment_date = this.recordData.appointment_date;

            rpc.query({
                model: 'hospital.appointment',
                method: 'check_appointment_availability',
                args: [doctor_id, appointment_date],
            }).then(function (availability) {
                if (!availability) {
                    alert("Bu doktorun bu tarihte yeterli randevusu yok.");
                } else {
                    self._super.apply(self, arguments);
                }
            });
        }
    });
});

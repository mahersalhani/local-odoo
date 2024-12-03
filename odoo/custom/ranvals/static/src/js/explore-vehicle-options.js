/** @odoo-module **/

import options from "@web_editor/js/editor/snippets.options";

options.registry.ExploreVehicleOptions = options.Class.extend({
  /**
   * @override
   */
  init() {
    this._super(...arguments);
    this.rpc = this.bindService("rpc");
  },

  /**
   * @override
   */
  start: async function () {
    this.vehiclesRow = this.$target.find("#yh-vehicle-raw");

    if (this.vehiclesRow) {
      const data = await this.rpc("/vehicle_cart/");

      let html = ``;

      if (!data.length)
        html = `<div class="col-12 alert alert-warning text-center">No Vehicle Found</div>`;
      else if (data.length)
        data.forEach((v) => {
          html += `<div class="col-lg-4 col-md-6 col-sm-12 mb-3">
            <div class="card">
              <img src="data:image/png;base64,${v.vehicle_image}" class="card-img-top" alt="Vehicle Image" />
              <div class="card-body">
                <h5 class="card-title">
                  ${v.name}
                </h5>
                <p class="card-text">
                  ${v.vehicle_model}
                </p>
              </div>
            </div>
          </div>
        `;
        });

      this.vehiclesRow.html(html);
    }
  },

  destroy() {
    this.vehiclesRow.html("");
  },
});

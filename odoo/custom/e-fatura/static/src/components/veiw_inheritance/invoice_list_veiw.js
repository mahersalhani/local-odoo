/** @odoo-module */

import { registry } from "@web/core/registry";
import { listView } from "@web/views/list/list_view";
import { ListController } from "@web/views/list/list_controller";
import { useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

class InvoiceListController extends ListController {
  setup() {
    super.setup();
    this.rpc = useService("rpc");
    this.notificationService = useService("notification");

    this.state = useState({
      loading: false,
      hasSyncedOnce: false,
    });

    // Daha önce senkronize edilmiş mi kontrol et
    const hasSyncedOnce = localStorage.getItem("invoices_synced") === "true";
    const isSyncing = sessionStorage.getItem("invoices_syncing") === "true";
    if (!hasSyncedOnce && !isSyncing) {
      this.syncInvoices();
    }
  }

  async syncInvoices() {
    // Eğer senkronizasyon daha önce yapılmışsa çıkış yap
    // if (localStorage.getItem("invoices_synced") === "true") {
    //   return;
    // }

    sessionStorage.setItem("invoices_syncing", "true");

    this.state.loading = true;

    try {
      // Senkronizasyon API çağrısı
      const res = await this.rpc("/call_kw/account.move/sync_invoices");

      if (res.status === "field") {
        sessionStorage.removeItem("invoices_syncing");
        this.state.hasSyncedOnce = true;

        this.notificationService.add(res.message, {
          title: "Invoices Synced",
          type: "danger",
        });

        return;
      }

      // Başarılı bir senkronizasyon yapıldığında localStorage'a kaydet
      localStorage.setItem("invoices_synced", "true");
      sessionStorage.removeItem("invoices_syncing");
      window.location.reload();
    } catch (error) {
      console.log("Error syncing invoices:", error.message);
    } finally {
      this.state.loading = false;
    }
  }

  handleButtonClick() {
    // Senkronizasyon butonuna tıklanıldığında senkronizasyonu başlat
    this.syncInvoices();
  }
}

export const invoiceListView = {
  ...listView,
  Controller: InvoiceListController,
  buttonTemplate: "owl.InvoiceListView.Buttons",
};

registry.category("views").add("invoice_list_view", invoiceListView);

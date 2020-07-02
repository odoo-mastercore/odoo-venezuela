.. |company| replace:: ADHOC SA

.. |icon| image:: https://raw.githubusercontent.com/ingadhoc/maintainer-tools/master/resources/adhoc-icon.png

.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============
Payment Groups
==============

This module extends the functionality of payments to suport paying with multiple payment methods at once.

By default payments are managed on one step, if you want, you can use two steps to confirm payments on supplier payments. This option is available per company.

A new security group "See Payments Menu" is created and native odoo payments menus are assigned to that group.

We also add a pay now functionality on invoices so that payment can be automatically created if you choose a journal on the invoice. You need to enable this on accounting configuration.

Account Payment groups are created from:

* sale order payments
* reconciliation wizard (statements)
* website payments
* after expense validation when posting journal items.

Credits
=======

* |company| |icon|
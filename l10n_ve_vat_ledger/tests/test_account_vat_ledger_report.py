# -*- coding: utf-8 -*-
##############################################################################
# Author: Mastercore Sinapsys Global®
# Copyright: 2019-Present.
# License OPL-1 (Odoo Proprietary License v1.0)
# See https://www.odoo.com/documentation/master/legal/licenses.html
#
#
##############################################################################

from odoo import Command, fields
from odoo.addons.account.tests.common import AccountTestInvoicingCommon
from odoo.tests import tagged


@tagged('post_install', '-at_install')
class TestAccountVatLedgerReport(AccountTestInvoicingCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.withholding_tax = cls.company_data['default_tax_sale'].copy({
            'name': 'Customer VAT withholding',
            'type_tax_use': 'none',
            'l10n_ve_tax_type': 'partner_tax',
            'l10n_ve_withholding_payment_type': 'customer',
            'l10n_ve_withholding_ingoing_type': 'iva',
        })
        cls.ledger = cls.env['account.vat.ledger'].create({
            'company_id': cls.env.company.id,
            'type': 'sale',
            'date_from': fields.Date.from_string('2026-09-01'),
            'date_to': fields.Date.from_string('2026-09-30'),
            'journal_ids': [Command.set(
                cls.company_data['default_journal_sale'].ids
            )],
        })
        cls.posted_withholding = cls.env['l10n_ve.payment.withholding'].create({
            'tax_id': cls.withholding_tax.id,
            'name': 'TEST-POSTED',
            'date': fields.Date.from_string('2026-09-10'),
            'state': 'posted',
            'amount': 100.0,
        })
        cls.canceled_withholding = cls.env['l10n_ve.payment.withholding'].create({
            'tax_id': cls.withholding_tax.id,
            'name': 'TEST-CANCELED',
            'date': fields.Date.from_string('2026-09-10'),
            'state': 'cancel',
            'amount': 100.0,
        })
        cls.ledger.withholding_ids = [Command.set(
            (cls.posted_withholding | cls.canceled_withholding).ids
        )]

    def test_canceled_withholdings_are_excluded_from_report(self):
        report = self.env[
            'report.l10n_ve_vat_ledger.account_vat_ledger_xlsx'
        ]

        report_withholdings = report._get_report_withholdings(self.ledger)

        self.assertEqual(report_withholdings, self.posted_withholding)

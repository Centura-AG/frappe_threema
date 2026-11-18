// Copyright (c) 2024, Centura AG and contributors
// For license information, please see license.txt

const originalSetupFieldnameSelect = frappe.notification.setup_fieldname_select;

const isPhoneField = (df) => ['Phone', 'Mobile'].includes(df.options);

frappe.notification.setup_fieldname_select = function (frm) {
  if (frm.doc.channel !== 'Threema') {
    return originalSetupFieldnameSelect(frm);
  }
  if (!frm.doc.document_type) return;

  frappe.model.with_doctype(frm.doc.document_type, () => {
    const fields = frappe.get_doc('DocType', frm.doc.document_type).fields;
    const receiverFields = [];

    for (const df of fields) {
      if (isPhoneField(df)) {
        receiverFields.push({
          value: df.fieldname,
          label: `${df.fieldname} (${__(df.label, null, df.parent)})`
        });
      }

      if (frappe.model.table_fields.includes(df.fieldtype)) {
        const childFields = frappe.get_doc('DocType', df.options)?.fields || [];
        for (const cdf of childFields.filter(isPhoneField)) {
          receiverFields.push({
            value: `${cdf.fieldname},${df.fieldname}`,
            label: `${df.fieldname} > ${cdf.fieldname} (${__(cdf.label, null, cdf.parent)})`
          });
        }
      }
    }

    frm.fields_dict.recipients.grid.update_docfield_property(
      'receiver_by_document_field',
      'options',
      ['', 'owner', ...receiverFields]
    );
  });
};

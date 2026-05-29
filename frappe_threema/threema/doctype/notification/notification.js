// Copyright (c) 2024, Centura AG and contributors
// For license information, please see license.txt

const _originalSetupFieldnameSelect =
  frappe.notification.setup_fieldname_select;

frappe.notification.setup_fieldname_select = function (frm) {
  _originalSetupFieldnameSelect(frm);

  if (frm.doc.channel !== 'Threema') {
    return;
  }

  frappe.model.with_doctype(frm.doc.document_type, function () {
    const fields = frappe.get_doc('DocType', frm.doc.document_type).fields;

    const receiverFields = [];
    fields.forEach((df) => {
      if (df.options === 'Phone' || df.options === 'Mobile') {
        receiverFields.push({
          value: df.fieldname,
          label: df.fieldname + ' (' + __(df.label, null, df.parent) + ')'
        });
      }
      if (frappe.model.table_fields.includes(df.fieldtype)) {
        const childFields = frappe.get_doc('DocType', df.options)?.fields || [];
        childFields.forEach((cdf) => {
          if (cdf.options === 'Phone' || cdf.options === 'Mobile') {
            receiverFields.push({
              value: cdf.fieldname + ',' + df.fieldname,
              label:
                df.fieldname +
                ' > ' +
                cdf.fieldname +
                ' (' +
                __(cdf.label, null, cdf.parent) +
                ')'
            });
          }
        });
      }
    });

    frm.fields_dict.recipients.grid.update_docfield_property(
      'receiver_by_document_field',
      'options',
      [''].concat(['owner']).concat(receiverFields)
    );
  });
};

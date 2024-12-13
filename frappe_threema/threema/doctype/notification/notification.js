frappe.notification = {
    setup_fieldname_select: function (frm) {
        // get the doctype to update fields
        if (!frm.doc.document_type) {
            return;
        }

        frappe.model.with_doctype(frm.doc.document_type, function () {
            let get_select_options = function (df, parent_field) {
                // Append parent_field name along with fieldname for child table fields
                let select_value = parent_field ? df.fieldname + "," + parent_field : df.fieldname;
                let path = parent_field ? parent_field + " > " + df.fieldname : df.fieldname;

                return {
                    value: select_value,
                    label: path + " (" + __(df.label, null, df.parent) + ")",
                };
            };
            let get_receiver_fields = function (
                fields,
                is_extra_receiver_field = (_) => {
                    return false;
                }
            ) {
                // finds receiver fields from the fields or any child table
                // by default finds any link to the User doctype
                // however an additional optional predicate can be passed as argument
                // to find additional fields
                let is_receiver_field = function (df) {
                    return (
                        is_extra_receiver_field(df)
                    );
                };
                let extract_receiver_field = function (df) {
                    // Add recipients from child doctypes into select dropdown
                    if (frappe.model.table_fields.includes(df.fieldtype)) {
                        let child_fields = frappe.get_doc("DocType", df.options).fields;
                        return $.map(child_fields, function (cdf) {
                            return is_receiver_field(cdf)
                                ? get_select_options(cdf, df.fieldname)
                                : null;
                        });
                    } else {
                        return is_receiver_field(df) ? get_select_options(df) : null;
                    }
                };
                return $.map(fields, extract_receiver_field);
            };

            const fields = frappe.get_doc("DocType", frm.doc.document_type).fields;

            if (["Threema"].includes(frm.doc.channel)) {
                const receiver_fields = get_receiver_fields(fields, function (df) {
                    return df.options === "Phone";
                });
                frm.fields_dict.recipients.grid.update_docfield_property(
                    "receiver_by_document_field",
                    "options",
                    [""].concat(["owner"]).concat(receiver_fields)
                );
            }
        });
    }
};

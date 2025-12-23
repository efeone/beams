frappe.pages['m1-ticket-dashboard'].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Ticket Dashboard',
        single_column: true
    });

    page.add_field({
        label: __("Timespan"),
        fieldname: "timespan",
        fieldtype: "Select",
        options: "Last 7 Days\nLast 30 Days\nCustom",
        default: "Last 7 Days",
        change() {
            const timespan = page.fields_dict.timespan.get_value();
            set_dates_by_timespan(page, timespan);
            refresh_cards(page);
        }
    });

    make_filters(page);

    set_dates_by_timespan(page, "Last 7 Days");

    // Card Container
    page.body.append(`
        <br>
        <div id="ticket-cards" class="ticket-cards" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:20px;">
        </div>
    `);

    refresh_cards(page);
};

function make_filters(page) {

    // Define all filters except Status
    const filters = [
        { label: "From Date", fieldname: "from_date", fieldtype: "Date", default: frappe.datetime.add_days(frappe.datetime.get_today(), -6) },
        { label: "To Date", fieldname: "to_date", fieldtype: "Date", default: frappe.datetime.get_today() },
        { label: "Ticket Type", fieldname: "ticket_type", fieldtype: "Link", options: "HD Ticket Type" },
        { label: "Priority", fieldname: "priority", fieldtype: "Link", options: "HD Ticket Priority" },
        { label: "Subcategory", fieldname: "subcategory", fieldtype: "Link", options: "HD Ticket SubCategory" },
        { label: 'Team', fieldname: 'team', fieldtype: 'Link', options: 'HD Team' },
        { label: "Agent", fieldname: "agent", fieldtype: "Link", options: "HD Agent" },
    ];

    // Helper function for refresh
    const bind_refresh = (fieldname) => {
        let field = page.fields_dict?.[fieldname];
        if (field && field.$input) {
            field.$input.on('change', function () {
                refresh_cards(page);
            });
        }
    };

    // Create fields dynamically
    filters.forEach(f => {
        page.add_field({
            label: frappe._(f.label),
            fieldname: f.fieldname,
            fieldtype: f.fieldtype || "Link",
            options: f.options,
            default: f.default || undefined,
            read_only: f.read_only || 0,
            change() {
                if (page.fields_dict[f.fieldname].get_value()) {
                    refresh_cards(page);
                }
            }
        });
        bind_refresh(f.fieldname);
    });
}

function set_dates_by_timespan(page, timespan) {
    const today = frappe.datetime.get_today();

    let from_date = null;
    let to_date = today;

    const from_field = page.fields_dict.from_date;
    const to_field = page.fields_dict.to_date;

    if (timespan === "Last 7 Days") {
        from_date = frappe.datetime.add_days(today, -6);
    }
    else if (timespan === "Last 30 Days") {
        from_date = frappe.datetime.add_days(today, -29);
    }

    if (from_date) {
        from_field.set_value(from_date);
        to_field.set_value(to_date);

        from_field.df.read_only = 1;
        to_field.df.read_only = 1;
    } else {
        // Custom
        from_field.df.read_only = 0;
        to_field.df.read_only = 0;
    }

    from_field.refresh();
    to_field.refresh();
}



function refresh_cards(page) {
    if (!(page.fields_dict.from_date.get_value() && page.fields_dict.to_date.get_value())) {
        frappe.msgprint("Please select both From Date and To Date");
        return;
    }

    frappe.call({
        method: 'beams.beams.page.m1_ticket_dashboard.m1_ticket_dashboard.get_ticket_summary',
        args: {
            filters: {
                from_date: page.fields_dict.from_date?.value,
                to_date: page.fields_dict.to_date?.value,
                ticket_type: page.fields_dict.ticket_type?.value,
                priority: page.fields_dict.priority?.value,
                subcategory: page.fields_dict.subcategory?.value,
                team: page.fields_dict.team?.value,
                agent: page.fields_dict.agent?.value
            }
        },
        callback(r) {
            if (!r.message) return;
            const container = $('#ticket-cards');
            container.empty();
            $(frappe.render_template("m1_ticket_dashboard", {
                card_data: r.message.data
            })).appendTo(container);
        },
        freeze: true,
        freeze_message: 'Loading Dashboard'
    });
}
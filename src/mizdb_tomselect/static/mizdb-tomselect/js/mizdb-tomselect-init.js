addEventListener("DOMContentLoaded", (event) => {
    document.querySelectorAll("[is-tomselect]").forEach((elem) => {
        const defaults = {
            preload: 'focus',
            searchField: [],  // disable sifter search
            // Add bootstrap 'form-control' to the search input:
            controlInput: '<input class="form-control mb-1"/>',
            // Pad the dropdown to make it appear in a neat box:
            dropdownClass: 'ts-dropdown p-2',

            valueField: elem.dataset['valueField'] || "id",
            labelField: elem.dataset['labelField'] || "name",
            url: elem.dataset['autocompleteUrl'],
            model: elem.dataset['model'],
            createField: elem.dataset['createField'],

            load: function(query, callback) {
                // TODO: toggle 'create' property according to results?
                const params = new URLSearchParams({
                    'q': encodeURIComponent(query),
                    'model': encodeURIComponent(this.settings.model)
                })
                fetch(`${this.settings.url}?${params.toString()}`)
                    .then(response => response.json())
                    .then(json => {
                        this.clearOptions();
                        callback(json.results);
                    }).catch(()=>{
                        callback();
                    });
        
            },
            plugins: {
                // Add the dropdown input plugin so we get a input element that can have the theme's border-shadow
                dropdown_input: ''
            }
        }
        let settings = defaults
        if (elem.hasAttribute('is-tabular')) {
            // Update the settings for tabular stuff
            settings = Object.assign({}, settings, {
                extra_columns: elem.dataset['extraColumns'].split(',') || [],
                // TODO: adjust col width when not using extra columns
                render: {
                    option: function(data, escape) {
                        let columns = `<div class="col-1">${data[this.settings.valueField]}</div>
                                       <div class="col-5">${data[this.settings.labelField]}</div>`;
                        let col_width = 6 / this.settings.extra_columns.length;
                        for (var c of this.settings.extra_columns){
                            columns += `<div class="col-${col_width}">${data[c] || ""}</div>`
                        }
                        return `<div class="row">${columns}</div>`;
                    },
                    option_create: function(data, escape) {
                        return '<div class="create bg-secondary text-bg-secondary">Hinzufügen <strong>' + escape(data.input) + '</strong>&hellip;</div>';
                    }
                },
            });
            Object.assign(settings.plugins, {
                'dropdown_header': {
                    html: function(data){
                        let header = `<div class="col-1"><span class="${data.labelClass}">${data.valueFieldLabel}</span></div>
                                        <div class="col-5"><span class="${data.labelClass}">${data.labelFieldLabel}</span></div>`
                        for (var h of data.extra_headers) {
                            header += `<div class="col-2"><span class="${data.labelClass}">${h}</span></div>`
                        }
                        return `<div class="${data.headerClass}">
                                    <div class="${data.titleRowClass}">${header}</div>
                                </div>`;
                    },
                    valueFieldLabel: elem.dataset['valueFieldLabel'],
                    labelFieldLabel: elem.dataset['labelFieldLabel'],
                    extra_headers: elem.dataset['extraHeaders'].split(',') || [],
                    headerClass: "container-fluid bg-primary text-bg-primary pt-1 pb-1 mb-2",
                    titleRowClass: "row",
                },
            });
        }
        new TomSelect(elem, settings);
    });
})
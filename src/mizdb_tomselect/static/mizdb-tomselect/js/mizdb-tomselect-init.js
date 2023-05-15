addEventListener("DOMContentLoaded", (event) => {
    document.querySelectorAll("[is-tomselect]").forEach((elem) => {
        let settings = {
            preload: 'focus',
            searchField: [],  // disable sifter search
            // Add bootstrap 'form-control' to the search input:
            controlInput: '<input class="form-control mb-1"/>',
            // Pad the dropdown to make it appear in a neat box:
            dropdownClass: 'ts-dropdown p-2',

            valueField: elem.dataset['valueField'] || "id",
            labelField: elem.dataset['labelField'] || "name",
            createField: elem.dataset['createField'],
            plugins: {
                // Use the dropdown input plugin to introduce a separate search
                // input element that we can style more easily than the default
                // TomSelect input (f.ex. to have the element respect the 
                // theme's box-shadow colour).
                dropdown_input: null,
            },
            render: {
                option_create: function(data, escape) {
                    return '<div class="create bg-secondary text-bg-secondary">Hinzufügen <strong>' + escape(data.input) + '</strong>&hellip;</div>';
                },
                loading_more: function(data, escape) {
                    return `<div class="loading-more-results py-2 d-flex align-items-center"><div class="spinner"></div> Lade mehr Ergebnisse </div>`;
                }
            }
        }

        const endpoint = elem.dataset['autocompleteUrl'];
        if (endpoint) {
            const model = elem.dataset['model'];

            function buildUrl(query, page){
                let params = new URLSearchParams({
                    'q': encodeURIComponent(query),
                    'p': page,
                });
                if (model) {
                    params.append('model', encodeURIComponent(model));
                }
                return `${endpoint}?${params.toString()}`;
            }

            settings.plugins.virtual_scroll = null;
            settings.firstUrl = function(query) {
                return buildUrl(query, 1);
            }

            settings.load = function(query, callback){
                const url = this.getUrl(query);
                fetch(url)
                    .then(response => response.json())
                    .then(json => {
                        if (json.has_more){
                            this.setNextUrl(query, buildUrl(query, json.page + 1));
                        }
                        // Workaround for an issue of the virtual scroll plugin
                        // where it  scrolls to the top of the results whenever
                        // a new page of results is added.
                        // https://github.com/orchidjs/tom-select/issues/556
                        const _scrollToOption = this.scrollToOption;
                        this.scrollToOption = () => {};
                        callback(json.results);
                        this.scrollToOption = _scrollToOption;
                    }).catch(()=>{
                        callback();
                    });
            }

            // TODO: enable item creation
            if (model && elem.dataset['createField']) {
                settings.create = true;
            }
        }
        
        if (elem.hasAttribute('is-tabular')) {
            // Render the dropdown as a table.
            settings.extra_columns = elem.dataset['extraColumns'].split(',') || [];

            // Allocate more width to the label field column if there are only
            // some extra columns, otherwise allocate equal width to all columns.
            if (settings.extra_columns.length > 0 && settings.extra_columns.length < 4) {
                settings.label_col_width = 'col-5';
            }
            else {
                settings.label_col_width = 'col';
            }

            settings.render.option = function(data, escape){
                let columns = `<div class="col-1">${data[this.settings.valueField]}</div>
                               <div class="${this.settings.label_col_width}">${data[this.settings.labelField]}</div>`;
                for (var c of this.settings.extra_columns){
                    columns += `<div class="col">${data[c] || ""}</div>`
                }
                return `<div class="row">${columns}</div>`;
            }

            // If there are more columns than just the value field and the 
            // label field, add a table header using the dropdown header plugin.
            if (settings.extra_columns) {
                settings.plugins.dropdown_header = {
                    html: function(data){
                        let header = `<div class="col-1"><span class="${data.labelClass}">${data.valueFieldLabel}</span></div>
                                        <div class="${data.labelColWidth}"><span class="${data.labelClass}">${data.labelFieldLabel}</span></div>`
                        for (var h of data.extra_headers) {
                            header += `<div class="col"><span class="${data.labelClass}">${h}</span></div>`
                        }
                        return `<div class="${data.headerClass}">
                                    <div class="${data.titleRowClass}">${header}</div>
                                </div>`;
                    },
                    valueFieldLabel: elem.dataset['valueFieldLabel'],
                    labelFieldLabel: elem.dataset['labelFieldLabel'],
                    labelColWidth: settings.label_col_width,
                    extra_headers: elem.dataset['extraHeaders'].split(',') || [],
                    headerClass: "container-fluid bg-primary text-bg-primary pt-1 pb-1 mb-2",
                    titleRowClass: "row",
                }
            }
        }
        new TomSelect(elem, settings);
    });
})
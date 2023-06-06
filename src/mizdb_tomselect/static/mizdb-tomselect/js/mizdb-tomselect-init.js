document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('[is-tomselect]').forEach((elem) => {
    const settings = {
      preload: 'focus',
      maxOptions: null,
      searchField: [], // disable sifter search
      // Add bootstrap 'form-control' to the search input:
      controlInput: '<input class="form-control mb-1"/>',
      // Pad the dropdown to make it appear in a neat box:
      dropdownClass: 'ts-dropdown p-2',

      valueField: elem.dataset.valueField,
      labelField: elem.dataset.labelField,
      createField: elem.dataset.createField,
      plugins: {
        dropdown_input: null
      },
      render: {
        no_results: function (data, escape) {
          return '<div class="no-results">Keine Ergebnisse</div>'
        },
        option_create: function (data, escape) {
          return '<div class="create bg-secondary text-bg-secondary">Hinzufügen <strong>' + escape(data.input) + '</strong>&hellip;</div>'
        },
        loading_more: function (data, escape) {
          return '<div class="loading-more-results py-2 d-flex align-items-center"><div class="spinner"></div> Lade mehr Ergebnisse </div>'
        },
        no_more_results: function (data, escape) {
          return '<div class="no-more-results">Keine weiteren Ergebnisse</div>'
        }
      }
    }

    if (elem.hasAttribute('is-multiple')) {
      settings.maxItems = 10
      settings.plugins.remove_button = { title: 'Entfernen' }
      settings.plugins.clear_button = { title: 'Auswahl aufheben' }
    }

    const endpoint = elem.dataset.autocompleteUrl
    if (endpoint) {
      const model = elem.dataset.model

      function buildUrl (query, page) {
        const params = new URLSearchParams({
          q: encodeURIComponent(query),
          p: page
        })
        if (model) {
          params.append('model', encodeURIComponent(model))
        }
        return `${endpoint}?${params.toString()}`
      }

      settings.plugins.virtual_scroll = null
      settings.firstUrl = function (query) {
        return buildUrl(query, 1)
      }

      settings.load = function (query, callback) {
        const url = this.getUrl(query)
        fetch(url)
          .then(response => response.json())
          .then(json => {
            if (json.has_more) {
              this.setNextUrl(query, buildUrl(query, json.page + 1))
            }
            this.settings.showCreateOption = json.show_create_option
            // Workaround for an issue of the virtual scroll plugin
            // where it  scrolls to the top of the results whenever
            // a new page of results is added.
            // https://github.com/orchidjs/tom-select/issues/556
            const _scrollToOption = this.scrollToOption
            this.scrollToOption = () => {}
            callback(json.results)
            this.scrollToOption = _scrollToOption
          }).catch(() => {
            callback()
          })
      }
    }

    if (elem.hasAttribute('is-tabular')) {
      // Render the dropdown as a table.
      settings.extra_columns = JSON.parse(elem.dataset.extraColumns)

      // Allocate more width to the label field column if there are only
      // some extra columns, otherwise allocate equal width to all columns.
      if (settings.extra_columns.length > 0 && settings.extra_columns.length < 4) {
        settings.label_col_width = 'col-5'
      } else {
        settings.label_col_width = 'col'
      }

      settings.render.option = function (data, escape) {
        let columns = `<div class="col-1">${data[this.settings.valueField]}</div>
                               <div class="${this.settings.label_col_width}">${data[this.settings.labelField]}</div>`
        for (const c of this.settings.extra_columns) {
          columns += `<div class="col">${data[c] || ''}</div>`
        }
        return `<div class="row">${columns}</div>`
      }

      // If there are more columns than just the value field and the
      // label field, add a table header using the dropdown header plugin.
      if (settings.extra_columns) {
        // TODO: could settings.plugin just be an array?
        settings.plugins.dropdown_header = {
          html: function (data) {
            let header = `<div class="col-1"><span class="${data.labelClass}">${data.valueFieldLabel}</span></div>
                                        <div class="${data.labelColWidth}"><span class="${data.labelClass}">${data.labelFieldLabel}</span></div>`
            for (const h of data.extra_headers) {
              header += `<div class="col"><span class="${data.labelClass}">${h}</span></div>`
            }
            return `<div class="${data.headerClass}">
                                    <div class="${data.titleRowClass}">${header}</div>
                                </div>`
          },
          valueFieldLabel: elem.dataset.valueFieldLabel,
          labelFieldLabel: elem.dataset.labelFieldLabel,
          labelColWidth: settings.label_col_width,
          extra_headers: JSON.parse(elem.dataset.extraHeaders),
          headerClass: 'container-fluid bg-primary text-bg-primary pt-1 pb-1 mb-2 dropdown-header',
          titleRowClass: 'row'
        }
      }
    }
    const ts = new TomSelect(elem, settings)

    // Reload the default/initial options when the input is cleared:
    ts.on('type', (query) => {
      if (!query) {
        ts.load('')
        ts.refreshOptions()
      }
    })

    // Add a footer that contains a link to the add page and a link to the
    // changelist.
    const changelistURL = elem.dataset.changelistUrl
    const addURL = elem.dataset.addUrl
    if (changelistURL || addURL) {
      const footer = document.createElement('div')
      footer.classList.add('d-flex', 'mt-1', 'dropdown-footer')

      if (addURL) {
        const addBtn = document.createElement('a')
        addBtn.classList.add('btn', 'btn-success', 'invisible', 'add-btn')
        addBtn.href = addURL
        addBtn.target = '_blank'
        addBtn.innerHTML = 'Hinzufügen'
        footer.appendChild(addBtn)
        ts.on('load', () => {
          if (ts.settings.showCreateOption) {
            addBtn.classList.remove('invisible')
            addBtn.classList.add('visible')
          } else {
            addBtn.classList.remove('visible')
            addBtn.classList.add('invisible')
          }
        })
        ts.on('type', (query) => {
          if (query) {
            addBtn.innerHTML = `'${query}' hinzufügen...`
          } else {
            addBtn.innerHTML = 'Hinzufügen'
          }
        })

        // If given a create field, try adding new model objects via AJAX request.
        const createField = elem.dataset.createField
        if (createField) {
          addBtn.addEventListener('click', (e) => {
            if (!ts.lastValue) {
              // No search term: just open the add page.
              return
            }
            e.preventDefault()
            const form = new FormData()
            form.append('create-field', createField)
            form.append(createField, ts.lastValue)
            form.append('model', elem.dataset.model)
            const options = {
              method: 'POST',
              headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
              },
              body: form
            }
            fetch(elem.dataset.autocompleteUrl, options)
              .then(response => {
                if (!response.ok) {
                  throw new Error('POST request failed.')
                }
                return response.json()
              }).then(json => {
                const data = {}
                data[ts.settings.valueField] = json.pk
                data[ts.settings.labelField] = json.text
                ts.addOption(data, true)
                ts.setCaret(ts.caretPos)
                ts.addItem(json.pk)
              }).catch((error) => console.log(error))
          })
        }
      }

      if (changelistURL) {
        const changelistLink = document.createElement('a')
        changelistLink.classList.add('btn', 'btn-info', 'ms-auto', 'cl-btn')
        changelistLink.href = changelistURL
        changelistLink.target = '_blank'
        changelistLink.innerHTML = 'Änderungsliste'
        footer.appendChild(changelistLink)
        ts.on('type', (query) => {
          if (query) {
            // Update the URL to the changelist to include the query
            const queryString = new URLSearchParams({ q: encodeURIComponent(query) }).toString()
            changelistLink.href = `${changelistURL}?${queryString}`
          } else {
            changelistLink.href = changelistURL
          }
        })
      }

      ts.dropdown.appendChild(footer)
    }
  })
})

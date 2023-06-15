import TomSelect from 'tom-select/src/tom-select'

/* eslint-disable camelcase */
import clear_button from 'tom-select/src/plugins/clear_button/plugin'
import dropdown_header from 'tom-select/src/plugins/dropdown_header/plugin'
import dropdown_input from 'tom-select/src/plugins/dropdown_input/plugin'
import remove_button from 'tom-select/src/plugins/remove_button/plugin'
import virtual_scroll from 'tom-select/src/plugins/virtual_scroll/plugin'
/* eslint-enable camelcase */

TomSelect.define('clear_button', clear_button)
TomSelect.define('dropdown_header', dropdown_header)
TomSelect.define('dropdown_input', dropdown_input)
TomSelect.define('remove_button', remove_button)
TomSelect.define('virtual_scroll', virtual_scroll)

function getSettings (elem) {
  function buildUrl (query, page) {
    const params = new URLSearchParams({
      q: encodeURIComponent(query),
      p: page,
      model: encodeURIComponent(elem.dataset.model)
    })
    return `${elem.dataset.autocompleteUrl}?${params.toString()}`
  }
  elem.extraColumns = elem.hasAttribute('is-tabular') ? JSON.parse(elem.dataset.extraColumns) : ''
  elem.labelColClass = elem.extraColumns.length > 0 && elem.extraColumns.length < 4 ? 'col-5' : 'col'
  return {
    preload: 'focus',
    maxOptions: null,
    searchField: [], // disable sifter search
    // Add bootstrap 'form-control' to the search input:
    controlInput: '<input class="form-control mb-1"/>',
    // Pad the dropdown to make it appear in a neat box:
    dropdownClass: 'ts-dropdown p-2',
    maxItems: elem.hasAttribute('is-multiple') ? 10 : null,

    valueField: elem.dataset.valueField,
    labelField: elem.dataset.labelField,
    createField: elem.dataset.createField,
    extraColumns: elem.extraColumns,
    labelColClass: elem.labelColClass,

    firstUrl: (query) => buildUrl(query, 1),
    load: function (query, callback) {
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
    },
    plugins: getPlugins(elem),
    render: getRenderTemplates(elem)
  }
}

function getPlugins (elem) {
  const plugins = {
    dropdown_input: null,
    virtual_scroll: null
  }

  if (elem.hasAttribute('is-multiple')) {
    plugins.remove_button = { title: 'Entfernen' }
    plugins.clear_button = { title: 'Auswahl aufheben' }
  }

  if (elem.hasAttribute('is-tabular')) {
    plugins.dropdown_header = {
      html: function (settings) {
        let header = `<div class="col-1"><span class="${settings.labelClass}">${settings.valueFieldLabel}</span></div>
                      <div class="${settings.labelColClass}"><span class="${settings.labelClass}">${settings.labelFieldLabel}</span></div>`
        for (const h of settings.extraHeaders) {
          header += `<div class="col"><span class="${settings.labelClass}">${h}</span></div>`
        }
        return `<div class="${settings.headerClass}"><div class="${settings.titleRowClass}">${header}</div></div>`
      },
      valueFieldLabel: elem.dataset.valueFieldLabel,
      labelFieldLabel: elem.dataset.labelFieldLabel,
      labelColClass: elem.labelColClass,
      extraHeaders: JSON.parse(elem.dataset.extraHeaders),
      headerClass: 'container-fluid bg-primary text-bg-primary pt-1 pb-1 mb-2 dropdown-header',
      titleRowClass: 'row'
    }
  }
  return plugins
}

function getRenderTemplates (elem) {
  const templates = {
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
  if (elem.hasAttribute('is-tabular')) {
    templates.option = function (data, escape) {
      let columns = `<div class="col-1">${data[this.settings.valueField]}</div>
                     <div class="${this.settings.labelColClass}">${data[this.settings.labelField]}</div>`
      for (const c of this.settings.extraColumns) {
        columns += `<div class="col">${escape(data[c]) || ''}</div>`
      }
      return `<div class="row">${columns}</div>`
    }
  }
  return templates
}

function attachFooter (ts, elem) {
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
}

document.addEventListener('DOMContentLoaded', (event) => {
  document.querySelectorAll('[is-tomselect]').forEach((elem) => {
    const ts = new TomSelect(elem, getSettings(elem))
    attachFooter(ts, elem)

    // Reload the default/initial options when the input is cleared:
    ts.on('type', (query) => {
      if (!query) {
        ts.load('')
        ts.refreshOptions()
      }
    })
  })
})

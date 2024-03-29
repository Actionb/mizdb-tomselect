import TomSelect from 'tom-select/src/tom-select'

/* eslint-disable camelcase */
import clear_button from 'tom-select/src/plugins/clear_button/plugin'
import dropdown_header from 'tom-select/src/plugins/dropdown_header/plugin'
import dropdown_input from 'tom-select/src/plugins/dropdown_input/plugin'
import remove_button from 'tom-select/src/plugins/remove_button/plugin'
import virtual_scroll from 'tom-select/src/plugins/virtual_scroll/plugin'
import no_backspace_delete from 'tom-select/src/plugins/no_backspace_delete/plugin'
import edit_button from './plugins/edit_button'
import dropdown_footer from './plugins/dropdown_footer'
import add_button from './plugins/add_button'
import changelist_button from './plugins/changelist_button'
/* eslint-enable camelcase */

import merge from 'lodash/merge'

// TomSelect plugins
TomSelect.define('clear_button', clear_button)
TomSelect.define('dropdown_header', dropdown_header)
TomSelect.define('dropdown_input', dropdown_input)
TomSelect.define('remove_button', remove_button)
TomSelect.define('virtual_scroll', virtual_scroll)
TomSelect.define('no_backspace_delete', no_backspace_delete)
// mizdb-tomselect plugins
TomSelect.define('edit_button', edit_button)
TomSelect.define('dropdown_footer', dropdown_footer)
TomSelect.define('add_button', add_button)
TomSelect.define('changelist_button', changelist_button)

document.addEventListener('DOMContentLoaded', (event) => {
  // Do not initialize elements which contain '__prefix__'; those are part of
  // empty form templates for django formsets:
  const selector = '[is-tomselect]:not([id*="__prefix__"])'
  document.querySelectorAll(selector).forEach(elem => init(elem))

  // Initialize dynamically added elements that match the selector.
  new window.MutationObserver(mutations => {
    mutations.forEach(mutation =>
      mutation.addedNodes.forEach(node => {
        if (!(node instanceof window.HTMLElement)) return
        node.querySelectorAll(selector).forEach(elem => init(elem))
        if (node.matches(selector)) init(node)
      })
    )
  }).observe(document.documentElement, { childList: true, subtree: true })
})

/**
 * Create a TomSelect from the given element.
 *
 * @param {HTMLElement} elem the HTML element to turn into a TomSelect
 */
function init (elem) {
  if (elem.tomselect) {
    // Already initialized
    return
  }

  // Attach the init function to the element so it can be called in a custom
  // handler for the init event.
  elem.initMIZSelect = (userSettings) => {
    if (elem.tomselect) {
      // Already initialized
      return elem.tomselect
    }
    const settings = merge(getSettings(elem), userSettings)
    return new TomSelect(elem, settings)
  }
  const initEvent = new Event('initMIZSelect', { bubbles: true })
  elem.dispatchEvent(initEvent)
  const ts = elem.tomselect ? elem.tomselect : elem.initMIZSelect()

  // Open the dropdown instead of marking an item when clicking on a multi
  // select item.
  ts.hook('instead', 'onItemSelect', (evt, item) => false)

  // Reload the default/initial options when the input is cleared:
  ts.on('type', (query) => {
    if (!query) {
      ts.load('')
      ts.refreshOptions()
    }
  })

  if (elem.filterByElem) {
    // Force re-fetching the options when the value of the filterBy element
    // changes.
    elem.filterByElem.addEventListener('change', () => {
      // Reset the pagination (query:url) mapping of the virtual_scroll
      // plugin. This is necessary because the filter value is not part of
      // the query string, which means that the mapping might return an URL
      // that is incorrect for the current filter.
      ts.getUrl(null)
      // Clear all options, but leave the selected items.
      ts.clearOptions()
      // Remove the flag that this element has already been loaded.
      ts.wrapper.classList.remove('preloaded')
    })
  }

  // When necessary, scroll the dropdown into view when opening it.
  ts.on('dropdown_open', (dropdown) => {
    const rect = dropdown.getBoundingClientRect()
    // The dropdown may not have reached its full height (still loading options)
    // yet, so using rect.bottom now may give a value that is too low.
    // Instead, calculate the bottom position from the top plus a fixed amount.
    // If the bottom end of the dropdown is outside the windows interior height,
    // scroll the dropdown into the center of the view.
    if (rect.top + 400 > window.innerHeight) dropdown.scrollIntoView({ block: 'center' })
  })

  // Disable or enable tomselect when the disabled attribute changes.
  new window.MutationObserver(mutations => {
    mutations.forEach(mutation => {
      if (mutation.target.disabled && !ts.isDisabled) {
        ts.disable()
      } else if (!mutation.target.disabled && ts.isDisabled) {
        ts.enable()
      }
    })
  }).observe(elem, { attributeFilter: ['disabled'] })
}

/**
 * A global function that handles closing popups opened by 'add' and 'edit'
 * buttons. This function is called directly by script in the popup response,
 * and it dispatches the `popupDismissed` event for the button that opened the
 * popup. An event handler can then be used to update the form with the changes
 * made in the popup.
 *
 * @param popup the popup window to dismiss
 * @param data the updated data of the object that was modified by the popup
 */
window.dismissPopup = (popup, data) => {
  const dismissEvent = new window.CustomEvent('popupDismissed', { detail: { data } })
  const btn = document.getElementById(popup.name)
  btn.dispatchEvent(dismissEvent)
  popup.close()
}

/**
 * Return the settings for the TomSelect constructor for the given element.
 *
 * @param {HTMLElement} elem the HTML element to turn into a TomSelect
 * @returns an object of settings
 */
function getSettings (elem) {
  function buildUrl (query, page) {
    // Get the fields to select with queryset.values()
    let valuesSelect = [elem.dataset.valueField, elem.dataset.labelField]
    if (elem.extraColumns) {
      valuesSelect = valuesSelect.concat(elem.extraColumns)
    }
    const params = new URLSearchParams({
      q: query,
      p: page,
      model: elem.dataset.model,
      sl: elem.dataset.searchLookup,
      vs: JSON.stringify(valuesSelect)
    })
    if (elem.filterByElem) {
      params.append('f', `${elem.filterByLookup}=${elem.filterByElem.value}`)
    }
    return `${elem.dataset.autocompleteUrl}?${params.toString()}`
  }
  elem.extraColumns = elem.hasAttribute('is-tabular') ? JSON.parse(elem.dataset.extraColumns) : []
  elem.labelColClass = elem.extraColumns.length > 0 && elem.extraColumns.length < 4 ? 'col-5' : 'col'
  if (elem.dataset.filterBy) {
    const filterBy = JSON.parse(elem.dataset.filterBy)
    elem.filterByElem = getElementByPrefixedName(filterBy[0], [getFormPrefix(elem)])
    elem.filterByLookup = filterBy[1]
  }
  return {
    preload: 'focus',
    maxOptions: null,
    searchField: [], // disable sifter search
    // Add bootstrap 'form-control' to the search input:
    controlInput: '<input class="form-control mb-1 bg-light-subtle"/>',
    // Pad the dropdown to make it appear in a neat box:
    dropdownClass: 'ts-dropdown p-2 bg-body text-body',
    maxItems: elem.hasAttribute('is-multiple') ? null : 1,
    itemClass: 'item bg-body text-body rounded px-1',

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

/**
 * Return the TomSelect plugin settings to use for the given element.
 *
 * @param {HTMLElement} elem the HTML element to turn into a TomSelect
 * @returns an object of plugin settings
 */
function getPlugins (elem) {
  const removeImage = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-x text-danger"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>'
  const plugins = {
    dropdown_input: null,
    virtual_scroll: null,
    edit_button: { editUrl: elem.dataset.editUrl },
    no_backspace_delete: null
  }

  if (elem.dataset.addUrl) {
    plugins.add_button = { addUrl: elem.dataset.addUrl }
  }

  if (elem.dataset.changelistUrl) {
    plugins.changelist_button = { changelistUrl: elem.dataset.changelistUrl }
  }

  if (elem.hasAttribute('can-remove')) {
    plugins.remove_button = { label: removeImage }
  }

  if (elem.hasAttribute('is-multiple')) {
    plugins.clear_button = null
  }

  if (elem.hasAttribute('is-tabular')) {
    plugins.dropdown_header = {
      html: function (settings) {
        let header = `<div class="${settings.labelColClass}"><span class="${settings.labelClass}">${settings.labelFieldLabel}</span></div>`
        for (const h of settings.extraHeaders) {
          header += `<div class="col"><span class="${settings.labelClass}">${h}</span></div>`
        }
        header += `<div class="col-1"><span class="${settings.labelClass}">${settings.valueFieldLabel}</span></div>`
        return `<div class="${settings.headerClass}"><div class="${settings.titleRowClass}">${header}</div></div>`
      },
      valueFieldLabel: elem.dataset.valueFieldLabel,
      labelFieldLabel: elem.dataset.labelFieldLabel,
      labelColClass: elem.labelColClass,
      extraHeaders: JSON.parse(elem.dataset.extraHeaders),
      headerClass: 'container-fluid bg-primary text-bg-primary pt-1 pb-1 mb-2 dropdown-header border-bottom-0',
      titleRowClass: 'row'
    }
  }
  return plugins
}

/**
 * Return the TomSelect templates to use for the given element.
 *
 * @param {HTMLElement} elem the HTML element to turn into a TomSelect
 * @returns an object of template declarations
 */
function getRenderTemplates (elem) {
  const templates = {
    loading_more: function (data, escape) {
      return '<div class="loading-more-results py-2 d-flex align-items-center"><div class="spinner"></div> Loading more results </div>'
    },
    item: function (data, escape) {
      return '<div><span>' + escape(data[this.settings.labelField]) + '</span></div>'
    }
  }
  if (elem.hasAttribute('is-tabular')) {
    templates.option = function (data, escape) {
      let columns = `<div class="${this.settings.labelColClass}">${data[this.settings.labelField]}</div>`
      for (const c of this.settings.extraColumns) {
        columns += `<div class="col">${escape(data[c] || '')}</div>`
      }
      columns += `<div class="col-1">${data[this.settings.valueField]}</div>`
      return `<div class="row">${columns}</div>`
    }
  }
  return templates
}

/**
 * Extract the form prefix from the name of the given element.
 *
 * @param elem a HTML element belonging to django form
 * @returns the form prefix of the django form
 */
function getFormPrefix (elem) {
  const parts = elem.getAttribute('name').split('-').slice(0, -1)
  if (parts.length) {
    return parts.join('-') + '-'
  }
  return ''
}

/**
 * Walk through the given (form) prefixes and return the first element
 * matching prefix + name.
 *
 * @param {string} name the name of a form element
 * @param {string[]} prefixes an array of form prefixes
 * @returns a form element with name that matches a prefix and the given name
 */
function getElementByPrefixedName (name, prefixes) {
  const _prefixes = prefixes || []
  _prefixes.push('')
  for (let i = 0; i < _prefixes.length; i++) {
    const element = document.querySelector(`[name=${prefixes[i] + name}]`)
    if (element) {
      return element
    }
  }
}

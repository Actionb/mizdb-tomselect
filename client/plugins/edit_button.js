/**
   * Return a dom element from either a dom query string, jQuery object, a dom element or html string
   * https://stackoverflow.com/questions/494143/creating-a-new-dom-element-from-an-html-string-using-built-in-dom-methods-or-pro/35385518#35385518
   *
   * param query should be {}
   */

const getDom = query => {
  if (query.jquery) {
    return query[0]
  }

  if (query instanceof HTMLElement) { // eslint-disable-line no-undef
    return query
  }

  if (isHtmlString(query)) {
    const tpl = document.createElement('template')
    tpl.innerHTML = query.trim() // Never return a text node of whitespace as the result

    return tpl.content.firstChild
  }

  return document.querySelector(query)
}

const isHtmlString = arg => {
  if (typeof arg === 'string' && arg.indexOf('<') > -1) {
    return true
  }

  return false
}

/**
 * Plugin: "edit_button" (Tom Select)
 *
 * Attach an 'edit' link to each selected item.
 *
 * Configuration:
 *  label: the text of the link
 *  title: value of the title attribute of the link
 *  className: CSS classes of the link
 *  editUrl: the URL to link to. If omitted, no links will be added.
 *  editUrlPlaceholder: a placeholder in the edit URL to be substituted with
 *    the value of the selected item
 *  getEditUrl: a function that takes the plugin options, the selected item (div)
 *    and the value of the selected item. This function should return the final
 *    URL (placeholder replaced by the item value) to include in the link.
 */
export default function (userOptions) {
  const options = Object.assign({
    label: '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-edit-3 text-success"><path d="M12 20h9"></path><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path></svg>',
    title: 'Bearbeiten',
    className: 'edit',
    editUrl: '',
    editUrlPlaceholder: '{pk}',
    getEditUrl: (pluginOptions, item, value) => {
      return pluginOptions.editUrl.replace(pluginOptions.editUrlPlaceholder, value)
    }
  }, userOptions)

  if (!options.editUrl) return

  const html = `<a class="${options.className}" title="${options.title}" target="_blank">${options.label}</a>`

  this.hook('after', 'setupTemplates', () => {
    const orig = this.settings.render.item

    this.settings.render.item = (data, escape) => {
      const item = getDom(orig.call(this, data, escape))
      const editButton = getDom(html)
      editButton.href = options.getEditUrl(options, item, data[this.settings.valueField])
      editButton.addEventListener('click', (e) => {
        e.stopPropagation() // do not show the dropdown
      })
      item.appendChild(editButton)
      return item
    }
  })
}

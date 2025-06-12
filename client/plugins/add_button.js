// A helper function that first adds a new option with the given value and
// text, and then selects that new option.
function addAndSelectNewOption (ts, value, text) {
  const data = {}
  data[ts.settings.valueField] = value
  data[ts.settings.labelField] = text
  ts.addOption(data, true)
  ts.setCaret(ts.caretPos)
  ts.addItem(value)
}

/**
 * Plugin: "add_button" (Tom Select)
 *
 * Attach a button to the dropdown footer that sends the user to the 'add' page
 * of the element's model.
 *
 * Configuration:
 *   addUrl: the URL to the 'add' page. If omitted, no button will be added.
 *   className: CSS classes of the button
 *   label: the text of the button
 */
export default function (userOptions) {
  this.require('dropdown_footer')
  const options = Object.assign({
    addUrl: '',
    className: 'btn btn-success mizselect-add-btn d-none',
    label: 'Add',
    errorMessages: {
      error: 'Server Error! Something went wrong :(',
      unique: 'Object already exists. Please select it out of the available options.'
    }
  }, userOptions)

  if (!options.addUrl) return

  const elem = this.input
  const footer = this.dropdown_footer

  const addBtn = document.createElement('a')
  addBtn.classList.add(...options.className.split(' '))

  const url = new URL(options.addUrl, window.location.href)
  url.searchParams.set('_popup', '1')
  addBtn.href = url

  addBtn.id = `id_add_button_${elem.id}`
  addBtn.target = '_blank' // TODO: is this still needed with the popups?
  addBtn.innerHTML = options.label
  footer.appendChild(addBtn)

  // Add an alert box
  const errorMessages = options.errorMessages
  const alertPlaceholder = document.createElement('div')
  alertPlaceholder.id = 'alertPlaceholder'
  const appendAlert = (message, type) => {
    alertPlaceholder.innerHTML = ''
    const wrapper = document.createElement('div')
    wrapper.innerHTML = [
      `<div class="alert alert-${type} alert-dismissible" role="alert">`,
      `   <div>${message}</div>`,
      '   <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>',
      '</div>'
    ].join('')

    alertPlaceholder.append(wrapper)
  }
  this.hook('after', 'setup', () => {
    this.dropdown.insertBefore(alertPlaceholder, this.dropdown.children[0])
  })

  // After loading new options, check if the button should be shown.
  this.on('load', () => {
    if (this.settings.showCreateOption) {
      addBtn.classList.remove('d-none')
    } else {
      addBtn.classList.add('d-none')
    }
  })

  // Update the add button text when the user is typing.
  this.on('type', (query) => {
    if (query) {
      addBtn.innerHTML = `${options.label}: '${query}'`
    } else {
      addBtn.innerHTML = options.label
    }
  })
  // Reset the add button text when the dropdown is closed.
  this.on('blur', () => { addBtn.innerHTML = options.label })

  // Handle clicking the button.
  const createField = elem.dataset.createField
  addBtn.addEventListener('click', (e) => {
    e.preventDefault()
    // If given a create field, try adding new model objects via AJAX request.
    if (this.lastValue && createField) {
      const form = new FormData()
      form.append('create-field', createField)
      form.append(createField, this.lastValue)
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
            appendAlert(errorMessages.error, 'danger')
            throw new Error('POST request failed.')
          }
          return response.json()
        }).then(json => {
          if (json.error_type) {
            msg = errorMessages[json.error_type] || errorMessages["error"]
            appendAlert(msg, json.error_level)
          } else {
            addAndSelectNewOption(this, json.pk, json.text)
          }
        }).catch((error) => console.log(error))
    } else {
      // No search term or no createField set: just open the add page.
      const popup = window.open(addBtn.href, addBtn.id)
      popup.focus()
    }
  })

  // Handle the creation of a new object from a popup. Add the object to the
  // available options and select it.
  addBtn.addEventListener('popupDismissed', (e) => {
    addAndSelectNewOption(this, e.detail.data.value, e.detail.data.text)
  })
}

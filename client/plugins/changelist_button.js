/**
 * Plugin: "changelist_button" (Tom Select)
 *
 * Attach a button to the dropdown footer that sends the user to the 'changelist'
 * page of the element's model.
 *
 * Configuration:
 *   changelistUrl: the URL to the 'changelist' page. If omitted, no button will be added.
 *   className: CSS classes of the button
 *   label: the text of the button
 */
export default function (userOptions) {
  this.require('dropdown_footer')
  const options = Object.assign({
    changelistUrl: '',
    className: 'btn btn-info ms-auto cl-btn',
    label: 'Changelist'
  }, userOptions)

  if (!options.changelistUrl) return

  const changelistBtn = document.createElement('a')
  changelistBtn.classList.add(...options.className.split(' '))
  changelistBtn.href = options.changelistUrl
  changelistBtn.target = '_blank'
  changelistBtn.innerHTML = options.label
  this.dropdown_footer.appendChild(changelistBtn)
  this.on('type', (query) => {
    // TODO: include value of filterBy in query
    if (query) {
      // Update the URL to the changelist to include the query.
      const queryString = new URLSearchParams({ q: query }).toString()
      changelistBtn.href = `${options.changelistUrl}?${queryString}`
    } else {
      changelistBtn.href = options.changelistUrl
    }
  })
  this.on('blur', () => { changelistBtn.href = options.changelistUrl })
}

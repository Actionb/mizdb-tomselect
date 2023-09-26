/**
 * Plugin: "dropdown_footer" (Tom Select)
 *
 * Attach a div to the bottom of the dropdown. The div is meant to hold the
 * 'add' and 'changelist' buttons.
 */
export default function (userOptions) {
  const footer = document.createElement('div')
  footer.classList.add('d-flex', 'mt-1', 'flex-wrap', 'dropdown-footer')
  this.dropdown_footer = footer
  this.hook('after', 'setup', () => {
    this.dropdown.appendChild(footer)
  })
};

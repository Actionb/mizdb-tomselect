/* global opener */
const data = JSON.parse(document.getElementById('popup-response-data').dataset.popupResponse)
opener.dismissPopup(window, data)

jQuery(document).ready(function ($) {
  'use strict';

  $('#datetimepickerIn').datetimepicker({
    inline: true,
    sideBySide: true,
    minDate: new Date(),
    format:'d.m.Y H:i',
  });

  $("#datetimepickerIn").on("change.datetimepicker", ({date, oldDate}) => {
    $("#datetimeIn").val(date.format('DD.MM.YYYY HH:mm'));
  })

  $('#ui-datepicker-div').removeClass('ui-helper-hidden-accessible');
});

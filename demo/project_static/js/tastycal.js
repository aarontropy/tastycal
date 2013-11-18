

var save_start_time, save_end_time;
var event_duration = 60;		// end - start in minutes
var n = moment();

var current = {
	start: n,
	end: n.add(60, 'minutes'),
	duration: moment.duration(60, 'minutes')
}


$(document).ready(function() {
	
	$('.datefield').datepicker();
	$('.timefield').timepicker({
		minuteStep: 15,
        showInputs: false,
        disableFocus: true
	});

	// ---- ALL DAY ------------------------------------------------------------
	$('#all_day').on('click', function() {
		set_all_day($(this).is(':checked'));
	});


	// ---- REPEAT -------------------------------------------------------------
	$('#repeat').on('click', function() {
		set_repeat($(this).is(':checked'));
	});

	// ---- STOP REPEATING -----------------------------------------------------
	$("input[name='stopRepeatType']").on('click', function() {
		set_repeat_stop_type($(this).val());
	});

	// ---- SAVE START AND END TIMES -------------------------------------------
	$('#start_date').on('changeDate', function() { update_start(); });
	$('#start_time').on('change', function() { update_start(); });
	$('#end_date').on('changeDate', function() { update_end(); });
	$('#end_time').on('change', function() { update_end(); });

	var update_start = function() {
		current.start = moment( $('#start_date').val() + ' ' + $('#start_time').val() )
		// update end datetime to be start + duration
		if (current.duration != null) {
			current.end = moment(current.start).add(current.duration);
			dehydrate_event_time('end', current.end);
		}
	};

	var update_end = function() {
		current.end = moment( $('#end_date').val() + ' ' + $('#end_time').val() )
		// update duration
		current.duration = moment.duration(current.end.diff(current.start));
		update_duration_text();
	}

	// ---- BUTTONS ------------------------------------------------------------
	$('#save').on('click', function(e) {
		var is_new = ( $('#event_id').val() == '' && $('#repeat_id').val() == '')
		var is_repeat = ($('#repeat').is(':checked'));

		var url, data, data_obj, method;

		if (is_repeat) {
			data_obj = prep_repeat_data();
			if (is_new) {
				url = calendar_data.repeats_uri;
				method = 'POST';
			} else {
				url = $('#repeat_uri').val();
				method = 'PUT';
			}
		} else {
			data_obj = prep_event_data();
			if (is_new) {
				url = calendar_data.events_uri;
				method = 'POST';
			} else {
				url = $('#event_uri').val();
				method = 'PUT';
			}
		}


		console.log(data_obj);

		data = JSON.stringify(data_obj)
		call_api(url, data, method);
    	$('#eventModal').modal('hide')
	});

	$('#delete').on('click', function(e) {
		var url = $('#event_uri').val();
		var data = '';
		var method = "DELETE";
		call_api(url, data, method);
    	$('#eventModal').modal('hide')
		})

}); // document ready


// -----------------------------------------------------------------------------
// ---- FORM FUNCTIONS ---------------------------------------------------------
var set_all_day = function(all_day) {
	if (all_day) {
		$('#start_time').val('').prop('disabled', true);
		$('#end_time').val('').prop('disabled', true);	
		update_duration_text("");
	} else {
		dehydrate_event_time('start', current.start);
		dehydrate_event_time('end', current.end);
		$('#start_time').prop('disabled', false);
		$('#end_time').prop('disabled', false);			
		update_duration_text();
	}
};

var set_repeat = function(repeat) {	
	if (repeat) {
		$('#repeatTabButton').show();
	} else {
		$('#repeatTabButton').hide();
	}
};

var set_repeat_stop_type = function(stoptype) {
	if (stoptype=="until") {
		$('#until').prop('disabled', false);
		$('#count').prop('disabled', true);
	} else {
		$('#until').prop('disabled', true);
		$('#count').prop('disabled', false);
	}
}


// ---- DATA FUNCTIONS ---------------------------------------------------------
var prep_event_data = function() {
	data = {
		title: $('#title').val(),
		start: moment($('input[name="start_date"]').val() + ' ' + $('input[name="start_time"]').val()).toString(),
		end: moment($('input[name="end_date"]').val() + ' ' + $('input[name="end_time"]').val()).toString(),
		all_day: $('input[name="all_day"]').is(':checked'),
		repeat: $('input[name="repeat"]').is(':checked')
	};
	if (!isNaN($('#event_id').val())) {
		data.id = parseInt($('#event_id').val());
	}
	return data;
}

var prep_repeat_data = function() {

	var byweekday = []
	$('input[name="byweekday"]:checked').each(function() {
		byweekday.push( this.id );
	})

	data = {
		title: $('#title').val(),
		dtstart: moment($('input[name="start_date"]').val() + ' ' + $('input[name="start_time"]').val()).toString(),
		end: moment($('input[name="end_date"]').val() + ' ' + $('input[name="end_time"]').val()).toString(),
		duration: ($('input[name="all_day"]').is(':checked')) ? null : current.duration.minutes(),
		byweekday: byweekday,
		freq: parseInt($('input[name="freq"]:checked').val()),
		all_day: $('input[name="all_day"]').is(':checked'),
		repeat: $('input[name="repeat"]').is(':checked')
	};


	stoptype = $("input[name='stopRepeatType']:checked").val()
	if (stoptype=="until") {
		data.until = new Date($('#until').val());
	} else {
		data.count = parseInt($('#count').val());
	}

	if (!isNaN($('#repeat_id').val())) {
		data.id = parseInt($('#repeat_id').val());
	}
	return data;
};

var prep_form = function(event, repeat) {
	// default value for repeat is false
	repeat = typeof repeat !== 'undefined' ? repeat : false;

	current.start = moment(event.start);
	current.end = moment(event.end);
	current.duration = moment.duration(current.end.diff(current.start));

	$('#event_id').val(event.id);
	$('#event_uri').val(event.resource_uri);
	$('#title').val(event.title);
	dehydrate_event_time('start', current.start);
	dehydrate_event_time('end', current.end);
	// $('#start_date').val(moment(event.start).format('MM/DD/YYYY'));
	// $('#end_date').val(event.end ? moment(event.end).format('MM/DD/YYYY') : "");
	// if (!event.allDay) {
	// 	$('#start_time').val(moment(event.start).format('h:mm A') );
	// 	$('#end_time').val(event.end ? moment(event.end).format('h:mm A') : "" );
	// }
	console.log(event.allDay);
	$('#all_day').prop('checked', event.allDay);
	$('#repeat').prop('checked', event.repeat);

	if (event.repeat) {
		$('#repeat_id').val(event.rule.id);
		$('#repeat_uri').val(event.rule.resource_uri);
		$('input[name="freq"]').each( function() {
			$(this).prop('checked', (event.rule.freq==$(this).val()));
		});
		$('input[name="byweekday"]').each( function() {
			$(this).prop('checked', (event.rule.byweekday.indexOf($(this).val()) > -1) );
		});

		if (event.rule.until === null) {
			$("#stop_count").prop('checked', true);
			$('#count').val(event.rule.count);
		} else {
			$("#stop_until").prop('checked', true);
			$('#until').val(moment(event.rule.until).format('MM/DD/YYYY'));
		}
	}
	set_all_day($('#all_day').is(':checked'));
	set_repeat($('#repeat').is(':checked'));
	set_repeat_stop_type($("input[name='stopRepeatType']:checked").val());
};

var reset_form = function() {
	$('form').each(function() {
		$(this)[0].reset();
	});
	save_start_time = null;
	save_end_time = null;
};

var dehydrate_event_time = function(start_end, m) {
	$('#'+start_end+'_date').val(m ? m.format('MM/DD/YYYY') : "");
	$('#'+start_end+'_time').val(m ? m.format('h:mm A') : "");
}

var update_duration_text = function(duration_text) {

	var s = '';
	if (duration_text !== undefined ) {
		s = duration_text;
	} else if ($('#all_day').is(':checked')) {
		s = '';
	} else {
		s = humanize_duration(current.duration);
		if (s != '') {
			s = 'Duration: ' + s;
		} else {
			s = 'No time at all';
		}
	}
	$('#duration-label').html(s);
}

var humanize_duration = function(d) {
	var s = '';
	if (d.days() > 0) { s += ( (s != '') ? ', ' : '' ) + d.days() + ' Day(s)'; }
	if (d.hours() > 0) {  s += ( (s != '') ? ', ' : '' ) + d.hours() + ' Hour(s)'; }
	if (d.minutes() > 0) { s += ( (s != '') ? ', ' : '' ) + d.minutes() + ' Minute(s)'; }
	return s;
}



// ---- API FUNCTIONS ----------------------------------------------------------
var call_api = function(url, data, method) {
	var c_obj = {
		url: url,
		type: method,
		contentType: 'application/json',
		dataType: 'text',
		processData: false
	}
	if (data !== '') {
		c_obj.data = data;
	}
	$.ajax( c_obj
	).done(function() { 
		calendar.fullCalendar('refetchEvents');
	}).fail(function(xhr, textStatus, errorThrown) { 
		console.log(jQuery.parseJSON( xhr.responseText ));
		alert('Error in saving event');
	}).always(function() { 
		// Do something always
	});
}

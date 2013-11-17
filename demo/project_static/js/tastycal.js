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

	// ---- BUTTONS ------------------------------------------------------------
	$('#save').on('click', function(e) {
		var is_new = ( $('#event_id').val() == '' && $('#repeat_id').val() == '')
		var is_repeat = ($('#repeat').is(':checked'));

		var url, data, data_obj, method;

		if (is_repeat) {
			url = calendar_data.repeats_uri;
			data_obj = prep_repeat_data();
		} else {
			url = calendar_data.events_uri;
			data_obj = prep_event_data();
		}

		if (is_new) {
			method = 'POST';
		} else {
			method = 'PUT';
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
var save_start_time, save_end_time;
var set_all_day = function(all_day) {
	if (all_day) {
		save_start_time = $('#start_time').val();
		save_end_time = $('#end_time').val();
		$('#start_time').val('').prop('disabled', true);
		$('#end_time').val('').prop('disabled', true);			
	} else {
		$('#start_time').prop('disabled', false);
		$('#end_time').prop('disabled', false);			
		if (save_start_time !== null) {
			$('#start_time').val(save_start_time);
		}
		if (save_end_time !== null) {
			$('#end_time').val(save_end_time);
		}
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
		repeat: $('input[name="repeat"]').is(':checked'),
	};
	if (!isNaN($('#event_id').val())) {
		id: parseInt($('#event_id').val());
	}
	return data;
}

var prep_repeat_data = function() {
	// repeat data has at least all the fields of an event, so start with that
	// but remove the id, if it exists
	data = prep_event_data();
	delete data.id;

	var byweekday = []
	$('input[name="byweekday"]:checked').each(function() {
		byweekday.push( this.id );
	})

	data.freq = parseInt($('input[name="freq"]:checked').val());
	data.byweekday = byweekday

	stoptype = $("input[name='stopRepeatType']:checked").val()
	if (stoptype=="until") {
		data.until = new Date($('#until').val());
	} else {
		data.count = parseInt($('#count').val());
	}

	if (!isNaN($('#repeat_id').val())) {
		id:  parseInt($('#repeat_id').val());
	}
	return data;
};

var prep_form = function(event, repeat) {
	// default value for repeat is false
	repeat = typeof repeat !== 'undefined' ? repeat : false;

	$('#event_id').val(event.event_id);
	$('#event_uri').val(event.resource_uri);
	$('#title').val(event.title);
	$('#start_date').val(moment(event.start).format('MM/DD/YYYY'));
	$('#end_date').val(event.end ? moment(event.end).format('MM/DD/YYYY') : "");
	if (!event.allDay) {
		$('#start_time').timepicker('setTime', moment(event.start).format('h:mm A').toString() );
		$('#end_time').val(event.end ? moment(event.end).format('h:mm A') : "" );
	}
	$('#all_day').prop('checked', event.all_day);
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
	console.log(c_obj);
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

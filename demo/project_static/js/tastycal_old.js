/*
Create new, non-repeating event
	1. POST to Event resource
	2. GET event list from Event resource
Create new, repeating event
	1. POST to RRule resource
	2. GET event list from Event resource
Edit existing, non-repeating event
	1. Open modal dialog
	2. PUT to Event resource
Edit existing, repeating event
	1. Query whether user wants to open instance or rule
	if instance:
		2a. PUT to Event resource
	if rrule:
		2a. PUT to RRule resource
	3. GET event list from Event resource
Delete non-repeating event
	1. DELETE to Event resource
	2. GET event list from Event resource
Delete repeating event
	1. DELETE to RRile resource
	2. GET event list from Event resource
*/

/* TODO:
1. "Starts on" field for repeat modal
2. Repeat on, Starts on field determined by the date of the event already in progress
3. Radio select the type of end (after # occurrences or on specific date)
4. Summary field
*/

$(document).ready(function() {
		//--- MODAL  -----------------------------------------------------------
		$('#event_modal').modal({ 
			show: false,
			keyboard: true,
		});


		//--- MODAL REPEAT SECTION  ------------------------------------------------
		$('#event_repeat').on('change', function() {
			set_repeat_section_visibility();
		})



		//----------------------------------------------------------------------
		//--- EVENT SAVE BUTTON  -----------------------------------------------
		$('#event_modal_save').on('click', function(e){
			var byweekday = []
			$('#byweekday-group .btn.active').each(function() {
				byweekday.push( eval(this.id) );
			})

			// The various jquery serializeObject techniques for forms don't 
			// grab the data from the bootstrap button groups, so we do it
			// this way
			data_obj = {
				title: $('#event_title').val(),
				start: new Date($('#event_start').val()),
				end: new Date($('#event_end').val()),
				repeating: $('#event_repeat').is(':checked'),
				calendar: calendar_current.resource_uri,
				freq: freqs.indexOf($('#freq-group .btn.active').attr('id')),
			    until: new Date($('#event_until').val()),
			    count: parseInt($('#event_count').val()),
			    byweekday: byweekday,
			}
			data = JSON.stringify(data_obj);

			if ($('#event_id').val() == "") {
				// new event
				url = calendar_current.events_uri;
				type = "POST";
			} else {
				// update existing
				url = $('#event_uri').val();
				type = "PATCH";
			}
			
			console.log(data_obj);
			$.ajax({
				url: url,
				type: type,
				contentType: 'application/json',
				data: data,
				dataType: 'text',
				processData: false,

			}).done(function() { 
		    	calendar.fullCalendar('refetchEvents');
			}).fail(function(xhr, textStatus, errorThrown) { 
				console.log(jQuery.parseJSON( xhr.responseText ));
				alert('Error in saving event');
		    }).always(function() { 
		    	// Do something always
		    });

		    $('#event_modal').modal('hide')

		});

		//----------------------------------------------------------------------
		//--- REPEAT CHECKBOX --------------------------------------------------
		$('#event_repeat').on('change', function() {
			// If repeat is clicked and this event does not already have a rule 
			// associated with it, open the repeat form
			var existing_rule = $('#rule_id').val() != ""
			var repeating = $('#event_repeat').is(':checked')
			if (repeating && !existing_rule) {
				$('#event_modal').modal('hide');
				$('#repeat_modal').modal('show');

			// If repeat is clicked and there is already a rule associated with
			// the event, re-show the edit link
			} else if (repeating && existing_rule) {

			}
		});

		//----------------------------------------------------------------------
		//--- MODAL REPEAT CANCEL  ---------------------------------------------
		$('#repeat_modal_cancel').on('click', function() {
			$('#repeat_modal').modal('hide');
			$('#event_modal').modal('show');
			$('#updated_rule').val("");
			// If the user is cancelling and there was no previous repeat rule
			// saved, make sure that the repeat checkbox is off
			if ($('#rule_id').val() == "") {
				$('#event_repeat').prop('checked', false);
			}
		});


		//----------------------------------------------------------------------
		//--- MODAL REPEAT SAVE BUTTON  ----------------------------------------
		$('#repeat_modal_save').on('click', function(e) {
			$('#repeat_modal').modal('hide');
			$('#event_modal').modal('show');
			// $('#updated_rule').val("XXX");
		});
			


		//----------------------------------------------------------------------
		//--- MODAL DELETE BUTTON  ---------------------------------------------
		$('#event_modal_delete').on('click', function(e) {
			$.ajax({
				url: $('#event_uri').val(),
				type: 'DELETE',
				contentType: 'application/json',
				dataType: 'text',
				processData: true

			}).done(function() { 
		    	calendar.fullCalendar('refetchEvents');
			}).fail(function(xhr, textStatus, errorThrown) { 
		    	alert("There was a problem on the server...wonder what it was...");
		    	console.log(xhr);
		    }).always(function() { 
		    	// Do something always
		    });
	    	$('#event_modal').modal('hide')
		    calendar.fullCalendar('refetchEvents');
		})

		//--- DATE/TIME PICKER ------------------------------------
		$('#event_start, #event_end, #event_until').datetimepicker({
	      timeFormat: 'hh:mm tt',
	      stepMinute: 15,
	    });



	    function set_up_forms(event) {

		$('#event_tite').val(event.title);
		$('#event_start').val( moment(event.start).format('MM/DD/YYYY h:mm a') );
		$('#event_end').val( event.end ? moment(event.end).format('MM/DD/YYYY h:mm a') : "" );
		$('#event_id').val(event.id);
		$('#event_uri').val(event.resource_uri);
		$('#event_modal_delete').removeClass("hide") 
		$('#event_repeat').prop('checked', event.rule != null); 
		$('#updated_rule').val("");
		if (event.rule != null) {
			$('#edit_repeat').removeClass('hide');
			$('#' + freqs[event.rule.freq]).addClass('active');
			// $.each('#byweekday-group .btn')
		} else {
			$('#edit_repeat').addClass('hide');
		}


	}

}); // document ready
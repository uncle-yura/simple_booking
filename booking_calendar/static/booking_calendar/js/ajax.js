'use strict';

function getMasterData(event){
    $('#id_calendar_loading').show();
    $.ajax({
        data: event.serialize(), 
        url: getLocalText('gcal_url'),
    
        success: function (response) {
            $('#id_calendar_loading').hide();

            if( response.msg ) update_messages({'tag':'alert-danger','text':response.msg});
            
            if( !response.success ) return;

            for(let price in response.prices){
                $('#id_work_type').append($("<option></option>")
                    .attr("value",response.prices[price].id)
                    .attr("price",response.prices[price].price)
                    .attr("time",response.prices[price].time)
                    .text(response.prices[price].name + ' - ' + response.prices[price].str_time + ' - ' + response.prices[price].price));
            }
    
            let eventsList = [];

            let startDate = new Date();
            startDate.setHours(0,0,0,0);
            let delayDate = new Date(parseInt(response.delay));

            eventsList.push({
                'start': startDate.toISOString(),
                'end': delayDate.toISOString(),
                });

            for(let event in response.events){
                let eventElement = response.events[event];

                eventsList.push({
                    'start': eventElement.start['dateTime' in eventElement.start ? 'dateTime' : 'date'],
                    'end': eventElement.end['dateTime' in eventElement.end ? 'dateTime' : 'date'],
                    });
                }

            sessionStorage.setItem('events', JSON.stringify(eventsList));

            drawCalendar(+response.range);
            drawTimetable(new Date());
        },
    
        error: function (response) {
            update_messages({'tag':'alert-danger','text':getLocalText('responseError')})
        }
    });
}

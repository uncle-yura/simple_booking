'use strict';

function getMasterData(event){
    $.ajax({
        data: event.serialize(), 
        url: gcal_url,
    
        success: function (response) {
            $('#id_work_type').empty();
            for(let price in response.prices){
                $('#id_work_type').append($("<option></option>")
                    .attr("value",response.prices[price].id)
                    .attr("price",response.prices[price].price)
                    .attr("time",response.prices[price].time)
                    .text(response.prices[price].name + ' - ' + response.prices[price].str_time + ' - ' + response.prices[price].price));
            }
    
            eventsList = [];
            for(let event in response.events){
                let eventElement = response.events[event];
                eventsList.push({
                    'start': Date.parse(eventElement.start['dateTime' in eventElement.start ? 'dateTime' : 'date']),
                    'end': Date.parse(eventElement.end['dateTime' in eventElement.end ? 'dateTime' : 'date']),
                    });
            }
    
            drawCalendar(+response.range);
            drawTimetable(new Date());
        },
    
        error: function (response) {
            console.log(response.responseJSON.errors);
        }
    });
}


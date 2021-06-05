'use strict';

class Event {
    constructor(event, id='') {
        this.event = new Object;
        Object.assign(this.event, event);

        this._pos_start = getPosFromStamp(this.event.start);
        this.pos_end = getPosFromStamp(this.event.end);
        this.duration = this.event.end - this.event.start;

        this.card = document.createElement('div');
        this.card.className = "timetable_event";
        this.card.id = id;

        this._dragging = false;

        if(!id) {
            this.card.onclick =  this.click_callback.bind(this);
        }
        else {
            this.card.onmousedown = this.mouse_down.bind(this);
            this.card.onmouseup = this.mouse_up.bind(this);
        }

        this.update_position();
        this.update_text();
    }

    mouse_down() {
        this.dragging = true;
    }

    mouse_up() {
        this.dragging = false;
        moveTimetable(this._pos_start - 1/6);
    }

    update_text() {
        this.card.innerHTML = getLocalText('busyFromTo', getLocaleTimeString(this.event.start), getLocaleTimeString(this.event.end));
    }

    update_position() {
        this.card.style = "height: " + (this.pos_end - this._pos_start)*100 + "%; top: " + this._pos_start*100 + "%";

        if(this.card.id && !this.dragging) {
            moveTimetable(this._pos_start - 1/6);
        }
    }

    check_new_position(position_start) {
        if( position_start >= 1 || position_start<0 ) return false;

        let pos_duration = this.pos_end - this._pos_start;
        let position_end = pos_duration + position_start;
    
        for(let i=0; i<selectedDayEventsObjList.length; i++) {
            let event = selectedDayEventsObjList[i].event;
            let start = getPosFromStamp(event.start);
            let end = getPosFromStamp(event.end);
    
            if( checkPosition(position_start, position_end, event) ) {
                continue;
            } 
            else {
                let dif_next;
                let dif_prev;
                if(end+pos_duration<1) {
                    if((i==selectedDayEventsObjList.length-1) || (i<selectedDayEventsObjList.length-1) && 
                            checkPosition(end, end+pos_duration, selectedDayEventsObjList[i+1].event)) {
                        dif_next = end - position_start;
                    }
                }
                
                if(start - pos_duration>=0){
                    if(i==0 || (i>0 && checkPosition(start - pos_duration, start, selectedDayEventsObjList[i-1].event))) {
                        dif_prev = (start - pos_duration) - position_start;
                    } 
                }
      
                if((dif_next && dif_prev == undefined) || (dif_next && dif_prev && (dif_next < Math.abs(dif_prev)))) {
                    position_start += dif_next;
                }
                else if((dif_next == undefined && dif_prev) || (dif_next && dif_prev && (dif_next > Math.abs(dif_prev)))) {
                    position_start += dif_prev;
                }
                else {
                    return false;
                }
                
            }
        }
        return position_start;
    }

    get dragging() {
        return this._dragging;
    }

    set dragging(value) {
        this._dragging = value;
        if(!value) {
            $(this.card).removeClass('draggable');
        } else {
            $(this.card).addClass('draggable');
        }
    }

    get pos_start() {
        return this._pos_start;
    }

    set pos_start(value) {
        if((value=this.check_new_position(value)) === false) {
            return;
        }

        this._pos_start = value;
        this.pos_end = value + this.duration/86400000;
        this.event.start = getStampFromPos(this._pos_start,this.event.start);
        this.event.end = this.event.start+this.duration;

        this.update_position();    
        this.update_text();
    }

    click_callback() {
        drawNewEvent(this.pos_end);
    }
}

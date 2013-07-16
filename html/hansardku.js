jQuery(document).ready(function($) {
    var manager;

    $(window).load(function() {
        $('body').scrollTop(1);
        console.log('scrollTop');
    });

    var HaikuManager = function() {
        this.init();
    };
    $.extend(HaikuManager.prototype, {
        init: function() {
            var self = this;
            this.base = '/api/0.1/';
            $("#btn-another").click(function() {
                self.next();
            });
            $("#btn-another-stuck").click(function() {
                self.next_mp();
            });
            $("#btn-tweet").click(function() {
                self.tweet();
            });
        }, 
        _set: function(data) {
            this.data = data;
            window.location.hash = data['hash'];
            $(".haiku-name").text(data['talker']);
            $(".haiku-date").text(data['date']);
            $(".poem-body").empty();
            $.each(data['text'], function(idx, line) {
                var div = $("<div/>");
                div.text(line.replace(" ", "&nbsp;"));
                $(".poem-body").append(div);
            });
        },
        _trail_get: function(trail_name, last) {
            var self = this;
            var uri = '/api/0.1/haiku/' + trail_name;
            if (last) {
                uri += '/' + last;
            }
            $.getJSON(uri, function(data) {
                self._set(data);                
            });
        },
        next: function() {
            this._trail_get('all', this.data['poem_index']);
        },
        next_mp: function() {
            this._trail_get('talker=' + this.data['talker_id'], this.data['talker_index']);
        },
        tweet: function() {
            // fixme!!
        }
    });

    manager = new HaikuManager();
    manager.next();
});

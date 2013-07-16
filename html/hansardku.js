jQuery(document).ready(function($) {
    var manager;

    $(window).load(function() {
        $('body').scrollTop(1);
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
            window.location.hash = '/' + data['hash'];
            $(".haiku-name").text(data['talker']);
            $(".haiku-date").text(data['date']);
            // fill in the poem
            $(".poem-lines").empty();
            $("#btn-another-stuck").text("Another from " + data['talker']);

            $.each(data['text'], function(idx, line) {
                var div = $("<div/>");
                div.text(line);
                div.html(div.html().replace(' ', '&nbsp;'));
                $(".poem-lines").append(div);
            });
        },
        _trail_get: function(trail_name, last) {
            var self = this;
            var uri = '/api/0.1/haiku/issue/' + trail_name;
            if (last) {
                uri += '/' + last;
            }
            $.getJSON(uri, function(data) {
                self._set(data);                
            });
        },
        load: function(uid) {
            var self = this;
            var uri = '/api/0.1/haiku/byuid/' + uid;
            $.getJSON(uri, function(data) {
                self._set(data);                
            });
        },
        next: function() {
            var last;
            if (this.data) {
                last = this.data['poem_index'];
            }
            this._trail_get('all', last);
        },
        next_mp: function() {
            if (!this.data) {
                return;
            }
            this._trail_get('talker=' + this.data['talker_id'], this.data['talker_index']);
        },
        tweet: function() {
            // fixme!!
        }
    });

    manager = new HaikuManager();

    // restore last haiku
    var m = window.location.hash.match(/^#\/([A-Za-z0-9]+)$/);
    console.log(window.location.hash);
    if (m) {
        manager.load(m[1]);
    } else {
        manager.next();
    }
});

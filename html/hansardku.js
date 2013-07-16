jQuery(document).ready(function($) {
    /*
     * jQuery hashchange event - v1.3 - 7/21/2010
     * http://benalman.com/projects/jquery-hashchange-plugin/
     * 
     * Copyright (c) 2010 "Cowboy" Ben Alman
     * Dual licensed under the MIT and GPL licenses.
     * http://benalman.com/about/license/
     */
    (function($,e,b){var c="hashchange",h=document,f,g=$.event.special,i=h.documentMode,d="on"+c in e&&(i===b||i>7);function a(j){j=j||location.href;return"#"+j.replace(/^[^#]*#?(.*)$/,"$1")}$.fn[c]=function(j){return j?this.bind(c,j):this.trigger(c)};$.fn[c].delay=50;g[c]=$.extend(g[c],{setup:function(){if(d){return false}$(f.start)},teardown:function(){if(d){return false}$(f.stop)}});f=(function(){var j={},p,m=a(),k=function(q){return q},l=k,o=k;j.start=function(){p||n()};j.stop=function(){p&&clearTimeout(p);p=b};function n(){var r=a(),q=o(m);if(r!==m){l(m=r,q);$(e).trigger(c)}else{if(q!==m){location.href=location.href.replace(/#.*/,"")+q}}p=setTimeout(n,$.fn[c].delay)}/MSIE/.test(navigator.userAgent)&&!d&&(function(){var q,r;j.start=function(){if(!q){r=$.fn[c].src;r=r&&r+a();q=$('<iframe tabindex="-1" title="empty"/>').hide().one("load",function(){r||l(a());n()}).attr("src",r||"javascript:0").insertAfter("body")[0].contentWindow;h.onpropertychange=function(){try{if(event.propertyName==="title"){q.document.title=h.title}}catch(s){}}}};j.stop=k;o=function(){return a(q.location.href)};l=function(v,s){var u=q.document,t=$.fn[c].domain;if(v!==s){u.title=h.title;u.open();t&&u.write('<script>document.domain="'+t+'"<\/script>');u.close();q.location.hash=v}}})();return j})()})(jQuery,this);
    /* end paste */

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
            $("#btn-another").click(function(ev) {
                ev.preventDefault();
                self.next();
            });
            $("#btn-another-stuck").click(function(ev) {
                ev.preventDefault();
                self.next_mp();
            });
            $("#btn-tweet").click(function(ev) {
                ev.preventDefault();
                self.tweet();
            });
            $("#haiku-search").submit(function(ev) {
                ev.preventDefault();
                console.log($("#haiku-search-text").val());
                $('body').scrollTop(1);
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
        },
        from_hash: function() {
            var m = window.location.hash.match(/^#\/([A-Za-z0-9]+)$/);
            if (m) {
                manager.load(m[1]);
            } else {
                manager.next();
            }
        }
    });

    manager = new HaikuManager();
    manager.from_hash();
    $(window).hashchange( function(){
        manager.from_hash();
    });
});

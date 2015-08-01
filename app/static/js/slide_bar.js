/**
 * Created by assassinpig on 2015/4/1.
 */

var slider = function(elem, args) {
    //console.log('constructor');
    this.config = $.extend({
        "effect"    : 'x',          //effect: x-horizontal | y-vertical | fade-fade | none-hidden
        "speed"     : 600,          //动画速度
        "interval"  : 1000,         //播放时间间隔
        "auto"      : true,         //是否自动播放
        "trigger"   : "mouseenter", //触发事件
        "content_box"   : ".photo_ul",       //容器id
        "content_tag"   : '.photo_ul li',    //内容标签
        "switcher_box"  : ".number_ul",      //
        "switcher_tag"  : ".number_ul li",   //
        "active_class"  : 'active',          //
        "prev"          : ".prev",           //
        "next"          : ".next",           //
        "rand"          : false,             //是否随机指定默认开始页面
        "callback"      : null               //是否有callback函数
    }, args ||  {});

    this.elem = elem;
    this.init();
}

slider.prototype.init = function() {
    //console.log('init');
    var opts = this.config;
    var elem = this.elem
    this.index = 0;
    this.last_index = 0;
    this.content_box = elem.find(opts.content_box);
    this.content_tag = elem.find(opts.content_tag);
    this.switcher_box = elem.find(opts.switcher_box);
    this.switcher_tag = elem.find(opts.switcher_tag);
    this.prev = elem.find(opts.prev);
    this.next = elem.find(opts.next);

    var self = this;
    this.timer = setInterval(function (){ self.show_next(); }, opts.interval);
    
    var length = self.content_tag.length;
    this.prev.click(function(){
        self.pause();
        self.show((self.index -1 + length) % length);
        self._continue();
    });

    this.next.click(function(){
        self.pause();
        self.show((self.index + 1 + length) % length);
        self._continue();
    });

    this.switcher_tag.click(function(e){
        self.pause();
        var to = $(this).html() - 1;
        self.show(to);
        self._continue();
    });

    if(opts.effect == 'fade') {
        $.each(this.content_tag, function(k, v) {
                (k === 0) ? $(this).css({
                    'position': 'absolute',
                    'z-index': 9
                }) : $(this).css({
                    'position': 'absolute',
                    'z-index': 1,
                    'opacity': 0
                });
            });
    }
}

slider.prototype.show_next = function() {
    var length = this.content_tag.length;
    this.show((this.index + 1 + length) % length);
}

slider.prototype.show = function(to) {
    //console.log('show');
    var length = this.content_tag.length;
    var real_to = to%length;
    var operation = '';
    var delta = to - this.index;
    
    var delta_operation;
    var opts = this.config;

    switch(opts.effect) {
        case 'x': {
            delta_operation = this.content_tag.width();
        }
        break;

        case 'y': {
            delta_operation = this.content_tag.height();
        }
        break;

        case 'fade': {

        }
        break;
    }

    //console.log(delta_operation);

    if( delta < 0) {
        operation = '+='+ ( -delta * delta_operation) + 'px';
    }
    if (delta > 0) {
        operation = '-='+ ( delta * delta_operation) + 'px';
    }
    
    //console.log(operation);
    this.index = real_to;
    //console.log(this.index);    
    switch(opts.effect) {
        case 'x': {
            this.content_box.stop().animate( {
                    left: operation
                },
                500
            );
        }
        break;

        case 'y': {
            this.content_box.stop().animate( {
                    top: operation
                },
                500
            );
        }
        break;

        case 'fade': {
            this.content_tag.eq(this.last_index).stop().animate({
                'opacity': 0
            }, opts.speed / 2).css('z-index', 1).end()
                .eq(this.index).css('z-index', 9).stop().animate({
                'opacity': 1
            }, opts.speed / 2);
        }
        break;
    }
    
    this.last_index = this.index;
    
    if(this.switcher_tag) {
        this.switcher_tag.siblings().removeClass('number_bar_active').addClass('number_bar_unactive');
        this.switcher_tag.siblings('li:nth-child('+(this.index+1)+')').removeClass('number_bar_unactive').addClass('number_bar_active');    
    }
}

slider.prototype.pause = function (){
    clearInterval(this.timer);
}

slider.prototype._continue = function (){
    var opts = this.config;
    var self = this;
    if (opts.auto) {
        this.timer = setInterval(function (){ self.show_next(); }, opts.interval);
    }
}

$.fn.slider = function(args) {
    return this.each(function() {
        var $el = $(this);
        var plugins = new slider($el, args);
        $el.data("slider", plugins);
    });
}

!function($) {
    $(document).ready(function(){
        
        $(".photo_bar").slider({
            "content_box"   : ".photo_ul",       
            "content_tag"   : '.photo_ul li',    
            "switcher_box"  : ".number_ul",      
            "switcher_tag"  : ".number_ul li",              
            "effect":'x',
            "rand":true
        });    

        $(".photo_bar_y").slider({
            "content_box"   : ".photo_ul_y",       
            "content_tag"   : '.photo_ul_y li',    
            "switcher_box"  : ".number_ul",      
            "switcher_tag"  : ".number_ul li",              
            "effect":'y',
            "rand":true
        });    

        $(".photo_bar_fade").slider({
            "content_box"   : ".photo_ul_fade",       
            "content_tag"   : '.photo_ul_fade li',    
            "switcher_box"  : ".number_ul",      
            "switcher_tag"  : ".number_ul li",              
            "effect":'fade',
            "rand":true
        });    
        
    });
}(jQuery);
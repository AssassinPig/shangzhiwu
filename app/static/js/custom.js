!function($){

    $(document).ready(function(){
        //console.log('ready');

        var menu_status = false;        //0-fold 1-unfold
        var main_menu = $('.main_menu');
        var main_list = $('.menu_list');
        var main_barrier = $('.menu_barrier');

        var menu_click_fun = function() {
            if(menu_status == false){
                main_list.addClass('display');
                main_list.removeClass('hidden');

                main_menu.addClass('main_menu_ative');
                main_barrier.css('background-color', '#F0F0F0');

            } else {
                main_list.addClass('hidden');
                main_list.removeClass('display');

                main_menu.removeClass('main_menu_ative');
                main_barrier.css('background-color', '#90415E');
            }
            menu_status = !menu_status;
        }

        main_list.addClass('hidden');
        main_menu.click(function() {
            menu_click_fun();
        });

    });


}(jQuery);

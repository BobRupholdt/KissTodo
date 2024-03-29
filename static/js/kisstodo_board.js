var kisstodo_board = (function () {
    var res = {};
    
    res.init_board=function() {
        
        $(document).ajaxStart(function() { 
            kisstodo_board.ajax_pending = true; 
            kisstodo_board.lockGui(); 
        }).ajaxStop(function() { 
            kisstodo_board.unlockGui(); 
            kisstodo_board.ajax_pending = false; 
        });        
        
        $(document).ajaxError(function(e, xhr, settings, exception) {
         
          if (settings.url.indexOf("/static/js/ping.js")==0) return;
          
  

          if (xhr.status!="0")
          {
                kisstodo_board.show_message("Network error.");
          }
          else
          {

            kisstodo_board.check_network();
            if(kisstodo_board.is_network_available()) {
                // not logget on GAE
                window.location.replace(kisstodo_board.urls['login']);
                
               
            } else {
                kisstodo_board.show_message("Network error.");
            }
            
            
          }
          
          //kisstodo_board.check_network();
        });

        /*
        $.ajaxPrefilter(function( options, originalOptions, jqXHR ) {
          if ( !kisstodo_board.is_currently_online() ) {
              jqXHR.abort();
              console.log("request "+options.url+" aborted");
          }
        }); */
        
        //$(document).ajaxComplete(function(e, xhr, settings) {
        //console.log("AC status:"+xhr.status);
        //console.log("AC location:"+xhr.location);
        //console.log("AC header"+xhr.getResponseHeader('Location'));
        //if (xhr.status == 302) {
        //    window.location.href = xhr.getResponseHeader("Location").replace(/\?.*$/, "?next="+window.location.pathname);
        //}
        //});
        
        // redirect ajax requests that are redirected, not found (404), or forbidden (403.)
        //$('body').bind('ajaxComplete', function(event,request,settings){
                //console.log("AJAX COMPLETE: "+request.status);
                //console.log("HTTP DATA: "+request.responseText);
                
                //if (request.responseText.indexOf('<html>')==0) window.location.replace(kisstodo_board.urls['login']);
                
                /*
                switch(request.status) {
                    case 301: case 404: case 403:                    
                        
                        break;
                }
                */
        //});
        
        $(document).bind('keypress', kisstodo_board.event_keypress);
        $(document).bind('keydown', kisstodo_board.event_keydown);
        
        //$('#sort_mode').change(function() {kisstodo_board.refresh_selected_todo_list();});
        
        $('#sort_mode_P,#sort_mode_D,#sort_mode_A').live('click', function() {
            $('.sort_mode').removeClass('selected_link');
            $('.sort_mode').removeClass('ui-btn-active'); // jquery mobile
            $(this).addClass('selected_link');
            $(this).addClass('ui-btn-active');
            kisstodo_board.sort_mode=$(this).attr('id').replace('sort_mode_',''); 
            kisstodo_board.refresh_selected_todo_list();
        });
        
        $('.complete_button').live('click', function() {
           var x = $(this).parents('li').find(".todo_complete");
           x.click();
           return false;
        });    

        $('.edit_button').live('click', function() {
           $(this).parents('li').find(".todo_description").click(); 
           return false;
        });            
        
         $('.network_switch').live('click', function() {      
            kisstodo_board.set_currently_online(!kisstodo_board.is_currently_online(), true);
        });
        
        $('#show_complete_T,#show_complete_F').live('click', function() {
            $('.show_complete').removeClass('selected_link');
            $('.show_complete').removeClass('ui-btn-active'); // jquery mobile
            $(this).addClass('selected_link');
            $(this).addClass('ui-btn-active');
            kisstodo_board.show_complete=$(this).attr('id').replace('show_complete_','');
            kisstodo_board.refresh_selected_todo_list();
        });        
        
        $('input[type=text]').live('focus', function () {           
            kisstodo_board.focused_element = $(this).attr('id');
            if (kisstodo_board.focused_element.indexOf('edit_todo_')!=0) kisstodo_board.select_next_todo(0);
        });
        
        $('input[type=text]').live('blur', function () {           
            kisstodo_board.focused_element = '';
        });
        
        $(kisstodo_board.selector_prefix+'#selected_list_option').live('change', function () { 
            var list_id=$(this).val();
            
            kisstodo_board.refresh_todo_list(list_id);
            
            kisstodo_board.update_list_edit_tools();
        });        
        
        $('.todo_description').live('click', function () { 
            if (kisstodo_board.is_edit_active()) return;
            
            //todo_id=($(this).parents('li').attr('id').replace('todo_li_',''));
            $('.todos li.todo_li').removeClass("selected_todo");
            $($(this).parents('li')).addClass("selected_todo");
            kisstodo_board.edit_selected_todo();
        });        
    
        $('.list_delete').live('click', function () { 
            var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
            
            var data = {
                list_id: list_id,
                csrfmiddlewaretoken : kisstodo_board.csrftoken
            };
       
            $.post(kisstodo_board.urls['list_delete'], data, function (response) {
                    kisstodo_board.refresh_list_list(kisstodo_board.inbox_list_id);
                    kisstodo_board.show_message("List deleted.");
            });        
    		
            
            return false;
        });   
        
        $('#empty_trash').live('click', function () { 
            var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
            
            var data = {csrfmiddlewaretoken : kisstodo_board.csrftoken};
       
            $.post(kisstodo_board.urls['todo_empty_trash'], data, function (response) {
                    kisstodo_board.refresh_list_list(kisstodo_board.inbox_list_id);
            });        
    		
            return false;
        });   
        
        $('#clear_completed_items').live('click', function () { 
            var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
            
            var data = {csrfmiddlewaretoken : kisstodo_board.csrftoken};
       
            $.post(kisstodo_board.urls['todo_clear_completed_items']+list_id, data, function (response) {
                    //console.log("LIST_ID2:"+list_id);
                    kisstodo_board.refresh_list_list(list_id);
            });        
    		
            return false;
        });           
        
        /*
        $('body').bind( 'taphold', function( e, ui ) {
            alert( 'You tapped and held!'+$(this).attr('id'));
            //e.stopImmediatePropagation();
            //return false;
          });  
          
        
        $('.todo_li').live('tap', function() {
            console.log($(this).attr('id'));
        }
        
        );*/
        
        $('.list_item').live('hover', function () { 
        
            var config = {    
                 over: function()  
                 {  
                    var list_id=$(this).attr('id').replace('list_item_','');
                    $('#list_edit_delete_'+list_id).toggle(0);
                 }, // function = onMouseOver callback (REQUIRED)    
                 interval: 300, // number = milliseconds delay before onMouseOut    
                 out: function() 
                 {
                    var list_id=$(this).attr('id').replace('list_item_','');
                    $('#list_edit_delete_'+list_id).toggle(0);
                 }
            };
            
            if (!$(this).data('init')) {
                $(this).data('init', true);  
                $(this).hoverIntent(config);  
                $(this).trigger('mouseover');  
            }
        });
        
        $('.todo_item').live('hover', function () { 
        
            var config = {    
                 over: function()  
                 {  
                    $(this).find(".image_delete").fadeIn();
                 }, // function = onMouseOver callback (REQUIRED)    
                 interval: 150, // number = milliseconds delay before onMouseOut    
                 out: function() 
                 {
                    $(this).find(".image_delete").fadeOut();
                 }
            };
            
            if (!$(this).data('init')) {
                $(this).data('init', true);  
                $(this).hoverIntent(config);  
                $(this).trigger('mouseover');  
            }
        });        

        $('.list_edit').live('click', function () { 
            var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
            
            var d = $(".list_list");
            d.fadeOut(kisstodo_board.default_animation_speed);
            
            var d2=$('#list_edit_container');
            d2.load(kisstodo_board.urls['list_edit']+list_id, function () {
                d2.fadeIn(kisstodo_board.default_animation_speed);
                $('#edit_list_name').focus();
            });
            
            return false;
        });    
        
        $('.todo_delete').live('click', function () { 
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            
            var todo_id=$(this).attr("id").replace("todo_delete_","");
            var todo=$(this).parents("li");
            
            var data = {
                todo_id: todo_id,
                csrfmiddlewaretoken : kisstodo_board.csrftoken
            };
            
            $.post(kisstodo_board.urls['todo_delete'], data, function (response) {
                todo.remove();
            });        
    		
            return false;
        });   

        $('.todo_undelete').live('click', function () { 
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            
            var todo_id=$(this).attr("id").replace("todo_undelete_","");
            var todo=$(this).parents("li");
            
            var data = {
                todo_id: todo_id,
                csrfmiddlewaretoken : kisstodo_board.csrftoken
            };
            
            $.post(kisstodo_board.urls['todo_undelete'], data, function (response) {
                todo.remove();
            });        
    		
            return false;
        });           

        $('.todo_complete').live('click', function () { 
            
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return false;}
            
        
            var todo_id=$(this).attr("id").replace("todo_complete_","");
            var todo=$(this).parents("li");
            
            var data = {
                todo_id: todo_id,
                csrfmiddlewaretoken : kisstodo_board.csrftoken
            };
            
            $.post(kisstodo_board.urls['todo_complete'], data, function (response) {
                //var d = $(".selected_todo .todo_item");
                var d=$('#todo_complete_'+todo_id+' .todo_item');
                d.fadeOut(kisstodo_board.default_animation_speed);
                d.load(kisstodo_board.urls['todo_show_item']+todo_id, function () {d.fadeIn(kisstodo_board.default_animation_speed);});      
                todo.toggleClass("complete");
            });        
    		
            return true;
        });   
        
        /*$(".help_toggle, #help").click(function(){$('#help').toggle(0);});*/
        
        /*$("#list_list").touchwipe({
             wipeLeft: function() { kisstodo_board.select_next_list(1); },
             wipeRight: function() { kisstodo_board.select_next_list(-1); },
             wipeUp: function() { },
             wipeDown: function() { },
             min_move_x: 20,
             min_move_y: 5000,
             preventDefaultEvents: true
        });*/
        
        if (kisstodo_board.mobile) {
            $(".main_page").live('swipeleft swiperight', function(event) {
                 if (event.type == "swiperight") {
                    kisstodo_board.select_next_list(-1); 
                 }
                 else {
                    kisstodo_board.select_next_list(1); 
                 }
                 event.preventDefault();
            });
            
            //$('#main_page').live('pageinit',function(event){
            //  console.log("PAGEINIT BEGIN");
            //  kisstodo_board.init_board_lists();
            //  console.log("PAGEINIT END");
            //});
        }
        
        kisstodo_board.init_board_refresh();
        
        kisstodo_board.check_network();
        
        kisstodo_board.initialized=true;
        
    }
    
    // called once by init_board and shoud be called at every pageinit event
    res.init_board_refresh = function() {
        
        //if (kisstodo_board.mobile) {
        //    $(".main_page").trigger('create');
        //}
        
        $(".help_toggle").colorbox({inline:true, top:"0px", left: "0px", transition:"elastic", href:"#help"});
         
        kisstodo_board.update_currently_online_visualization(false);
        
        var init_list_id = kisstodo_board.inbox_list_id;
        
        if (kisstodo_board.selected_list_id != '' ) {init_list_id=kisstodo_board.selected_list_id;}
        
        kisstodo_board.refresh_list_list(init_list_id);
       
        $('#description').hint();
        $('#description').blur();
    }
    
    res.update_todo = function(todo_id, data) {
        data.todo_id=todo_id
        
        $.post(kisstodo_board.urls['todo_edit']+todo_id, data, function (response) {
            
            var d = $(".selected_todo .todo_item");
            d.fadeOut(kisstodo_board.default_animation_speed);
            
            d.html(response);
             d.fadeIn(kisstodo_board.default_animation_speed);
            /*d.load(kisstodo_board.urls['todo_show_item']+todo_id, function () {
                d.fadeIn(kisstodo_board.default_animation_speed);
            });*/

        });    
        
    }
    
    res.search_todo = function(search_string) {
        $(".todo_list").fadeOut(kisstodo_board.default_animation_speed);
        
        var ajax_url = kisstodo_board.urls['todo_search'];
        
        ajax_url=ajax_url.replace('#sort_mode', kisstodo_board.sort_mode);
        ajax_url=ajax_url.replace('#show_complete', kisstodo_board.show_complete);
        ajax_url=ajax_url.replace('#search_string', $("#search_string").val());
        
        $.get(ajax_url, function(response) {
            $(".todo_list").html(response);
            $(".todo_list").fadeIn(kisstodo_board.default_animation_speed);
            $("#search_string").focus();
        });  
    }
    
    res.refresh_todo_list = function (list_id) {
        $(".todo_list").fadeOut(kisstodo_board.default_animation_speed);
        
        var ajax_url = kisstodo_board.urls['todo_list_complete'];
        ajax_url=ajax_url.replace('#sort_mode', kisstodo_board.sort_mode);
        ajax_url=ajax_url.replace('#show_complete', kisstodo_board.show_complete);
        ajax_url=ajax_url.replace('#list_id', list_id);

        if (kisstodo_board.is_currently_online())
        {
        $.get(ajax_url, function(response) {
        
            if (response.indexOf('<!DOCTYPE HTML>')==0) document.location = "/accounts/login/";
            
            var received_list_id=$(response).find("#list_id").val();
            var sel = $(kisstodo_board.selector_prefix+"#selected_list_option").val();
            //console.log("expecting "+list_id+", selected="+sel);
            
            if (received_list_id==sel) $(".todo_list").html(response);
            
            $(".todo_list").fadeIn(kisstodo_board.default_animation_speed);
            
            $("#add_todo_form").find("#description").focus();
            
            if (list_id==-1) $(".todo_list").html("");
            
            localStorage.setItem('todo_list_'+kisstodo_board.mobile.toString()+list_id, response);
            
            if (kisstodo_board.mobile) $(".todo_list ul").listview();
        });
        } else
        {
            $(".todo_list").html(localStorage.getItem('todo_list_'+kisstodo_board.mobile.toString()+list_id));
            $(".todo_list").fadeIn(kisstodo_board.default_animation_speed);
            
            $("#add_todo_form").find("#description").focus();
            
            if (list_id==-1) $(".todo_list").html("");
            
            if (kisstodo_board.mobile) $(".todo_list ul").listview();
        }
        
        var selcted_list_name = $(kisstodo_board.selector_prefix+"#selected_list_option option[value='"+list_id+"']").text();
        $('#collapsible_title .ui-btn-text').text(selcted_list_name);
        
        //$('#collapsible_container').collapsible({collapsed: false});
    }
    
    res.refresh_selected_todo_list = function() {
        var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
        if (!list_id) list_id=$('#selected_list_option').val();
        kisstodo_board.refresh_todo_list(list_id);
    }
    
    res.refresh_list_list = function(selected_list_id) {
        $(".list_list").fadeOut(kisstodo_board.default_animation_speed);
         if (kisstodo_board.is_currently_online())
        {
        $.get(kisstodo_board.urls['list_list']+selected_list_id, function(response) {
        
            //console.log("refresh_list_list RESPONSE:'"+response+'');
            if (response.indexOf('<!DOCTYPE HTML>')==0) document.location = "/accounts/login/";
            
            $(".list_list").html(response);
            
            kisstodo_board.update_list_edit_tools();
            $(".list_list").fadeIn(kisstodo_board.default_animation_speed);
            
            kisstodo_board.refresh_todo_list(selected_list_id);
            
            localStorage.setItem('list_list', response);
            
            if (kisstodo_board.mobile) $('.list_list select').selectmenu();
        });   
        } else {
             $(".list_list").html(localStorage.getItem('list_list'));
             
             kisstodo_board.update_list_edit_tools();
             $(".list_list").fadeIn(kisstodo_board.default_animation_speed);
             kisstodo_board.refresh_todo_list(selected_list_id);
             
             if (kisstodo_board.mobile) $('.list_list select').selectmenu();
        }
    }    
    
    res.select_next_list = function(increment) {
        var option_count = $(kisstodo_board.selector_prefix+'#selected_list_option option').length;
        var selected_index = $(kisstodo_board.selector_prefix+'#selected_list_option').prop('selectedIndex');
        
        var new_selected_index = selected_index + increment;
        
        if (new_selected_index<0) new_selected_index = 0;
        if (new_selected_index>=option_count) new_selected_index = option_count-1;        
        
        if (selected_index!=new_selected_index) {
            
            if (kisstodo_board.mobile) {
                var new_seleted_list_id=$(kisstodo_board.selector_prefix+'#selected_list_option option:eq('+new_selected_index+')').attr("value");

                var reverse = false;
                if (increment <0) reverse = true;
                
                kisstodo_board.selected_list_id=new_seleted_list_id;
                $.mobile.changePage(kisstodo_board.urls['mobile_board_list_id']+new_seleted_list_id,  {transition: "slide", reverse: reverse});
                
            }
            else {
                $(kisstodo_board.selector_prefix+'#selected_list_option').prop('selectedIndex', new_selected_index);
                $(kisstodo_board.selector_prefix+'#selected_list_option').change();
            }
            

        }
        
        return false;
        
        /*
        var lists=$("a.list");
        var selected_list=$("a.selected_list");
        var selected_id=-1;
        var selected_index=-1;
        if ((selected_list).length>0) {
            selected_id=selected_list.attr("id").replace('list_','');
        }
        
        var ids=new Array()

        for (x=0; x<lists.length; x++) {
            ids[x]=$(lists[x]).attr("id").replace('list_','');
            if (ids[x]==selected_id) selected_index=x;
        }
        
        var new_index=selected_index+increment;
        
        if (new_index<0) new_index=0;
        if (new_index <lists.length) {
            new_id=ids[new_index];
            $("#list_"+new_id).click();
        }
        */
    }

    res.lockGui = function() {
        if (kisstodo_board.mobile) {
            $.mobile.showPageLoadingMsg();
        }
        else {
              $.blockUI({message:"", overlayCSS:  {
                backgroundColor: '#000',
                opacity:	  	 0.1,
                cursor:		  	 'wait'
            },css: { backgroundColor: '#fff', color: '#fff'}});
            $('#wait').fadeIn();
        }
        
    }

    res.unlockGui = function() {
        if (kisstodo_board.mobile) {
            $.mobile.hidePageLoadingMsg();
        }
        else {
            $.unblockUI();
            $('#wait').fadeOut();
        }

    }
    
    res.show_offline_message = function() {
        kisstodo_board.show_message("Non available in offline mode.");
    }
    
    res.add_list = function() {
        
        var item = $("#add_list_form");

        var data = {
            name: item.find("#name").val(),
            csrfmiddlewaretoken : kisstodo_board.csrftoken
        };
        
        if (data.name == '') return false;
        
        item.find("#name").val("");
                
        $.post(kisstodo_board.urls['list_add'], data, function (response) {
            kisstodo_board.refresh_list_list(response);
            kisstodo_board.show_message("List created.");
        });

        
        return false;
    }    
    
    res.update_list_edit_tools = function() {
        var index = $(kisstodo_board.selector_prefix+'#selected_list_option').prop('selectedIndex');
        var selected = $(kisstodo_board.selector_prefix+'#selected_list_option').val();
        
        if (index==0 || selected <0 || kisstodo_board.mobile)
            $('.list_edit_delete').hide();
        else
            $('.list_edit_delete').show();
    }
    
    res.add_todo = function() {
        if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
        
        var item = $(kisstodo_board.selector_prefix+"#add_todo_form");
        
        var data = {
            description: item.find("#description").val(),
            list_id: item.find("#list_id").val(),
            csrfmiddlewaretoken : kisstodo_board.csrftoken
        };
        
        if (data.description == '') return false;
                
        $.post(kisstodo_board.urls['todo_add'], data, function (response) {
            var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
            kisstodo_board.refresh_todo_list(list_id);
        });

        return false;
    }     
    
    res.edit_selected_todo = function() {
        if ($(".selected_todo").hasClass('complete')) return;
        
        if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
        
        todo_id=$(".selected_todo").attr("id").replace('todo_li_','');
        var d = $(".selected_todo .todo_item");
        
        if (kisstodo_board.mobile)
        {
            //$.mobile.changePage(kisstodo_board.urls['todo_edit']+todo_id, {	transition: "pop",	reverse: false,	changeHash: false});
            $.mobile.changePage(kisstodo_board.urls['todo_edit']+todo_id, { transition: "pop" });
        }
        else
        {
            d.fadeOut(kisstodo_board.default_animation_speed);
            d.load(kisstodo_board.urls['todo_edit']+todo_id, function () {
                d.fadeIn(kisstodo_board.default_animation_speed);
                $('#edit_todo_description').focus();
                //setTimeout( function(){$('#edit_todo_description').select();}, 20);
                $('#edit_todo_repeat_every').spinner({ min: 1, max: 30 });
            });
        } 
    }     
    
    res.save_selected_todo = function() {
        if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
        
        var todo_id=$(".selected_todo").attr("id").replace('todo_li_','');
        
        var d = $(".selected_todo .todo_item");
        
        
        var data = {
            todo_id: todo_id,
            description: $('#edit_todo_description').val(),
            priority: $('#edit_todo_priority').val(),
            list_id: $('#edit_todo_list_id').val(),
            due_date: $('#edit_todo_due_date').val(),
            
            repeat_type: $('#edit_todo_repeat_type').val(),
            repeat_every: $('#edit_todo_repeat_every').val(),
            
            notify_minutes: $('#edit_todo_notify_minutes').val(),
            
            time_offset: new Date().getTimezoneOffset(),
            csrfmiddlewaretoken : kisstodo_board.csrftoken
        };
        
        if ($('input[name=edit_todo_priority]:checked').length>0)
            data.priority = $('input[name=edit_todo_priority]:checked').val();
        
        $.post(kisstodo_board.urls['todo_edit']+todo_id, data, function (response) {
        
            if (kisstodo_board.mobile) {
                    //$('.todo_delete_button_container').parent().trigger('create');
                    history.back();
                    kisstodo_board.refresh_selected_todo_list();
                    //$.mobile.changePage('#main_page');
            }
            else {
                d.fadeOut(0);
                d.html(response);
                //console.log("HTML updated");
                d.fadeIn(kisstodo_board.default_animation_speed);
                //d.load(kisstodo_board.urls['todo_show_item']+todo_id, function () {
                //    d.fadeIn(kisstodo_board.default_animation_speed);
                //});
            }
            /*if (kisstodo_board.mobile) {
                history.back();
                setTimeout( function(){$('.todo_delete_button_container').trigger('create');}, 500);
            }*/
        });    
    }
    
    res.event_keypress = function(event) {
        
        //console.log ("event_keypress: "+event.which);
        
        // enter
        if (event.which == 13) {
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            
            if (kisstodo_board.is_todo_edit_active()) {
                kisstodo_board.save_selected_todo();
            }
            else if (kisstodo_board.is_list_edit_active()) {
                var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
                                
                var data = {name: $('#edit_list_name').val(), csrfmiddlewaretoken : kisstodo_board.csrftoken};
                
                $.post(kisstodo_board.urls['list_edit']+list_id, data, function (response) {
                    kisstodo_board.refresh_list_list(list_id);
                    
                    $('#list_edit_container').fadeOut(kisstodo_board.default_animation_speed);
                    $('#list_edit_container').html("");
                });                   
            }
            else if ($(".selected_todo").length>0) {
                kisstodo_board.edit_selected_todo();
            }
            else if (kisstodo_board.focused_element=='search_string') {
                search_string = $("#search_string").val();
                if (search_string=="") return;
                kisstodo_board.search_todo(search_string);
            }
            else if (kisstodo_board.focused_element=='description') {
                kisstodo_board.add_todo();
            }
            
        }
        
        //  d
        if (event.which == 100) {
            if (kisstodo_board.is_edit_active()) return;
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            $(".selected_todo .todo_delete img").click();
        }
        
        // c
        if (event.which == 99) {
            if (kisstodo_board.is_edit_active()) return;
            
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            
            
            $(".selected_todo .todo_complete").click();
        }   

        // p
        if (event.which == 112) {
            if (kisstodo_board.is_edit_active()) return;
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            
            kisstodo_board.postpone_selected_todo();
        }           
        
        // 1..4
        if (event.which >= 49 && event.which<=52) {
            if (kisstodo_board.is_edit_active()) return;
            if ($(".selected_todo").length==0) return;
            
            if (!kisstodo_board.is_currently_online()) {kisstodo_board.show_offline_message(); return;}
            
            var todo_id=$(".selected_todo").attr("id").replace('todo_li_', '');
            kisstodo_board.update_todo(todo_id, {priority:event.which-48, csrfmiddlewaretoken : kisstodo_board.csrftoken});
        }
        
    }
    
    res.todo_edit_abort = function() {
        var d = $(".selected_todo .todo_item");
        var todo_id=$(".selected_todo").attr("id").replace('todo_li_', '');
        d.fadeOut(kisstodo_board.default_animation_speed);
        d.load(kisstodo_board.urls['todo_show_item']+todo_id, function () {d.fadeIn(kisstodo_board.default_animation_speed);});      
    }
    
    res.list_edit_abort = function() {
        var list_id=$(kisstodo_board.selector_prefix+'#selected_list_option').val();
        kisstodo_board.refresh_list_list(list_id);
        $('#list_edit_container').fadeOut(kisstodo_board.default_animation_speed);
        $('#list_edit_container').html("");
    }    
    
    res.postpone_selected_todo = function() {
        if ($('.selected_todo').length==0) return;
        
        var d = $(".selected_todo .todo_item");
        var todo_id=$(".selected_todo").attr("id").replace('todo_li_', '');
        d.fadeOut(kisstodo_board.default_animation_speed);
        
        var data = {
                todo_id: todo_id,
                csrfmiddlewaretoken : kisstodo_board.csrftoken
        };
            
        $.post(kisstodo_board.urls['todo_postpone'], data, function (response) {
                d.load(kisstodo_board.urls['todo_show_item']+todo_id, function () {d.fadeIn(kisstodo_board.default_animation_speed);});      
        });        
        
    }

    res.event_keydown = function(event) {  
        
        //console.log ("event_keydown: "+event.which);
        
        // TAB
        if (event.which == 9) {
            if (kisstodo_board.is_edit_active()) return;
            
            if (kisstodo_board.sort_mode=='D') { 
                $('#sort_mode_P').click();
            } else if (kisstodo_board.sort_mode=='P') {
                $('#sort_mode_A').click();
            } else {
                $('#sort_mode_D').click();
            }
            return false;
        }
        
        // ESC
        if (event.which == 27) {
            if (kisstodo_board.is_todo_edit_active()) {
                setTimeout(function(){kisstodo_board.todo_edit_abort();}, 1);
            }
            else if (kisstodo_board.is_list_edit_active()) {
                setTimeout(function(){kisstodo_board.list_edit_abort();}, 1);
            }
            else {
                kisstodo_board.select_next_todo(0);
                if (kisstodo_board.focused_element!='') $('#'+kisstodo_board.focused_element).blur();
            }
        }        
        
        // UP
        if (event.which == 38) {
            if (kisstodo_board.is_edit_active()) return; 
            
            if (kisstodo_board.focused_element=='name') return;
            
            $(kisstodo_board.selector_prefix+"#selected_list_option").blur();
            
            if (kisstodo_board.focused_element=='description') {
                $('#name').focus();
                return;
            }
            
            kisstodo_board.select_next_todo(-1);
            
            return false;
        }        
        
        // DOWN
        if (event.which == 40) {
            if (kisstodo_board.is_edit_active()) return;
            
            if (kisstodo_board.focused_element=='name' && $('#description').length>0) {
                $('#description').focus();
                return;
            }
            
            $(kisstodo_board.selector_prefix+"#selected_list_option").blur();
             
            kisstodo_board.select_next_todo(+1);
            
            return false;
        }     
        
        // LEFT
        if (event.which == 37) {
            
            if (kisstodo_board.is_edit_active()) return;
            
            $(kisstodo_board.selector_prefix+"#selected_list_option").blur();

            if (kisstodo_board.focused_element=='description' && $("#description").val()) {
                return;
            }
            kisstodo_board.select_next_list(-1);
        }    
        
        // RIGHT
        if (event.which == 39) {
            if (kisstodo_board.is_edit_active()  || kisstodo_board.ajax_pending) return;
            
            $(kisstodo_board.selector_prefix+"#selected_list_option").blur();
            
            if (kisstodo_board.focused_element=='description' && $("#description").val()) {
                return;
            }
            kisstodo_board.select_next_list(1);
        }            

    } 
    
    res.select_next_todo = function(increment) {
       
        $('.todos li.todo_li').removeClass("selected_todo");
        
        if (increment==0) {
            kisstodo_board.selected_todo_index=-1;
            return;
        }
        
        if (kisstodo_board.focused_element=="description") $('#description').blur();
        if (kisstodo_board.focused_element=="name") $('#name').blur();
        
        var selected_todo_index_max=$('.todos li.todo_li').length-1;
                
        kisstodo_board.selected_todo_index+=increment;
        
        if (kisstodo_board.selected_todo_index<0) { kisstodo_board.selected_todo_index=0; if ($('#description').length>0) $('#description').focus(); else $('#name').focus();}
        if (kisstodo_board.selected_todo_index>selected_todo_index_max) { kisstodo_board.selected_todo_index=selected_todo_index_max; }
        
        $('.todos li.todo_li:eq('+kisstodo_board.selected_todo_index+')').addClass("selected_todo");
    }
    
    res.is_todo_edit_active = function() {
        return  $('#edit_todo_description').length>0;
    }
    
    res.is_list_edit_active = function() {
        return  $('#edit_list_name').length>0;
    }
    
    res.is_edit_active = function() {
        return  kisstodo_board.is_todo_edit_active() || kisstodo_board.is_list_edit_active();
    }    
    
    res.show_message = function(message) {
        $('#message_text').html(message).fadeIn(kisstodo_board.default_animation_speed*2);
        
        setTimeout(function() {$('#message_text').fadeOut(kisstodo_board.default_animation_speed*2);}, kisstodo_board.long_animation_speed);
    }    
    
    res.check_network = function() {
        
        if (navigator.onLine) {
            $.ajax({
                async: true,
                cache: false,
                dataType: "json",
                error: function (req, status, ex) {
                   
                   
                    kisstodo_board.set_network_available(false);
                },
                success: function (data, status, req) {
                    
                    kisstodo_board.set_network_available(true);
                },
                timeout: 10000,
                type: "GET",
                url: "/static/js/ping.js"
            });
        } else {

            kisstodo_board.set_network_available(false);
        }
    }       

     /*
     res.show_network = function(online) {
          console.log("called show_network:"+online);
          console.log("kisstodo_board.is_currently_online(): "+kisstodo_board.is_currently_online());
          //if (online != kisstodo_board.is_currently_online()) {
            if (online) {
                
                 console.log('show_network:I am online');
            } else {

                 console.log('show_network:I am offline');
            }
            
            kisstodo_board.set_currently_online(online, true);
        //}
    }      */
    
    res.is_currently_online = function() {
        if (localStorage.getItem('currently_online')=="false") return false;
        
        return new Boolean(localStorage.getItem('currently_online'));
    }
    
    res.set_currently_online = function(value, notify) {
        localStorage.setItem('currently_online', value);
        kisstodo_board.update_currently_online_visualization(notify);
    }
    
    //
    res.is_network_available = function() {
        if (localStorage.getItem('network_available')=="false") return false;
        
        return new Boolean(localStorage.getItem('network_available'));
    }
    
    res.set_network_available = function(value, notify) {
        localStorage.setItem('network_available', value);
    }
    //
    
    res.update_currently_online_visualization = function(notify) {
        value = kisstodo_board.is_currently_online();
        $('.network_switch').html(value?'go offline':'go online');
        if (notify)
            kisstodo_board.show_message('You are '+(value?'online':'offline'))
    }    
    
        
    //$(document.body).bind("online", res.check_network);
    //$(document.body).bind("offline", res.check_network);
    
    
    res.selected_todo_index=0;
    res.focused_element = '';
    res.sort_mode = 'D';
    res.show_complete = 'T';
    res.ajax_pending = false;
    res.initialized = false;
    
    // CONFIG
    res.default_animation_speed=150;
    res.long_animation_speed=1500;
        
    return res; 
}());
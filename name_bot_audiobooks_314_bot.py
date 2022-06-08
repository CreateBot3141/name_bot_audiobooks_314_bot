
def get_down_menu_tovar (user_id,namebot,markup,parents):
    import iz_func
    import iz_telegram
    from telebot import types
    db,cursor = iz_func.connect ()
    sql_id = iz_telegram.load_variable (user_id,namebot,'SQL запрос')
    mn41 = types.InlineKeyboardButton(text = iz_telegram.get_namekey (user_id,namebot,"Назад"),callback_data  ="back_"+str(sql_id))
    markup.add(mn41)
    sql = "select id,user_id,`like` from bot_favorites where namebot = '"+str(namebot)+"' and id_tovar = '"+str(parents)+"' "
    cursor.execute(sql)
    results = cursor.fetchall()   
    summ_like    = 0 
    summ_dezlike = 0
    for row in results:
        id,user_id,like  = row.values()
        if like == 1:
            summ_like = summ_like + 1
        if like == -1:
            summ_dezlike = summ_dezlike + 1
    mn21 = types.InlineKeyboardButton(text="👍"+"("+str(summ_like)+")",callback_data  ="like_good_"+str(parents))
    mn22 = types.InlineKeyboardButton(text='Фото и комментарий',callback_data="send_foto_"+str(parents))
    mn23 = types.InlineKeyboardButton(text="👎"+"("+str(summ_dezlike)+")",callback_data  ="like_bad_"+str(parents))
    markup.add(mn21,mn22,mn23)
    sql = "select id,user_id from bot_basket where user_id = '"+str(user_id)+"' and  product = '"+str(parents)+"' and namebot = '"+namebot+"' and status = '1' limit 1"
    cursor.execute(sql)
    results = cursor.fetchall()    
    id = 0
    for row in results:
        id,user_id = row.values()
    if id == 0:
        like = ''
    else:    
        like = '💝'
    mn31 = types.InlineKeyboardButton(text= like +iz_telegram.get_namekey (user_id,namebot,"В избранное"),callback_data  ="like_Избранные_"+str(parents))
    markup.add(mn31)
    db.close
    return markup 

def get_info_in_name    (katalog):
    import iz_func
    db,cursor = iz_func.connect ( )
    sql = "select id,name,picture,parents from bot_product where id = '"+str(katalog)+"' limit 1"
    cursor.execute(sql)
    data = cursor.fetchall()
    id      = 0
    name    = ''
    picture = ''
    parents = ''
    for rec in data:
        id,name,picture,parents = rec.values()
    return id,name,picture,parents

def get_info_in_book    (katalog):
    import iz_func
    name    = ''
    change  = ''
    about   = ''
    avtor   = ''
    picture = '' 
    db,cursor = iz_func.connect ( )
    sql = "select id,name,picture,parents,change_name,about from bot_product where id = '"+str(katalog)+"' limit 1"
    cursor.execute(sql)
    data = cursor.fetchall()
    name = ''
    for rec in data:
        id,name,picture,parents,change_name,about = rec.values()
    change = change_name   
    sql = "select id,meaning from bot_features where name = '"+str(name)+"' and features = 'avtor' limit 1"
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:
        id,avtor  = rec.values()
    db.close    
    return id,change,about,avtor,picture    

def send_audio_file     (word,user_id,namebot):
    import iz_func
    import iz_telegram
    import time
    db,cursor = iz_func.connect ( )
    sql = "select id,name,picture,parents,change_name from bot_product where id = '"+str(word)+"' limit 1"
    cursor.execute(sql)
    data = cursor.fetchall()
    for rec in data:        
        id_product,name_file,picture,parents,change_name = rec.values()
        answer = 0
        print ('            [+] Отправка текстового файла:',name_file,picture)
        #sql = "select id,name,parents from bot_product where id = '"+str(parents)+"' limit 1"
        #cursor.execute(sql)
        #data = cursor.fetchall()
        #for rec in data:
        #    id,name,parents = rec.values()
        #    print ('            [+] Родитель аудиофайла:',name)
        #    pyth = '/mnt/home/Data/'+name+'/'+picture
        #    print ('            [+] Файл для скачивания:',pyth)

        #    print ('[+] pyth       ',pyth)
        pyth_new = iz_func.change_back(change_name)+picture
        pyth = pyth_new
        #    print ('[+] change_name',pyth_new)
        try:
            import telebot            
            audio  = open(pyth,'rb')
            message_out,menu = iz_telegram.get_message (user_id,'Скачивается файл. Ждите ...',namebot)
            markup = ''
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0) 
            token  = iz_func.get_token (namebot)
            bot    = telebot.TeleBot(token)
            bot.send_audio(user_id, audio)                            
            sql = "INSERT INTO audiobook_download (`id_product`,`quantity`,`user_id`,`comment`) VALUES ('{}','{}','{}','{}')".format (id_product,1,user_id,'Удачно')
            cursor.execute(sql)
            db.commit()
            message_out,menu = iz_telegram.get_message (user_id,'Файл скачен',namebot)
            kommanda = "" 
            kommanda = kommanda +name_file+ '\n'
            kommanda = kommanda +'/listen_'   +str(word)+' - <code>Отметить что прослушан</code>'+ '\n'
            message_out      = message_out.replace('%%ОтмеченПрочтен%%',str(kommanda))
            markup = ''
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,answer)
        except Exception as e:
            print ('[error]',e)
            sql = "INSERT INTO audiobook_download (`id_product`,`quantity`,`user_id`,`comment`) VALUES ('{}','{}','{}','{}')".format (id_product,1,user_id,'Ошибка')
            cursor.execute(sql)
            db.commit()
            message_out,menu,answer = iz_telegram.send_message (user_id,namebot,"Ошибка скачивания файла",'S',answer) 

        time.sleep (3)

def complite_message    (id_book,name_book,about,avtor,picture,word,user_id,namebot):
    import iz_telegram
    import iz_func
    id,name,picture,parents = get_info_in_name (word)
    message_out,menu = iz_telegram.get_message (user_id,'Список файлов',namebot)
    if name_book != '':
        message_out = message_out.replace('%%Название%%',name_book)
        message_out = message_out.replace('%%Автор%%',avtor)
        message_out = message_out.replace('%%Описание%%',about)
    else:
        message_out = message_out.replace('%%Название%%',name)
        message_out = message_out.replace('%%Автор%%',"нет данных")
        message_out = message_out.replace('%%Описание%%',"нет данных")

    if iz_telegram.check_admin (namebot,user_id) == 'Y':
        kommanda    = '\n'
        kommanda = kommanda +''+ '\n'
        kommanda = kommanda +'/name_'   +str(word)+' - <code>Исправить имя</code>'+ '\n'
        kommanda = kommanda +'/about_'  +str(word)+' - <code>Исправить описание</code>'+ '\n'
        kommanda = kommanda +'/comment_'+str(word)+' - <code>Добавить комментарий</code>'+ '\n'    
        kommanda = kommanda +'/delete_' +str(word)+' - <code>Удалить</code>'+ '\n'
    else:
        kommanda = ""
        kommanda = kommanda +'/comment_'+str(word)+' - <code>Добавить комментарий</code>'+ '\n'   

    message_out = message_out.replace('%%Команды%%',kommanda)
    return message_out

def send_photo          (user_id,namebot,picture):
    import telebot
    import iz_telegram
    import iz_func
    answer = 'Отправлено'
    token = iz_telegram.get_token (namebot)
    try:
        bot   = telebot.TeleBot(token) 
        photo = open(picture,'rb')
        bot.send_photo(user_id, photo)
        answer = 'Отправлено'
    except Exception as e:
        pass
        answer = 'Ошибка'
        db,cursor = iz_func.connect ()
        err = str(e)

def start_prog          (user_id,namebot,message_in,status,message_id,name_file_picture,telefon_nome,refer,user_id_refer,FIO_id): 
    import iz_func
    import iz_telegram
    import time
    answer = ''
    db,cursor = iz_func.connect ()
    if message_in.find ('/start') != -1:
        refer          = refer
        user_id_refer  = user_id_refer 
        FIO_id         = FIO_id
        if FIO_id[0] == 0:
            print ('[+] Внимание новый пользователь')
            print ('[+] Проверка выплаты баланса')
            sql = "select id,result from bot_balans where namebot = '"+str(namebot)+"' and user_id = '"+str(user_id_refer)+"' and comment = 'Выплата за реферала "+str(user_id)+"' limit 1;".format()
            cursor.execute(sql)
            data = cursor.fetchall()
            id = 0
            for rec in data: 
                id,result = rec.values() 
            if id == 0:
                message_out,menu = iz_telegram.get_message (user_id_refer,'Выплата за реферала',namebot)
                #message_out = message_out.replace('%%Процент%%',str(minmin))   
                markup = ''
                answer = iz_telegram.bot_send (user_id_refer,namebot,message_out,markup,0) 
                comment = "Выплата за реферала "+str(user_id)
                iz_telegram.add_money (namebot,user_id_refer,100,comment,'Руб')
            else:    
                message_out,menu = iz_telegram.get_message (user_id,'За пользователя выплата уже была',namebot)
                #message_out = message_out.replace('%%Процент%%',str(minmin))   
                markup = ''
                answer = iz_telegram.bot_send (user_id_refer,namebot,message_out,markup,0)     
        else:    
            print ('[+] Пользователь уже был в системе')
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''
        answer = 'Ответ'

    if message_in == 'Список книг':
        parents = "Родитель Продукта в 1С не указан"
        sql_id = iz_telegram.start_list (user_id,namebot,10,0,0,'',parents,'id DESC') ## Записываю новый порядок показа списка, По 10 штук, начиная с первого, с показателем родителя
        iz_telegram.save_variable (user_id,namebot,"SQL запрос",str(sql_id))
        markup = ''
        sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
        markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)   #### Получаю список товаров. Согласно SQL
        message_out,menu = iz_telegram.get_message (user_id,'Список аудиокниг',namebot)
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in == 'Coin Farmer':
        answer = 'Ответ'
        import iz_game
        iz_game.game_farmer (user_id,namebot,"start",message_id,refer)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('game_farmer_')     != -1:
        import iz_game        
        answer = 'Ответ'
        iz_game.game_farmer (user_id,namebot,message_in,message_id,refer)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('list_all_book_')   != -1:
        word  = message_in.replace('list_all_book_','')
        message_out,menu = iz_telegram.get_message (user_id,'Высылаем все файлы сразу',namebot)
        markup = ''
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        sql = "select id,name,picture,parents from bot_product where parents = '"+str(word)+"' ORDER BY name"
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data:
            id_product,name,picture,parents = rec.values()
            send_audio_file (id_product,user_id,namebot)
            
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,"Все файлы отправлены",'S',0)
        iz_telegram.save_variable (user_id,namebot,"status",'')    
        status = ''            

    if message_in.find ('katalog_')         != -1:
        answer = 'Ответ'
        word = message_in.replace('katalog_','')        
        parents = word
        if_grup = iz_telegram.if_grup (user_id,namebot,word)        
        if if_grup == 'Да':
            id_book,name_book,about,avtor,picture  = get_info_in_book (word)
            message_out = complite_message (id_book,name_book,about,avtor,picture,word,user_id,namebot)
            sql_id = iz_telegram.start_list (user_id,namebot,15,0,0,'',word,'grup,name')            ### Печать списка файлов
            list   = [['Вывести список','list_all_book_'+str(word)]]
            markup = iz_telegram.list_menu (user_id,namebot,list)
            sql    = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
            markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
            markup = get_down_menu_tovar (user_id,namebot,markup,word) 
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        iz_telegram.save_variable (user_id,namebot,"status",'')    
        status = ''            
        if if_grup == 'Нет' or if_grup == '':  
            send_audio_file (word,user_id,namebot)
            sql = "select id,parents,kod_1c from bot_product where namebot = '"+str(namebot)+"' and id = '"+str(word)+"' limit 1"
            parents_r = 0
            cursor.execute(sql) 
            results = cursor.fetchall()    
            for row in results:
                 id_r,parents_r,kod_1c_r = row.values()
            sql_id = iz_telegram.start_list (user_id,namebot,15,0,0,'',parents_r,'grup,name')            
            markup = ''
            sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
            sql = ""
            markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
            markup = get_down_menu_tovar (user_id,namebot,markup,parents_r) 
            id_book,name_book,about,avtor,picture  = get_info_in_book (parents_r)
            message_out = complite_message (id_book,name_book,about,avtor,picture,word,user_id,namebot)
            #answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        status = ''    

    if message_in.find ('back_')            != -1:
        word  = message_in.replace('back_','')
        message_out,menu = iz_telegram.get_message (user_id,'Список аудиокниг',namebot)    
        sql_id = word
        sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
        markup = ''
        markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('Избранный список') != -1:
        from telebot import types
        markup = types.InlineKeyboardMarkup(row_width=4)
        message_out = ''
        import iz_func
        sql = "select id,product from bot_basket where namebot = '"+str(namebot)+"' and user_id = "+str(user_id)+" limit 10;".format(namebot)
        cursor.execute(sql)
        data = cursor.fetchall()
        id = 0
        for rec in data: 
            id,product = rec.values()
            sql  = "select id,name from bot_product where id = '"+str(product)+"' limit 1;"
            cursor.execute(sql)
            data2 = cursor.fetchall()
            for rec2 in data2:
                id_product,name_product = rec2.values()
                name_tovar = iz_telegram.get_namekey(user_id,namebot,name_product)
                mn01 = types.InlineKeyboardButton(text=name_tovar,callback_data = "favorites_"+str(id_product))
                markup.add(mn01)
        if id == 0:
            message_out,menu = iz_telegram.get_message (user_id,'Спиок избранный пустой',namebot)
            markup = 0
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0)
        else:    
            message_out,menu = iz_telegram.get_message (user_id,'Избранный список показать',namebot)
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0)
        answer = 'Ответ'   
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = '' 

    if message_in.find ('like_Избранные')   != -1:
        word = message_in.replace('like_Избранные_','')
        answer = iz_func.change (str(word))
        db,cursor = iz_func.connect ()
        sql = "select id,product,status from bot_basket where product = '"+str(word)+"' and namebot = '"+str(namebot)+"' and user_id = '"+str(user_id)+"'  limit 1;"
        cursor.execute(sql)
        data = cursor.fetchall()
        id = 0
        status = '0'
        for rec in data: 
            id,product,status = rec.values()

        if id == 0:
            sql = "INSERT INTO bot_basket (namebot,`price`,product,status,unixtime,user_id,`сurrency`) VALUES ('{}','{}','{}','{}',{},'{}','{}')".format (namebot,0,word,'',0,user_id,'')
            cursor.execute(sql)
            db.commit()
            lastid = cursor.lastrowid
        else:    
            lastid = id

        if status == '0':
            sql = "UPDATE bot_basket SET status = '1' WHERE id = "+str(lastid) + ""
            cursor.execute(sql)
            db.commit()
        else:    
            sql = "UPDATE bot_basket SET status = '0' WHERE id = "+str(lastid) + ""
            cursor.execute(sql)
            db.commit()
        sql_id = iz_telegram.start_list (user_id,namebot,24,0,0,'',word,'grup,name')            
        markup = ''
        sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
        markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
        markup = get_down_menu_tovar (user_id,namebot,markup,word) 
        id_book,name_book,about,avtor,picture  = get_info_in_book (word)
        message_out,menu = iz_telegram.get_message (user_id,'Список файлов',namebot)
        if name_book != '':
            message_out = message_out.replace('%%Название%%','11111111111')  ### name_book
            message_out = message_out.replace('%%Автор%%',avtor)
            message_out = message_out.replace('%%Описание%%',about)
        else:
            message_out = message_out.replace('%%Название%%',"")
            message_out = message_out.replace('%%Автор%%',"")
            message_out = message_out.replace('%%Описание%%',"")
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('favorites_')       != -1:
        word  = message_in.replace('favorites_','')
        parents = word
        if_grup = iz_telegram.if_grup (user_id,namebot,word)        
        if if_grup == 'Да':
            id_book,name_book,about,avtor,picture  = get_info_in_book (word)
        message_out = complite_message (id_book,name_book,about,avtor,picture,word,user_id,namebot)
        sql_id = iz_telegram.start_list (user_id,namebot,15,0,0,'',word,'grup,name')            
        list   = [[iz_telegram.get_namekey (user_id,namebot,'Вывести список'),'list_all_book_'+str(word)]]
        markup = iz_telegram.list_menu (user_id,namebot,list)
        sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
        markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
        markup = get_down_menu_tovar (user_id,namebot,markup,word) 
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('like_good_')       != -1:
        word  = message_in.replace('like_good_','')
        #answer = iz_func.change (str(word))
        db,cursor = iz_func.connect ()
        sql = "select id,id_tovar from bot_favorites where id_tovar = '"+str(word)+"' and namebot = '"+str(namebot)+"' and user_id = '"+str(user_id)+"'  limit 1;"
        cursor.execute(sql)
        data = cursor.fetchall()
        id = 0
        for rec in data: 
            id,id_tovar = rec.values()
        if id == 0: 
            sql = "INSERT INTO bot_favorites (id_tovar,`like`,name_tovar,namebot,user_id) VALUES ('{}',{},'{}','{}','{}')".format (word,1,'',namebot,user_id)
            cursor.execute(sql)
            db.commit()
            sql_id = iz_telegram.start_list (user_id,namebot,26,0,0,'',word,'grup,name')            
            markup = ''
            sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
            markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
            markup = get_down_menu_tovar (user_id,namebot,markup,word) 
            id_book,name_book,about,avtor,picture  = get_info_in_book (word)
            message_out,menu = iz_telegram.get_message (user_id,'Список файлов',namebot)
            if name_book != '':
                message_out = message_out.replace('%%Название%%','22222')  ### name_book
                message_out = message_out.replace('%%Автор%%',avtor)
                message_out = message_out.replace('%%Описание%%',about)
            else:
                message_out = message_out.replace('%%Название%%',"")
                message_out = message_out.replace('%%Автор%%',"")
                message_out = message_out.replace('%%Описание%%',"")
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)            
        iz_telegram.save_variable (user_id,namebot,"status",'')    
        status = ''    

    if message_in.find ('like_bad_')        != -1:
        word  = message_in.replace('like_bad_','')
        db,cursor = iz_func.connect ()
        sql = "select id,id_tovar from bot_favorites where id_tovar = '"+str(word)+"' and namebot = '"+str(namebot)+"' and user_id = '"+str(user_id)+"' limit 1;"
        cursor.execute(sql)
        data = cursor.fetchall()
        id = 0
        for rec in data: 
            id,id_tovar = rec.values()
        if id == 0: 
            sql = "INSERT INTO bot_favorites (id_tovar,`like`,name_tovar,namebot,user_id) VALUES ('{}',{},'{}','{}','{}')".format (word,-1,'',namebot,user_id)
            cursor.execute(sql)
            db.commit()
            sql_id = iz_telegram.start_list (user_id,namebot,27,0,0,'',word,'grup,name')            
            markup = ''
            sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'"     # and quantity > 0 and grup = 'Да'  "
            markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)
            markup = get_down_menu_tovar (user_id,namebot,markup,word) 
            id_book,name_book,about,avtor,picture  = get_info_in_book (word)
            message_out,menu = iz_telegram.get_message (user_id,'Список файлов',namebot)
            if name_book != '':
                message_out = message_out.replace('%%Название%%','22222')  ### name_book
                message_out = message_out.replace('%%Автор%%',avtor)
                message_out = message_out.replace('%%Описание%%',about)
            else:
                message_out = message_out.replace('%%Название%%',"")
                message_out = message_out.replace('%%Автор%%',"")
                message_out = message_out.replace('%%Описание%%',"")
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)            
        iz_telegram.save_variable (user_id,namebot,"status",'')    
        status = ''    

    if message_in.find ('/delete')          != -1:
        import iz_func
        word  = message_in.replace('/delete_','')
        sql = "UPDATE bot_product SET quantity = 0 WHERE id = "+str(word)
        cursor.execute(sql)
        db.commit() 
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'Продукция помечена на удаление','S',0) 
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('/name_')           != -1:
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'Введите новое имя','S',0) 
        iz_telegram.save_variable (user_id,namebot,"status",message_in)
        status = ''

    if message_in.find ('/comment_')        != -1:
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'Введите коментарий','S',0) 
        iz_telegram.save_variable (user_id,namebot,"status",message_in)        
        status = ''

    if message_in.find ('send_foto_')       != -1:
        word  = message_in.replace('send_foto_','')
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'Подробная информация','S',0) 
        #iz_telegram.save_variable (user_id,namebot,"status",message_in)        
        sql = "select id,meaning,name from bot_features where features = 'picture' and name_id = '"+str(word)+"' ;".format()
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data: 
            id,meaning,name_f = rec.values()

            #picture = '/mnt/home/picture/'+meaning             ###audio_book_20646.jpg'
            picture = '/mnt/home/Data/'+str(name_f)+'/'+meaning
            print ('[+] picture',picture)
            send_photo (user_id,namebot,picture)


        sql = "select id,text_comment,user_id from bot_comment where id_product =   '"+str(word)+"';".format()
        cursor.execute(sql)
        data = cursor.fetchall()
        for rec in data: 
            id,text_comment,user_id = rec.values()
            message_out,menu = iz_telegram.get_message (user_id,'Вывод коментария',namebot)
            message_out = message_out.replace('%%Текст коментария%%',str(text_comment))   
            message_out = message_out.replace('%%user_id%%',str(user_id))
            markup = ''
            answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0) 
        iz_telegram.save_variable (user_id,namebot,"status",'')    
        status = ''    

    if message_in.find ('next_sql_')        != -1:
        word = message_in.replace('next_sql_','')
        sql = "select id,`range`,start_nomer from bot_sql where id = '{}' limit 1;".format(word)
        cursor.execute(sql)
        data = cursor.fetchall()
        id = 0
        for rec in data: 
            id,range,start_nomer = rec.values()    
            print ('[+] id,range,start_nomer',range,start_nomer)     
        if id != 0:
            start_nomer = int(start_nomer) + int (range)
            sql = "UPDATE bot_sql SET start_nomer = '"+str(start_nomer)+"' WHERE id = "+str(id)+""
            cursor.execute(sql)
            db.commit()  
        parents = "Родитель Продукта в 1С не указан"
        sql_id = word
        markup = ''
        sql = "select id,quantity from audiobook_download where user_id = '%%user_id%%' and id_product = '%%kod_1c%%'" 
        markup = iz_telegram.get_menu_tovar (user_id,namebot,sql_id,1,markup,sql)   #### Получаю список товаров. Согласно SQL
        message_out,menu = iz_telegram.get_message (user_id,'Список аудиокниг',namebot)
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,message_id)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in == 'Поиск'                     :
        #message_out,menu = iz_telegram.get_message (user_id,'Поиск в базе',namebot)
        #message_out = message_out.replace('%%Слово поиска%%',str(message_in))   
        #markup = ''
        #answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0) 
        #iz_telegram.save_variable (user_id,namebot,"status",'')
        #status = ''
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'Поиск временно отключен','S',message_id)

    if message_in.find ('Контакты')         != -1:
        message_out,markup = iz_telegram.get_kontakt (user_id,namebot)
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if message_in.find ('/ref_report')      != -1:
        message_out,markup = iz_telegram.get_refer_report (user_id,namebot)
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0)
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''

    if status.find     ('/comment_')        != -1:
        import iz_func
        import iz_telegram        
        word  = status.replace('/comment_','')
        message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'коментарий записан','S',0) 
        iz_telegram.save_variable (user_id,namebot,"status",'')
        sql = "INSERT INTO bot_comment (id_product,name_product,namebot,text_comment,user_id) VALUES ('{}','{}','{}','{}','{}')".format (word,'',namebot,message_in,user_id)
        cursor.execute(sql)
        db.commit()
        iz_telegram.save_variable (user_id,namebot,"status",'')

    if status.find     ('/name_')           != -1:
        import iz_func
        import iz_telegram        
        iz_telegram.save_variable (user_id,namebot,"status",'')

    if message_in.find     ('/listen_') != -1:        
        word  = status.replace('/listen_','')
        id_product = word
        import iz_func
        db,cursor = iz_func.connect ()
        try:
            sql = "INSERT INTO audiobook_download (`id_product`,`quantity`,`user_id`,`comment`) VALUES ('{}','{}','{}','{}')".format (id_product,1,user_id,'Удачно')
            cursor.execute(sql)
            db.commit()
        except:
            sql = "INSERT INTO audiobook_download (`id_product`,`quantity`,`user_id`,`comment`) VALUES ('{}','{}','{}','{}')".format (id_product,1,user_id,'Ошибка')
            cursor.execute(sql)
            db.commit()

        id,name,picture,parents = get_info_in_name (word)


        message_out,menu = iz_telegram.get_message (user_id,'Отмечен как прочтенный',namebot)
        message_out = message_out.replace('%%Названия файла%%',str(name))   
        #message_out = message_out.replace('%%Заявка%%',str(command))
        markup = ''
        answer = iz_telegram.bot_send (user_id,namebot,message_out,markup,0)
        #message_out,menu,answer = iz_telegram.send_message (user_id,namebot,'Отмечен как прочтенный','S',0)     

    if answer == '' and status == '':
        message_out,menu = iz_telegram.get_message (user_id,'Поиск в базе данных',namebot)
        message_out      = message_out.replace('%%Слово поиска%%',str(message_in))   
        markup     = ''
        answer     = iz_telegram.bot_send  (user_id,namebot,message_out,markup,0) 
        sql        = "select id,name from bot_product where ( change_name like '%"+str(message_in)+"%' or about like '%"+str(message_in)+"%') and namebot = '"+namebot+"' and parents = 'Родитель Продукта в 1С не указан' limit 20"
        sql_id     = start_sql_menu_list   (sql,0,10,namebot,user_id)
        list,nomer = list_sql_menu_list    (sql_id,namebot,user_id)
        markup     = get_sql_menu_list     (list,namebot,user_id)
        if nomer == 0:
            markup = ''
            message_out,menu = iz_telegram.get_message (user_id,'Ничего не найдена',namebot)
        else:    
            message_out,menu = iz_telegram.get_message (user_id,'Найденная книга',namebot)
            message_out = message_out.replace  ('%%Найдных элементов%%',str(nomer))   
        answer      = iz_telegram.bot_send (user_id,namebot,message_out,markup,answer)    
    
    if status.find ("send_foto_") != -1:
        iz_telegram.save_variable (user_id,namebot,"status",'')
        status = ''
    db.close

def start_sql_menu_list (sql_text,start_limit,limit_step,namebot,user_id):  #### Создам запрос для дальнейщей работы
    import iz_func
    sql_text = iz_func.change (sql_text)
    db,cursor = iz_func.connect ()
    sql = "INSERT INTO bot_search (sql_text,start_limit,limit_step,namebot,user_id,comment) VALUES ('{}','{}','{}','{}','{}','')".format (sql_text,start_limit,limit_step,namebot,user_id)
    cursor.execute(sql)
    db.commit()
    lastid = cursor.lastrowid
    return lastid

def list_sql_menu_list  (sql_id,namebot,user_id):
    import iz_func
    db,cursor = iz_func.connect ()    
    sql = "select id,sql_text from bot_search where id = "+str(sql_id)+" "
    cursor.execute(sql)
    data = cursor.fetchall()
    id    = 0
    noner = 0
    for rec in data:   
        id,sql_text = rec.values() 
    sql_text = iz_func.change_back (sql_text)
    list = []
    cursor.execute(sql_text)
    data = cursor.fetchall()
    for rec in data:
        noner = noner +1
        id,name = rec.values()
        list.append([id,name])
    return list,noner   
 
def get_sql_menu_list   (list,namebot,user_id):
    import iz_telegram
    from telebot import types 
    markup = types.InlineKeyboardMarkup(row_width=4)
    for rec in list: 
        id,name = rec
        name = iz_telegram.get_namekey (user_id,namebot,name)
        mn01 = types.InlineKeyboardButton(text=name,callback_data = "katalog_"+str(id))
        markup.add(mn01)
    return markup    

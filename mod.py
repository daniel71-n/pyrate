#module for pyrate.py
import re
import sqlite3
import os
# def track(inst):
#     "decorator that adds instances that are created to the tracker.lists class data attribute "
#     tracker.lists.add(inst)
#     return inst

class debugger_cl ():
    """This takes a string as an argument that's supposed to be printed out for debugging and either prints it or does nothing,
    depending on whether self.debugging is set to True or False. That depends on whether --debugging is used at the commandline or not.
    A lot of the debug messages though are in the module itself, where the bugger_cl is imported from, and can't be instantiated, since the the 
    debugging=True parameter is based on argparse commandline option the module doesn't have access to - only the main script. So the module will instead use
    a static method c_debug_msg, which again depends on whether or not a certain value is true or not. This value is deb_msg, and it's a class attribute.
    The way it's set is by a class method - c_debugging- called without any arguments. It's called by the debugger_cl instance in the main script, at the very beginning, if args.debug is True. Otherwise it's not called, and deb_msg stays false, and no debug messages get printed from the module"""

    deb_msg = False             # set to True by calling the argument-less class method c_debugging. This is supposed to be called from the main script by the debugger_cl instance

    @classmethod
    def c_debugging(cls):       # set deb_msg to True
        cls.deb_msg = True

    @staticmethod
    def c_debug_msg(*msg):       # this needs to be used instead of 'print', everywhere there's a debugging message in this module here
        if debugger_cl.deb_msg == True:
            for i in msg:
                print(i)
        else:
            pass
        
        
    def __init__(self, debugging=False):  # below is instance data
        self.debugging = debugging

    def debug_msg(self, *msg):
        if self.debugging==True:
            for i in msg:
                print(i)
        else:
            pass



    
#find or create a database file (if it doesn't exist) and get a connection object, This should be called first every time the program launches.
class db_interface():
    def __init__ (self):
        self.connection = None
        self.cursor = None
        self.list_types= None

    def init_db(self):
        "return sqlite connection object using the sqlite3 python module - if the database exists. If, first create the database first."
        file_path = os.path.expanduser("~/pylists.db")

        if os.path.exists(file_path) == True:
            debugger_cl.c_debug_msg("database file found in the home directory. Opening it")
            db_conn = sqlite3.connect(file_path)
        else:
            debugger_cl.c_debug_msg("database file not found/missing from the home directory. Creating it now...")
            db_conn = sqlite3.connect(file_path)
            db_cursor = db_conn.cursor()  # if it's now just being created for the first time, the main table also needs to be set up, which keeps track of the lists.
            create_table = ''' CREATE TABLE list_tracker(
                                 list_name TEXT PRIMARY KEY,
                                 list_type TEXT NOT NULL)'''

            try:
                db_cursor.execute(create_table)
            except:
                print('Error. Exitting')
            else:
                db_conn.commit()    # You need to commit for the transaction to take effect and finish

        self.connection=db_conn  # assign the connection object to the instance attribute 'connection' 




        
    def get_cursor(self):
        """call this method to get a cursor object, assigning it to the 'cursor' instance attribute for later use. This implies there's already a connection object, therefore init_db() has to have already been called before calling get_cursor()"""
        cursor_object = self.connection.cursor()
        self.cursor = cursor_object



    def execute_sql(self, sql_command, deletion=False, list_name=None):
        "called by other methods for execution of some sql code"
        if not deletion:
            try:
                debugger_cl.c_debug_msg('received the sql command:', sql_command)
                self.cursor.execute(sql_command)
                self.connection.commit()
                debugger_cl.c_debug_msg('ok')
                
            except:
                debugger_cl.c_debug_msg('failed to execute sql')



        elif deletion:
            # try:
            self.cursor.execute(sql_command)
            self.connection.commit()
            # except:
            #     print('failure')
            #     self.connection.rollback()
            # else:
            self.rebuild_counter(list_name)
            

#######################################
                    
    def sql_wildcard_show(self, sql_command):
        "called when showing items using the * wildcard. It returns a generator, just like get_list_items "

        res = self.cursor.execute(sql_command)
        return res

        

            

    
        
    def check_table(self, name):
        
        table_exists = None
        sql_command = "SELECT EXISTS (SELECT list_name from list_tracker WHERE list_name=='{}')".format(name)
        #sql_command = "SELECT EXISTS (SELECT * from list_tracker WHERE list_name == '{}')".format(name)
        res = self.cursor.execute(sql_command)
        table_exists = True if not len(res.fetchall()) == 0 else False

        return table_exists

    

    def create_table(self, list_name, kind):  # name is the name of the list, kind is the type of the list - rater, to-do etc
        table_exists = self.check_list(list_name)  # call table_exists() to check whether a table with that name already exists
        if table_exists == True:
            debugger_cl.c_debug_msg('A list with that name already exists. Use "pylists lists" to get a list of all the existing lists')
        elif table_exists == False:
            if kind == 'rater':
                sql_add_to_main_table = "INSERT INTO list_tracker (list_name, list_type) VALUES (?,?)"  # first, an entry for the new table needs to be created in the main table (list_tracker)

                sql_create_table = """CREATE TABLE '{n:}' ( --quoting is really important. For example, I was getting an error where n contained whitespace, even if  in quotation marks ('Twilight Zone'), but not quoted here as '{n:}' 
                               num INT NOT NULL, 
                               title TEXT PRIMARY KEY NOT NULL,  
                               rating INTEGER NOT NULL, 
                               table_name TEXT DEFAULT '{n:}',
                               FOREIGN KEY(table_name) REFERENCES list_tracker(list_name) ON UPDATE CASCADE ON DELETE CASCADE )""".format(n=list_name)

            # ON DELETE CASCADE and ON UPDATE CASCADE ensured that deletion or update actions performed on the parent table are reflected in the child table assocaited with it via the foreign key

            
            try:
                self.cursor.execute(sql_add_to_main_table, (list_name, kind))
            except:
                debugger_cl.c_debug_msg('FATAL. Exitting.')
            else:               # the purpose of the else clause here is: everything under the else only gets executed if NO exception is raised in the try block above.
                # try:
                self.cursor.execute(sql_create_table)
                self.connection.commit()
                # except:
                debugger_cl.c_debug_msg("ERROR. Table couldn't be created. Rolling back the changes")
                self.connection.rollback()
            
                

    def delete_table(self, list_name):
        #fix this. The table shouldn't be deleted like this, but using ON DELETE - in other words, the correponding row in the main  table should be deleted instead only, which would in turn trigger and take care of the deletion of the second table
        "remove a table named name"
        try:
            # sql_command = "DROP TABLE IF EXISTS {}".format(name)
            sql_delete_from_main_table = "DELETE FROM list_tracker where list_name == '{}'".format(list_name)
            sql_drop_table = "DROP TABLE IF EXISTS '{}'".format(list_name)  # initially I tried doing this with a CREATE TRIGGER, but that's not an option; you can't drop tables with triggers - only insert, delete items etc
            self.cursor.execute(sql_delete_from_main_table)
            self.cursor.execute(sql_drop_table)
            self.connection.commit()
            debugger_cl.c_debug_msg('Done.')
        except:
            debugger_cl.c_debug_msg('Couldn\'t delete the list')
            self.connection.rollback()


####
    def get_items_num(self, name):
        "find out how mnay items there are in the list NAME"
        sql_command = "SELECT COUNT(*) from '{}'".format(name)
        res = self.cursor.execute(sql_command)
        num = res.fetchone()[0]  # fetchone returns a one-item tuple ending in a comma (hence the slicing); fetchall() would return the  tuple enclosed in a list
        return num
        
####


    def get_list_items(self, list_name):
        sql_command= "SELECT num,title,rating FROM '{}' ORDER BY num ASC".format(list_name)
        res = self.cursor.execute(sql_command)
        return res
        

    def get_list_types(self):
        "get a list of the list types in the main table (rater, to-do, etc) "
        sql_command = "SELECT list_type FROM list_tracker".format()
        self.cursor.execute(sql_command)
        types = set(res.fetchall)
        self.list_types = types
        return types
    
    

#####
    
    def get_lists(self, kind=None):
        'determine, format, and print to stdout the lists specified when <<pyylists lists>> is used at the command line'
        lists = None
        res = None
        
        if not kind == None: #and kind in self.list_types:  
            debugger_cl.c_debug_msg('kind is', kind)
            sql_command="SELECT * from list_tracker WHERE list_type == '{}'".format(kind)
            res = self.cursor.execute(sql_command)
            lists = res.fetchall()

        elif kind == None:
            debugger_cl.c_debug_msg('kind is None')
            sql_command = "SELECT * from list_tracker"
            res = self.cursor.execute(sql_command)
            lists = res.fetchall()
            debugger_cl.c_debug_msg(lists, 'lists')
        debugger_cl.c_debug_msg(lists)


        if len(lists) == 0:
            print("There are NO lists. You can create one with 'pylists add -t TYPE name_of_list'")

        elif len(lists) > 0:

            final_res= {}

            list_types = set(y for x,y in lists) #list types are rater, to do etc. Duplicates need to be removed, or each type will be printed for each result, when it only has to be printed once
            debugger_cl.c_debug_msg('list types', list_types)

            for x in list_types:
                final_res[x] = []   # populate the final_res with the list types as a keys, each associated with a list to store the lists associated with a list type

            for x,y in lists:
                if y in list_types: 
                    final_res[y].append(x)

            debugger_cl.c_debug_msg('final result', final_res)




            def form_cat_title(title):
                return "*{brd:-^{lg}}*\n| {t:} lists |\n*{brd:-^{lg}}*".format(t=title, lg=len(title+'lists')+3, brd='')  # brd= border

            def form_items(item, item_num):
                return "{p:7}|{i:} -->({n:})".format(p='', i=item, n=item_num)  # p= padding


            for dict_key in final_res:     # lists is the result of a fetchall() call, which returns a lsit of tuples
               title = form_cat_title(dict_key)
               print(title)

               for item in final_res[dict_key]:
                   num = self.get_items_num(item)
                   print(form_items(item, num))     


    #########################################          

    def check_list(self, name):
        "check to see if the list NAME exists in the list_tracker table; This method is meant to be used when creating a table and similar cases, checking for its existence first. It returns a boolean value"
        sql_command = "SELECT EXISTS (SELECT * from list_tracker WHERE list_name == '{}')".format(name)
        executed = self.cursor.execute(sql_command)

        res = executed.fetchone()[0]
        debugger_cl.c_debug_msg(res, 'res')
        if res > 0:
            return True
        else:
            return False

        

    def get_max(self, column, table):
        """get the maximum value in a column -- this is meant to be called by add_item in order to determine the MAX value and increment it by one when adding a new item, so as to maintain a sequential numbering without any gaps"""
        sql_command= "SELECT MAX({}) from {}".format(column, table)
        res = None
        executed = self.cursor.execute(sql_command)

        for i in executed:
            res = i[0]

        if not res == None:
            pass
        elif res == None:
            res = 0
            
        return res

        
    def add_item(self, entries, kind=None, list_name=None):  # entries should be a list of elements to be added. This is different depending on the kind parameter (rater, todo)
        if kind == 'rater':
            debugger_cl.c_debug_msg("adding item to a list of type 'rater'")
            sql_command = "INSERT INTO {} (num, title, rating) VALUES (?, ?, ?)".format(list_name)
            try:
                self.cursor.execute(sql_command, entries)
                self.connection.commit()
                debugger_cl.c_debug_msg('executed command successfully')
            except:
                debugger_cl.c_debug_msg('failure. Rolling the changes back')
                self.connection.rollback()

        elif kind == to-do:
            #handle to-do lists elements
            pass
        else:
            debugger_cl.c_debug_msg('neither rater nor to-do')




    def delete_item(self, items_list, list_name, handle=False):
        #if many is set to True, the items_list is a list of numbers from the num column, as parsed by re_matcher()
        "delete an item from a list(table) and update the other items accordingly in order to keep the numbering of 'num' column in order and without any gaps "
        #item can either be a number -- the value of the POS column in the pylists output -- or a name.
        
        sql_command= None
        debugger_cl.c_debug_msg(items_list, 'items')


        if handle==False:         # the list should only be one-item long
            item=items_list
            get_num_value= "SELECT num from '{}' WHERE title == '{}'".format(list_name, item)
            num_value = self.cursor.execute(get_num_value)
            pos = None          # the value in the num column for this particular row. Needed in order to decrement by one all items that are > this value.
            for i in num_value:
                pos = i[0]

            debugger_cl.c_debug_msg('pos is', pos)


            sql_command = "DELETE FROM '{}' WHERE title == '{}'".format(list_name, item)

            try:
                self.cursor.execute(sql_command)
                debugger_cl.c_debug_msg('item successfully deleted')
            except:
                debugger_cl.c_debug_msg('item deletion failed')

            else:
                debugger_cl.c_debug_msg('updating all the rows after deletion')
                sql_update_rows= "UPDATE '{}' SET num=num-1 WHERE num>'{}'".format(list_name, pos)
                self.cursor.execute(sql_update_rows)
                self.connection.commit()


        elif handle == True:
            sql_command= "DELETE FROM '{}' WHERE num == ?".format(list_name)
            print('items list', items_list)
            if len(items_list) == 1:  # if only one item is deleted, proceed the same way as with --item, rather than --handle, since the additional overhead doesn't make sense for a single item being removed.
                pos = items_list.pop()
                debugger_cl.c_debug_msg('pos', pos)
                sql_update_rows= "UPDATE '{}' SET num=num-1 WHERE num>'{}'".format(list_name, pos)
                self.cursor.execute(sql_command, (pos,))
                self.cursor.execute(sql_update_rows)
                self.connection.commit()

 

            elif len(items_list) > 1:  # call 
                for item in items_list:
                    # try:
                    self.cursor.execute(sql_command, (item,))
                
                    # self.connection.commit()
                    #print('item successfully deleted')
                # except:
                    #print('item deletion failed')
                # else:
                    # try:
                    #print('updated all the rows successfully after deletion')
                    self.connection.commit()
                debugger_cl.c_debug_msg('list name', list_name)
                self.rebuild_counter(list_name)
                # except:
                    #print('sql deletion failed')
                    #self.connection.rollback()

            
                # print('deletion of multiple items at a time is only allowed using the item\'s handle - i.e. the value in the HND column in the output')
                # try:
                #     self.connection.commit()
                #     print('deletion committed')
                # except:
                #     print('deletion commit failed')





        

    def rebuild_counter(self,table):
        """when deleting items in bulk using del --handle, the sequential numbering will be blown full of holes. This function recounts renumbers the rows after the deletion is done"""          

        debugger_cl.c_debug_msg('table name', table)
        update_row="UPDATE '{}' SET num=? WHERE title==?".format(table)  # ?=the range generator

        get_item_title_com="SELECT title from '{}'".format(table)
        titles = self.cursor.execute(get_item_title_com).fetchall()


        total_items = self.get_items_num(table)
        debugger_cl.c_debug_msg('total items', total_items)
        counter = range(1,total_items+2)
        # for i in counter:
           # print('i, counter', i)

        yield_titles=(x[0] for x in titles)  # generator object generating one title at a time from the given lsit
        # for i in yield_titles:
            # print(', yield titles', i)

        yields= zip(counter, yield_titles)
        #print('printing yielder')
        #for i in yields:
            #print('yielder i', i)

        self.cursor.executemany(update_row, yields)
        self.connection.commit()
        
        # the indexing is neccessary because the items are returned as tuples, even if it's a one-item tuple
        
        
        
            # item=get_one.fetchone()[0]
            # self.cursor.execute(update_row, (counter, item))
            # counter+1
            




   

###################################################################################################################
##########################################################################################################


class re_matcher():

    def __init__(self):
        pass
    
    def _get_numlist(self, strings, ran=False):  # strings is the list of strings returned by re, under the show_items method
        "meant to be called by the show_items() method and the result passed as an arg to format_all; it determines just what items should be printed, based on the rating"
        numlist = []
        temp_list = []
        
        # match_range = re.compile(r'\d\d?-\d\d?')  #I'm cutting this out. Instead I'll put a boolean flag among the arguments that will be set from the show_all method
        try:
            if ran == True:
                for i in strings:
                    temp_list = i.split(sep='-')  # e.g. get a list of ['5','7'] from a string of '5-7'
                    numlist += list(range(int(temp_list[0]),int(temp_list[1])+1))
                    numlist = [x for x in numlist if not x ==""]  # empty strings can screw up parsing, so they need to be rid of
                    debugger_cl.c_debug_msg('numlist in get_numlist(),', numlist)

            elif ran == False:
                for i in strings:
                    temp_list = i.split(sep=',')

                    for x in temp_list:
                        try:
                            numlist.append(int(x))
                        except:
                            pass
                            # numlist += [int(x) for x in temp_list]

                    numlist = [x for x in numlist if not x == ""]

        except:
            debugger_cl.c_debug_msg('invalid input. It can only contain numbers, separated by a comma, if they\'re a list e.g. 7,123,200, or by a dash 100-170, if they form a range')
        return numlist




    
    def match_items(self, cat, items_to_format, rater=False):  # called from the main script - cat takes its value from args.rated 
        "print the items denoted by cat, which stands for the value passed using the --rated option with argparse"
        # if isinstance(cat, str):   #this is actually the wrong way to go about it; the value will ALWATS be a string. What I have to do is parse the string with regex
        # print('string')
        # print('string instance')
        if cat[0] in {';', '&', '%', '*', '!', '(', '\\', '/', '_', ']', '$', '}', '^', ')', '+', ',', '{', '#', '.', '@', '[', '~'}:    # if someone does something like --rated ---+@!# etc, which have no meaning
            print('invalid character:', cat[0])
            try:
                raise Exception('invalid input')
            except:
                print('invalid input. Illegal character found. Exitting')
                exit()
    
        elif cat[0] == 'all' or cat == 'all':  # if --rated=all is used, the result wil be a list, so indexing needs to be used. If --rated is ommitted comletely, the default will be used, which is all, and it's a string
            debugger_cl.c_debug_msg('all being used')
            debugger_cl.c_debug_msg('fine')
            numlist = None
            # print(self.format_title())
            # for i in self.format_all(items_to_format, numlist=None):
                # print(i)

                

        else:
                
            if rater==True:     # if this is supposed to match ratings, the pattern should be one and two-digit numbers max (i.e. 1-10)
                match_num = re.compile(r'\d\d?')  # match any one or two-digit number (0 -99)
                match_range = re.compile(r'\d\d?-\d\d?')  # match any one or two-digit number separated by a dash in a range

            elif rater == False:  # if matcher is dealing with something else, not 1-10 ratings - such as values in the num columns used to identify items for deletion
                match_num = re.compile(r'\d{,10}')  # this should match into the hundreds of millions
                match_range = re.compile(r'\d{,10}-\d{,10}')

           
            
            tomatch = ''.join(cat)                    # join the re match into a string e.g. '6-9', '6,7,blahblah,9-10' to use in searching the command line string for the correct patterns
            res = set()                           # this should store both the results of r_ran (after expanding the range) and r_num, ensuring they're unique.
            debugger_cl.c_debug_msg(tomatch, 'tomatch')
            r_num = match_num.findall(tomatch)  # returns a list object of all items found as a result of searching the whole string
            r_ran = match_range.findall(tomatch)  # I'm joining the results into a string, because if the --rated options returns a list of various strings, as a result of the used not passing the ranges correctly e.g. --rated 7-9, ,,,1-5 etc, it'l break things. But joining it into a single string allows re to search it start  to finish and match what it needs to
            debugger_cl.c_debug_msg(r_num,'r_num', r_ran, 'r_ran')

#evaluating the range pattern needs to come first, otherwise the number pattern will return results even if the match should be a range
#the way this is coded, you can either specify ranges or a comma separated list of values. The latter will only be considered if there's no range,
#and if there is a range, or ranges, it stops there. I need to have both r_ran and r_run executed and combine their results in a set, for uniqueness (of course, AFTER the range values are expanded i.e. from 5-8 to 5,6,7,8)
            if r_ran:         # if the list returned by the regex search isn't empty, after matching the string against r_num 
                debugger_cl.c_debug_msg('range match:', r_ran)
                numlist = self._get_numlist(r_ran, ran=True)
                
                for i in numlist:
                    res.add(i)
                    
                debugger_cl.c_debug_msg(res)
                debugger_cl.c_debug_msg(numlist, 'range numlist')

                # print(self.format_title())

                # for i in self.format_all(items_to_format, numlist=numlist):
                            # print(i)


            #r_num isn't conditioned by the execution of r_ran. BOTH are executed, and the result ultimately returned is a set consisting of the results of both r_ran (after its range results are expanded) and r_num    
            if r_num:           # if the list returned by the regex search isn't empty, after matching the string against r_num 
                debugger_cl.c_debug_msg('numbers match:', r_num)
                numlist = self._get_numlist(r_num, ran=False)

                for i in numlist:
                    res.add(i)
                debugger_cl.c_debug_msg(res)
                numlist=res

                # print(self.format_title())

                # for i in self.format_all(items_to_format,numlist=numlist):
                    # print(i)

        return (items_to_format, numlist)





########################################################################    

    def wildcard_match(self, string_to_be_matched, list_name, deletion=False, selection=False):  # this can be used either for showing or deleting items
      "use sql's built-in shell globbing like matching capabilities to match against the * wildcard when looking up or deleting items. Returns the formatted sql command to be passed to sql_execute or sql_wildcard_show "

      prep_str = string_to_be_matched.replace('*', '%')  # NOTE: sqlite supports teh GLOB keyword which allows you to use POSIX globbing, so I wouldn't really need to use LIKE and its syntax instead. But the latter does case-insensitive matching, while in the former case is sensitive. I want to do the letter, and so I'll replace * with % and use  the LIKE pattern matching feature instead. 
      if deletion:
          sql_com = "DELETE FROM '{}' WHERE title LIKE '{}'".format(list_name, prep_str)

      elif selection:
          sql_com = "SELECT num,title,rating FROM '{}' WHERE title LIKE'{}' ORDER BY num ASC".format(list_name, prep_str)

      return sql_com


 ##################################################################################################
#####################################################################################################
################################################################################################
        
        

        
class rater_cl():
    'class to manage ratings lists in the sqlite database'
    def __init__(self):
        self.kind = 'Ratings'


    def add_item(self, num, name_of_list, title, rating, callable=None):  # num is the result of returned by get_max()
       debugger_cl.c_debug_msg('received', name_of_list, title, rating)  
       #I should implement some checks here to test the argumetns in order to determine they're correct (e.g. the rating is between 1-10 etc)
       items = (num+1, title, rating)  # num is the maximum on the num column; the item to be added needs to be incremented by 1.
       debugger_cl.c_debug_msg(items, 'items')
       try:
          callable(items, kind='rater', list_name=name_of_list)  # callable should be a db_interface() instance, but should be called from the main script
          debugger_cl.c_debug_msg('calling db_interface -> successsful')
       except:
          print('calling db_interface', 'failed')
        


    def read_from_file(self, filename):
        "read entries from file, one per line, and yield them one by one. Meant to be fed to add_item"
        try:
            handle = open(filename, mode='r')
            debugger_cl.c_debug_msg('reading the files')
        except:
            print('not a file/can\'t open it')
        else:
            try:
                for i in handle.readlines():  # iterating over readline() instead of readlines() would return only one character at a time instead of one line at a time
                    title, rating = i.rstrip().split('==')
                    #if title.find("'") > 0:
                        #title = '"'+title+'"'
                        #print(title, 'title')
                    yield title, rating
            except:
                print('failed at file parsing')

    # #unlike the todo_class below, this class should match an item by either position (which will be an integer), OR name, which regex needs to be used for.

    def format_item(self, j, k, l):  # c=the number in the pos column, which corresponds to the value in the sql num column, t=title, r=rating
        "formats a single item; meant to be called by the format_all() method"
        border = "+{:-^5}+{:-^56}+{:-^7}+".format("","","")
        # return "{:>6}|{:<55} : {}".format(j, k, l)  # never forget the return. I did, and wasted precious time   #this is the previous formatting style, without border
        return "|{:^5}|{:<55} : {:<6}|\n{}".format(j,k,l,border)



    def format_title(self):
        "formats the header, before the list of items. This is meant to be called before format_all()"
        border = "+{:-^5}+{:-^56}+{:-^7}+".format("","","")
        return "{b:}\n|{p:^5}|{t:^55} : {r:^6}|\n{b:}".format(b=border,p="HND", t="TITLE", r="RATING")  # handle is the num value from the sqlite num column
    #it's intended as a handle (like in, for example, nftables - you can delete etc an item using that instead of typing out the whole name
        

    
    def format_all(self, to_format, numlist=None):
        "calls format_item for each argument-item, and adds some more formatting, such as cutting the title to size if too long"
        # self.items_rsorted = [(x,y) for (y,x) in sorted((y,x) for x,y in self.items.items())]
        # to_format = enumerate(self.items_rsorted,1)  # start counting from 1

        
        x = 55                  # this is the maximum width of the title column when printed out. If the text doesn't fit, it's truncated and an ... is appended
        for (c,t,r) in to_format:  # c=the counter - the num column ;; t = the title ; r= the rating
            if not numlist:
                #print('numlist is none')
                
                if x < len(t):
                    x = t[:52] + u' \u2026 '
                    t=x

                yield self.format_item(c,t,r)
                x=55

            elif numlist:
                #print('numlist not none')
                if r in numlist:
                    if x < len(t):
                        x = t[:52] + u' \u2026 '
                        t=x

                    yield self.format_item(c,t,r)
                    x=55
           
                
            

#make another option -p,--position that lists items by their position, not rating -- for example , listing the item with position 1-10 will lsit the first ten items in aspecified list;

    def show_items(self, items_to_format, num_list=None ):
        "print out the final product of formatted items - it calls other methods that do the actual heavy lifting of formatting the items"
        print(self.format_title())
        for i in self.format_all(items_to_format, num_list):
            print(i)

    

###########################################
                
                  

    def change_item_rating(self, item, rating_val, list_name):
        "change the rating or title of an item - the item can be specified either by its title or its handle"
        try:
            if isinstance(int(rating_val), int) and int(rating_val)<=10:
                print('valid rating value')
        except:
            print('invalid rating value')
        else:
            try:
                sql_comm = ""
                if isinstance(int(item), int):  # if the item is identified by its value in the num column
                    sql_comm = "UPDATE '{}' SET rating = '{}' WHERE num == '{}'".format(list_name, rating_val, item)
            except:
                if isinstance(item, str):  # if the item is identified by its value in the title column
                    sql_comm = "UPDATE '{}' SET rating = '{}' WHERE title == '{}'".format(list_name, rating_val, item)
                else:
                    print('invalid value')

        debugger_cl.c_debug_msg('sql comm is', sql_comm)
        return sql_comm         # meant to be fed to db_interface_execute_sql
            


    
    def change_item_title(self, item, title_val, list_name):
        if not isinstance(title_val, str):
            print('invalid title value - it needs to be a string')

        sql_com=""
        try:
            if isinstance(int(item), int):  # if the item is identified by its value in the num column
                sql_comm = "UPDATE '{}' SET title = '{}' WHERE num == '{}' ".format(list_name, title_val, item)
        except:
            if isinstance(item, str):  # if the item is identified by its value in the title column
                sql_comm = "UPDATE '{}' SET title = '{}' WHERE title == '{}' ".format(list_name, title_val, item)

        debugger_cl.c_debug_msg('sql comm is', sql_comm)
        return sql_comm         # meant to be fed to db_interface_execute_sql



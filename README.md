# pyrate
A program written in Python to keep organized lists of ratings. Underneath, it uses the sqlite3 module to store the entries in an sqlite database.


usage: 
     pyrate  {lists, add-list, del-list, add, from-file, del, show, change}
             --debugging
             -h,--help

Maintain nicely-organized ratings lists.
Each of the subcommands listed here is its own separate subcommand and each has its own help page. So, for example, to get help on the 'show' subcommand, you can do 'pyrate show --help'.

optional arguments
-h, --help            show this help message and exit
--debugging           print out debugging and internal messages

subcommands:
     {add-list,lists,del-list,add,from-file,show,del,change}




Note: 
Eacho of the subcommands have their own command line parser and set of options. Each has a separate help page. 
I.e. if you want to see the help message for the 'add-list' subcommand, you can do 'pyrate add-list --help'.

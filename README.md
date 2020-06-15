# pyrate
A program written in Python to keep organized lists of ratings. Underneath, it uses the sqlite3 module to store the entries in an sqlite database.

```
usage: 
     pyrate  {lists, add-list, del-list, add, from-file, del, show, change}
             --debugging
             -h,--help

Maintain nicely-organized ratings lists.
 Each of the subcommands listed here is its own separate subcommand and each has its own help page. 
 So, for example, to get help on the 'show' subcommand, you can do 'pyrate show --help'.

optional arguments:
  -h, --help            show this help message and exit
  --debugging           print out debugging and internal messages

subcommands:
  {add-list,lists,del-list,add,from-file,show,del,change}



```


**Some examples:** 

pyrate lists
```
*-------------*
| rater lists |
*-------------*
       |nosleep -->(47)
       |twilight_zone -->(89)
       |podcasts -->(6)
       |series -->(14)
       |Audiobooks -->(5)
```

pyrate show podcasts
```
+-----+--------------------------------------------------------+-------+
| HND |                         TITLE                          : RATING|
+-----+--------------------------------------------------------+-------+
|  1  |Hardcore History                                        : 10    |
+-----+--------------------------------------------------------+-------+
|  2  |Hardcore Game of Thrones                                : 10    |
+-----+--------------------------------------------------------+-------+
|  3  |Shit Town                                               : 8     |
+-----+--------------------------------------------------------+-------+
|  4  |We're alive                                             : 10    |
+-----+--------------------------------------------------------+-------+
|  5  |Darkest Night                                           : 9     |
+-----+--------------------------------------------------------+-------+
|  6  |A Very Fatal Murder [parody]                            : 9     |
+-----+--------------------------------------------------------+-------+

```

[{"expressions":["(set x 15)","(puts (str (subtract x 5)))"],"output":["10"]},
 {"expressions":["(puts (concat \"Hello\" \" World!\"))"],"output":["Hello World!"]},
 {"expressions":["(puts (str (equal \"10.5\" \"10\")))"],"output":["false"]},
 {"expressions":["(puts \"Not an error!\")","(puts 10)"],"output":["Not an error!","ERROR at line 2"]},
 {"expressions":["(puts (str (divide -1361.2772 7700)))","(puts (str (divide 6665.3525 0)))"],"output":["-0.1768","ERROR at line 2"]}]
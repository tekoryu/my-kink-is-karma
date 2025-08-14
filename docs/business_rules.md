[RN0001] Field 'casa_inicial' comprises the information of who initiate the 
process, so when correctly checked which house started the process, fields
'autor' and 'data_apresentacao' shall be extracted from the correct API, 
ignoring what the other API brings about it.
[RN0002] Field 'casa_inicial' can have a lot of values like Senado, Camara, Poder Executivo or other entities
legally granted the right to propose.
[RN0003] If a proposition can't be found in an API, or the proposition havent moved from one house to another yet
or the proposition do not exist.
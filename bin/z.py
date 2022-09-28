

res = '''1:
RM0 G—891076 is your Google verification code.'''
if "Google verification" in res:
    res = res.split(' ')
    for i in res : 
        
            if i.split('-') :
                i = i.split('—')
                # print(i)
                for i_part in i :
                    try:
                        if int(i_part):
                            print(i_part)
                    except Exception as e : ...
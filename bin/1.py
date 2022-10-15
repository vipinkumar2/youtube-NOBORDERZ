import requests
import urllib.parse
aa = ''' curl -X GET "https://randommer.io/api/Name?nameType=fullname&quantity=1" -H  "accept: */*" -H  "X-Api-Key: dd78b86caaae4f04a4957cb5f3730b45" '''
# headers = {
#     'accept': '*/*',
#     'X-Api-Key': 'dd78b86caaae4f04a4957cb5f3730b45'
# }
# def get_random_username():
#     url = "https://randommer.io/api/Name?nameType=fullname&quantity=1"
#     full_name = requests.post(url,headers=headers)
#     # return full_name
#     print(full_name)

# # print(get_random_username())
import subprocess

# bash_com = 'curl -X GET "https://randommer.io/api/Name?nameType=fullname&quantity=1" -H  "accept: */*" -H  "X-Api-Key: dd78b86caaae4f04a4957cb5f3730b45"'
# subprocess.Popen(bash_com)
# output = subprocess.check_output( bash_com)
# print(output)
# def run_cmd(cmd, verbose=True):
#     """Run shell commands, and return the results

#     ``cmd`` should be a string like typing it in shell.
#     """
#     try:
#         if verbose:
#             print(f'Command: {cmd}')

#         r = subprocess.run(cmd, stdout=subprocess.PIPE,
#                            stderr=subprocess.STDOUT, shell=True, text=True)

#         if verbose:
#             if r.returncode == 0:
#                 print(f'Successful to run the command: {cmd}')
#                 print(f'Result of the command: {r.stdout}')
#                 print(r.stdout,'----------------------------')
#                 return r.stdout
#             else:
#                 print(f'Failed to run the command: {cmd}')
#                 print(f'Result of the command: {r.stdout}')

#         return r.stdout
#     except Exception as e:
#         print(e)
      
# ddd = run_cmd(aa)  
# print(ddd)
# print(list(ddd))
# print(type(list(ddd)))

def fake_name():
        from faker import Faker
        fake = Faker()
        name = fake.name()
        name_li = str(name).split(' ')
        fname = name_li[0]
        lname = name_li[-1]
        print(name)
        return name,fname, lname
    
# print(fake_name())
name,fname, lname = fake_name()
name = name.split(' ')
name = name[0]+name[1]
print(name)
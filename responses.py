import json

res_dict = {
"s1" : ["success","Requested Successfully"],
"s2" : ["success","Created Successfully"],
"s3" : ["success","Updated Successfully"],
"s4" : ["success","Deleted Successfully"],
"s5" : ["success","Leave Approved"],
"s6" : ["success","Leave Rejected"],
"s7" : ["success","Reset email sent"],
"e1" : ["danger","Email & Password doesn't match"],
"e2" : ["danger","Something went wrong, please try again later"],
"e3" : ["danger","User with given email exist"],
"e4" : ["danger","Email deosn't exist"]
}

def response (code):
    return res_dict[code]
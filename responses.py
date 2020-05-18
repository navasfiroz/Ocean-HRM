import json

res_dict = {
"s1" : ["success","Requested Successfully"],
"s2" : ["success","Created Successfully"],
"s3" : ["success","Updated Successfully"],
"s4" : ["success","Deleted Successfully"],
"s5" : ["success","Leave Approved"],
"s6" : ["success","Leave Rejected"],
"e1" : ["danger","Email & Password doesn't match"]
}

def response (code):
    return res_dict[code]
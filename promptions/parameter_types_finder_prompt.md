Find the c/c++ Non-built-in Types of from the c++ code snippets:
- Only find them in the function parameter list
- Only output the types without c/c++ keywords
- Only respond with the JSON, without any explanation
##
Only respond with a JSON containing the array of the type name:
{"data": ["Non-built-in type 1", "Non-built-in type 2"]}
##
Only respond with a JSON containing empty array if find nothing:
{"data": []}
##
Some examples:
##
code snippet 1: `virtual void release(bool sync = false) = 0;`
output 1: {"data": []}
##
code snippet 2: `virtual int queryInterface(INTERFACE_ID_TYPE iid, void** inter) = 0;`
output 2: {"data": ["INTERFACE_ID_TYPE"]}
##
code snippet 3: `virtual int leaveChannel() = 0;`
output 3: {"data": []}
##
code snippet 4: `virtual const char* getVersion(int* build) = 0;`
output 4: {"data": []}

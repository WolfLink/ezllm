import inspect
import json


type_translations = {
        str : "string",
        int : "integer",
        float : "double",
        bool : "bool",
        None : "none",
        type(None) : "none",
        }
inverse_type_translations = dict()
for t in type_translations:
    inverse_type_translations[type_translations[t]] = t

def parse_docstr(docstr):
    if ":" not in docstr:
        desc = docstr
        return {"desc" : desc, "params" : {}, "return" : {}}

    main_desc = docstr.split(":")[0].strip()
    params = {}
    rval = {}
    comment_pairs = []
    
    pair = None
    for text in docstr.split(":")[1:]:
        if pair is None:
            pair = text
        else:
            comment_pairs.append((pair, text))
            pair = None

    for pair in comment_pairs:
        flags, desc = pair
        flags = list(flags.split(" "))
        if flags[0] == "param":
            param_name = flags[-1]
            param_types = list(flags[1:-1])
            params[param_name] = {
                    "desc" : desc.strip(),
                    "types" : param_types,
                    }
        elif flags[0] == "return":
            return_types = list(flags[1:])
            rval = {
                    "desc" : desc.strip(),
                    "types" : return_types,
                    }
        else:
            param_name = flags[-1]
            param_types = list(flags[:-1])
            params[param_name] = {
                    "desc" : desc.strip(),
                    "types" : param_types,
                    }
    return {"desc" : main_desc, "params" : params, "return" : rval}

class Tool:
    def __init__(self, f):
        self.f = f
        docstr_data = parse_docstr(f.__doc__)
        self.desc = docstr_data["desc"]
        self.name = f.__name__

        self.parameters = {}
        self.required = []
        sig = inspect.signature(f)
        for param in sig.parameters:
            desc = ""
            types = ""

            # get the data we can from the signature
            annotation = sig.parameters[param].annotation
            if annotation in type_translations:
                types = type_translations[annotation]

            if sig.parameters[param].default is sig.parameters[param].empty:
                self.required.append(param)

            # get the data we can't get from the signature from the docstr
            if param in docstr_data["params"]:
                paramstr = docstr_data["params"][param]
                if "desc" in paramstr:
                    desc = paramstr["desc"]
                if types == "" and "types" in paramstr:
                    types = paramstr["types"][0].strip() # TODO might want to handle multiple possible types later
            if types == "":
                types = "string"
            self.parameters[param] = {
                    "type" : types,
                    "description" : desc,
                    # TODO: support "enum" types
                    }
        if "return" in docstr_data:
            self.rval = docstr_data["return"]
        else:
            self.rval = {"desc" : "", "types" : ""}
        if sig.return_annotation is not inspect.Parameter.empty:
            rtype = sig.return_annotation
            if rtype in type_translations:
                self.rval["types"] = type_translations[rtype]


    def __call__(self, args):
        # parse kwargs and try to force it towards the expected behavior
        resp = f"Called {self.name}({args})"
        print(resp)
        #print(self.parameters)
        kwargs = dict()
        leftovers = []
        for k in self.parameters:
            if k in args:
                try:
                    kwargs[k] = inverse_type_translations[self.parameters[k]['type']](args[k])
                except ValueError as e:
                    print(f"The LLM did not call the tool correctly. Got '{e}'")
                    return f"The tool was not called correctly: {e}"
        try:
            return self.f(**kwargs)
        except TypeError as e:
            print(f"The LLM did not call the tool correctly. Got '{e}'")
            return f"The tool was not called correctly: {e}"

    def dict(self):
        return {
                "name" : self.name,
                "description" : self.desc,
                "parameters" : {
                    "properties" : self.parameters,
                    "required" : self.required,
                    },
                }


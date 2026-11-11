"""Decorator and class for easy argument conversion and validation."""

def parameterize(params:list|None=None,kwparams:dict|None=None):
    """
    Decorator function that converts the function into a callable ParamFunc object

    Format of params argument:
    {convert,[boolean functions]}
    e.g.
    {str,[lambda x:x[-4:]==".txt",lambda x:len(x)>=5]}
    Format of kwparams argument:
    {"key word":{"convert":convert,"params":[boolean functions]}}
    e.g.
    {"num1":{"convert":int,"params":[lambda x:x%3==0, lambda x:x>=0]}}
    
    convert can be any function that takes an argument and returns a converted argument (use lambda x:x if it needs to stay the same)
    boolean functions can be lambdas or any function that takes the converted argument and returns a boolean

    key word arguments with no conversion functions or parameters can be left empty
    """
    def create_param_func(func:function):
        return ParamFunc(func,params=params,kwparams=kwparams)
    return create_param_func

class ParamFunc:

    def __init__(self,func:function,params:list|None=None,kwparams:dict|None=None):
        """
        Format of params argument:
        {"convert":convert,"params":[boolean functions]}
        e.g.
        {"convert":str,"params":[lambda x:x[-4:]==".txt",lambda x:len(x)>=5]}
        Format of kwparams argument:
        {"key word":{"convert":convert,"params":[boolean functions]}}
        e.g.
        {"num1":{"convert":int,"params":[lambda x:x%3==0, lambda x:x>=0]}}
        
        convert can be any function that takes an argument and returns a converted argument (use lambda x:x if it needs to stay the same)
        boolean functions can be lambdas or any function that takes the converted argument and returns a boolean
        """
        self.func = func
        self.params = params
        self.kwparams = kwparams

    def __call__(self, *args, **kwargs):
        varnames = self.func.__code__.co_varnames[:self.func.__code__.co_argcount] # will be () if none
        def_var = self.func.__defaults__ # will be None if none 
        kw_def_var = self.func.__kwdefaults__ # will be None if none

        converted_kwargs = {}

        if kw_def_var != None:
            for kw_var in kw_def_var.items():
                converted_kwargs[kw_var[0]] = kw_var[1]

        if def_var != None:
            for var in range(-1,-1*len(def_var)-1,-1):
                converted_kwargs[varnames[var]] = def_var[var]

        if len(varnames) > 0:
            if self.kwparams != None:
                for var in range(len(args)):
                    if varnames[var] in self.kwparams.keys():
                        converted_arg = self.kwparams[varnames[var]]["convert"](args[var])
                        for param in self.kwparams[varnames[var]]["params"]:
                            assert param(converted_arg), f"arg {args[var]} doesn't satisfy parameter(s)"
                        converted_kwargs[varnames[var]] = converted_arg
                    else:
                        converted_kwargs[varnames[var]] = args[var]
            else:
                for var in range(len(args)):
                    converted_kwargs[varnames[var]] = args[var]
            args = args[len(varnames):]

        converted_args = []

        if self.params != None:
            for arg in args:
                converted_arg = self.params["convert"](arg)
                for param in self.params["params"]:
                    assert param(converted_arg), f"arg {arg} doesn't satisfy parameter(s)"
                converted_args.append(converted_arg)
        else:
            converted_args = args

        if self.kwparams != None:
            for kwarg in kwargs.items():
                if kwarg[0] in self.kwparams.keys():
                    converted_kwarg = self.kwparams[kwarg[0]]["convert"](kwarg[1])
                    for param in self.kwparams[kwarg[0]]["params"]:
                        assert param(converted_kwarg), f"arg {kwarg[1]} doesn't satisfy parameter(s)"
                    converted_kwargs[kwarg[0]] = converted_kwarg
                else:
                    converted_kwargs[kwarg[0]] = kwarg[1]
        else:
            for kwarg in kwargs.items():
                converted_kwargs[kwarg[0]] = kwarg[1]

        return self.func(*converted_args,**converted_kwargs)